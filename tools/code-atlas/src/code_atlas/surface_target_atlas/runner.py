from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

TEXT_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".css", ".scss", ".json", ".md", ".mdx", ".html",
    ".yml", ".yaml", ".txt"
}

SKIP_DIR_NAMES = {
    ".git", "node_modules", ".next", "dist", "build", "coverage",
    ".turbo", ".vercel", ".prisma", ".wrangler", "__pycache__",
    ".pytest_cache", ".cache", ".generated", "__generated__",
    "generated", "prisma-client", ".open-next", ".swc",
}

SKIP_PATH_NEEDLES = (
    "/app/.generated/",
    "/.generated/",
    "/prisma-client/",
    "/generated/prisma",
    "/node_modules/",
    "/.next/",
    "/dist/",
    "/build/",
    "/coverage/",
    "/.turbo/",
    "/.wrangler/",
)

DATA_ATTR_RE = re.compile(
    r"(data-(?:component|layer|role|part|kind|surface|screen|zone|panel|target|state|intent|slot|testid|cy))"
    r"\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|`([^`]*)`|\{([^}\n]+)\})",
    re.IGNORECASE,
)

CSS_SELECTOR_RE = re.compile(
    r"^\s*((?:\.[A-Za-z_][\w-]*|\[[^\]]+\]|#[A-Za-z_][\w-]*|:[\w-]+|[A-Za-z][\w-]*)(?:[^{;]*))\s*\{",
    re.MULTILINE,
)

EXPORT_COMPONENT_RE = re.compile(
    r"(?:export\s+)?(?:default\s+)?(?:function|const)\s+([A-Z][A-Za-z0-9_]*)",
    re.MULTILINE,
)

JSX_TAG_RE = re.compile(r"<([A-Z][A-Za-z0-9_\.]*)\b")

CLASSNAME_RE = re.compile(
    r"(?:className\s*=\s*(?:\{)?(?:styles\.)?([A-Za-z_][A-Za-z0-9_-]*)|styles\.([A-Za-z_][A-Za-z0-9_-]*))"
)

TEXT_LITERAL_RE = re.compile(r">([^<>{}\n][^<>{}\n]{2,90})<")

SURFACE_ROOTS = {
    "tablet": ("apps/terminal-de-venta-system/products/tablet", "Tablet", "tabatlas1"),
    "pc": ("apps/terminal-de-venta-system/products/pc", "PC", "pcatlas1"),
    "mobile": ("apps/terminal-de-venta-system/products/mobile", "Mobile", "mobileatlas1"),
    "web": ("apps/terminal-de-venta-system/products/web", "Web / EIT", "webatlas1"),
    "cloud-center": ("apps/terminal-de-venta-system/products/cloud-center", "Cloud Center", "cloudatlas1"),
    "control-center": ("apps/terminal-de-venta-system/products/control-center", "Control Center", "controlatlas1"),
    "chart-lab": ("apps/terminal-de-venta-system/products/chart-lab", "Chart Lab", "chartatlas1"),
}

ROUTE_LABELS = {
    "/": "Inicio",
    "/pos": "POS",
    "/checkout": "Checkout",
    "/inventory": "Inventario",
    "/inventory/low-stock": "Inventario · Bajo stock",
    "/settings/license": "Licencia",
    "/license": "Licencia",
    "/shift": "Turno",
    "/turno": "Turno",
    "/sales": "Ventas",
    "/sales/today": "Ventas de hoy",
    "/tablet-lab": "Tablet Lab",
    "/visual-os": "Visual OS",
    "/catalog": "Catálogo",
    "/catalogo": "Catálogo",
    "/stock": "Stock",
    "/existencias": "Existencias",
    "/sync": "Sync",
    "/settings": "Ajustes",
    "/customers": "Clientes",
    "/reports": "Reportes",
}

STRONG_COMPONENT_WORDS = {
    "button", "btn", "cta", "card", "panel", "rail", "drawer", "modal", "sheet",
    "badge", "pill", "chip", "price", "precio", "total", "amount", "table",
    "row", "grid", "header", "nav", "input", "field", "select", "form",
    "icon", "background", "canvas", "glass", "preview", "banner", "checkout",
    "license", "renew", "renovar", "inventory", "status", "footer",
}

KIND_NEEDLES = {
    "button": {"button", "btn", "cta", "submit", "renew", "renovar", "ghost"},
    "price": {"price", "precio", "total", "amount", "currency", "monto", "number"},
    "badge": {"badge", "pill", "chip", "status", "estado"},
    "table": {"table", "tabla", "row", "cell"},
    "background": {"background", "bg", "fondo", "surface", "canvas", "shell", "backdrop"},
    "panel": {"panel", "card", "rail", "drawer", "modal", "sheet", "pane", "capsule"},
    "text": {"title", "label", "copy", "text", "description", "titulo", "texto", "heading"},
    "field": {"input", "field", "form", "select", "campo", "textarea"},
    "icon": {"icon", "svg", "glyph"},
    "layout": {"layout", "stack", "column", "row", "zone", "section", "grid"},
    "effect": {"glass", "liquid", "shadow", "blur", "effect", "material", "glow"},
}


def _notify(notify: Callable[[str, str], None] | None, status: str, detail: str = "") -> None:
    if notify is not None:
        notify(status, detail)
    else:
        print(f"{status} {detail}".rstrip(), flush=True)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def find_repo_root(selected_path: str | Path) -> Path:
    start = Path(selected_path).expanduser().resolve()
    if start.is_file():
        start = start.parent
    for p in [start] + list(start.parents):
        if (p / "apps" / "terminal-de-venta-system").exists():
            return p
    default = Path(r"F:\repos\hitech-os")
    return default.resolve() if default.exists() else start


def rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        return str(path)


def sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def read_text(path: Path, max_bytes: int = 3_000_000) -> str:
    try:
        if path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", errors="replace")


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


def run_cmd(args: list[str], cwd: Path | None = None, timeout: int = 25) -> dict[str, Any]:
    try:
        p = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            shell=False,
        )
        return {"args": args, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as e:
        return {"args": args, "returncode": -999, "stdout": "", "stderr": repr(e)}


def path_key(path: Path) -> str:
    return str(path).replace("\\", "/").lower()


def is_generated_or_mechanical(path: Path) -> bool:
    p = path_key(path)
    name = path.name.lower()
    if any(needle in p for needle in SKIP_PATH_NEEDLES):
        return True
    if any(part.lower() in SKIP_DIR_NAMES for part in path.parts):
        return True
    if "prisma-client" in p:
        return True
    # Exclude mechanical generated artifacts such as *.generated.css without
    # treating legitimate hand-written docs as generated merely because they mention the word.
    if ".generated." in name or name.endswith(".generated.css") or name.endswith(".generated.ts") or name.endswith(".generated.tsx"):
        return True
    return False


def should_skip(path: Path) -> bool:
    return is_generated_or_mechanical(path)


def iter_scan_files(roots: list[Path]) -> tuple[list[Path], list[dict[str, Any]]]:
    files: list[Path] = []
    skipped: list[dict[str, Any]] = []
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else root.rglob("*")
        for p in candidates:
            if not p.is_file():
                continue
            if is_generated_or_mechanical(p):
                skipped.append({"path": str(p), "reason": "generated_or_mechanical"})
                continue
            if p.suffix.lower() not in TEXT_EXTS:
                continue
            key = str(p.resolve()).lower()
            if key not in seen:
                seen.add(key)
                files.append(p)
    return sorted(files, key=lambda x: str(x).lower()), skipped


def line_no(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def snippet_at(text: str, index: int, width: int = 220) -> str:
    start, end = max(0, index - width // 2), min(len(text), index + width // 2)
    return " ".join(text[start:end].split())


def normalize_id(raw: Any, fallback: str = "unknown") -> str:
    s = str(raw or "").strip() or fallback
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()
    return s or fallback



TOKEN_TERMS = [
    "checkout", "product", "status", "badge", "catalog", "drawer", "light", "safe", "shell", "layout",
    "license", "licensing", "setup", "renew", "button", "inventory", "stock", "sales", "today", "shift", "turno",
    "visual", "pulse", "prisma", "tablet", "mobile", "admin", "recipe", "gallery", "preview", "banner", "panel",
    "card", "rail", "grid", "header", "footer", "nav", "total", "number", "price", "amount", "sync", "outbox",
    "customer", "cashier", "payment", "tender", "receipt", "settings", "config", "modal", "sheet",
    "table", "row", "cell", "field", "input", "icon", "glass", "effect", "canvas", "surface", "zone", "target",
    "component", "container", "summary", "actions", "state", "disabled", "ghost", "touch", "low", "high", "empty",
]
TOKEN_TERMS = sorted(set(TOKEN_TERMS), key=len, reverse=True)
ACRONYMS = {"pos", "ui", "ux", "api", "sku", "qr", "cta", "db", "id", "url", "css", "jsx", "tsx", "dom", "json", "md", "d1"}

def _segment_known_terms(raw: Any) -> list[str]:
    text = str(raw or "").strip()
    if not text:
        return []
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    text = re.sub(r"[^A-Za-z0-9]+", " ", text)
    out: list[str] = []
    for piece in [p for p in text.split() if p]:
        low = piece.lower()
        if len(low) <= 4 or low.isdigit() or low in ACRONYMS:
            out.append(low)
            continue
        i = 0
        segmented: list[str] = []
        while i < len(low):
            match = None
            for term in TOKEN_TERMS:
                if low.startswith(term, i):
                    match = term
                    break
            if match:
                segmented.append(match)
                i += len(match)
            else:
                j = i + 1
                while j < len(low) and not any(low.startswith(term, j) for term in TOKEN_TERMS):
                    j += 1
                segmented.append(low[i:j])
                i = j
        if len(segmented) > 1:
            out.extend(segmented)
        else:
            out.append(low)
    return [x for x in out if x]


def _display_token(token: str) -> str:
    low = str(token or "").lower()
    if not low:
        return ""
    if low in ACRONYMS:
        return low.upper()
    if re.fullmatch(r"tabctl\d+", low):
        return low.upper()
    return low[:1].upper() + low[1:]


def titleize(raw: Any) -> str:
    tokens = _segment_known_terms(raw)
    if not tokens:
        return "Unknown"
    return " ".join(_display_token(t) for t in tokens) or "Unknown"


def split_tokens(*values: Any) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        tokens.update(_segment_known_terms(value))
    return {t.lower() for t in tokens if t}

def route_from_page(page: Path, repo_root: Path) -> str:
    relp = rel(repo_root, page).replace("\\", "/")
    marker = "/app/app/"
    sub = relp.split(marker, 1)[1] if marker in relp else page.name
    route_parts = [
        p for p in sub.split("/")[:-1]
        if not (p.startswith("(") and p.endswith(")")) and p not in {"index", "app"}
    ]
    return "/" + "/".join(route_parts) if route_parts else "/"


def route_to_screen(route: str) -> dict[str, Any]:
    label = ROUTE_LABELS.get(route)
    if not label:
        first = "/" + route.strip("/").split("/", 1)[0] if route.strip("/") else "/"
        label = ROUTE_LABELS.get(first) or titleize(route.strip("/") or "root")
    screen_id = normalize_id(route.strip("/") or "root")
    return {"screenId": screen_id, "screenLabel": label, "route": route}



def infer_screen(path: Path, repo_root: Path) -> dict[str, Any]:
    r = rel(repo_root, path).lower().replace("\\", "/")
    name = path.name.lower()
    stem = path.stem.lower()
    signal = " ".join(_segment_known_terms(r + " " + name + " " + stem))

    if path.name == "page.tsx" and "/app/" in r:
        return route_to_screen(route_from_page(path, repo_root))

    route_patterns = [
        ("/tablet-lab/", "/tablet-lab"),
        ("/settings/license", "/settings/license"),
        ("/license", "/settings/license"),
        ("/licensing", "/settings/license"),
        ("/inventory/low-stock", "/inventory/low-stock"),
        ("/low-stock", "/inventory/low-stock"),
        ("/inventory", "/inventory"),
        ("/checkout", "/checkout"),
        ("/pos", "/pos"),
        ("/shift", "/shift"),
        ("/turno", "/shift"),
        ("/sales/today", "/sales/today"),
        ("/sales", "/sales"),
        ("/ventas", "/sales"),
        ("/visual-os", "/visual-os"),
        ("/visual", "/visual-os"),
        ("/prisma-pulse", "/visual-os"),
        ("/tablet-visual-v2", "/visual-os"),
        ("/catalog", "/catalog"),
        ("/catalogo", "/catalog"),
        ("/stock", "/stock"),
        ("/existencias", "/existencias"),
        ("/sync", "/sync"),
        ("/settings", "/settings"),
    ]
    for needle, route in route_patterns:
        if needle in r:
            return route_to_screen(route)

    semantic_patterns = [
        (("tablet lab", "recipe", "studio", "capsule"), "/tablet-lab"),
        (("license", "licensing", "renew", "activation", "setup"), "/settings/license"),
        (("low stock",), "/inventory/low-stock"),
        (("inventory", "inventario"), "/inventory"),
        (("stock", "existencias"), "/stock"),
        (("checkout", "cart", "carrito", "payment", "tender", "total"), "/checkout"),
        (("pos", "cashier", "cash", "product grid"), "/pos"),
        (("catalog", "catalogo", "product drawer", "product status"), "/catalog"),
        (("shift", "turno"), "/shift"),
        (("sales", "ventas", "receipt"), "/sales"),
        (("sync", "outbox", "checkpoint"), "/sync"),
        (("visual", "pulse", "prisma pulse", "tablet visual"), "/visual-os"),
        (("settings", "config"), "/settings"),
    ]
    for needles, route in semantic_patterns:
        if any(n in signal or n in r for n in needles):
            return route_to_screen(route)

    if "/products/tablet/" in r:
        return {"screenId": "shared_tablet", "screenLabel": "Shared Tablet", "route": None}
    if "/tools/code-atlas/" in r:
        return {"screenId": "code_atlas_tooling", "screenLabel": "Code Atlas Tooling", "route": None}
    return {"screenId": "unknown_screen", "screenLabel": "Unknown Screen", "route": None}

def source_tier(path: Path) -> str:
    suffix = path.suffix.lower()
    p = path_key(path)
    if suffix in {".tsx", ".jsx"}:
        return "runtime_jsx"
    if suffix in {".ts", ".js", ".mjs", ".cjs"}:
        return "runtime_logic"
    if suffix in {".css", ".scss"}:
        return "style_css"
    if suffix == ".json":
        if any(name in p for name in ("tabctl", "matrix", "model", "recipe", "registry")):
            return "model_json"
        return "data_json"
    if suffix in {".md", ".mdx"}:
        return "spec_support"
    return "support"


def infer_kind(value: str, fallback: str = "") -> str:
    tokens = split_tokens(value, fallback)
    for kind, needles in KIND_NEEDLES.items():
        if tokens & needles:
            if kind == "table" and "tablet" in tokens and not (tokens & {"table", "tabla", "row", "cell"}):
                continue
            return kind
    compact = " ".join(tokens)
    if "checkout" in tokens and ("total" in tokens or "price" in tokens):
        return "price"
    if "checkout" in tokens and ("rail" in tokens or "panel" in tokens):
        return "panel"
    return "unknown"


def infer_intent(kind: str, raw: str) -> str:
    tokens = split_tokens(raw)
    if "total" in tokens or kind == "price":
        return "commercial_value"
    if {"cta", "renew", "renovar"} & tokens:
        return "primary_action"
    if "disabled" in tokens:
        return "disabled_state"
    if {"audit", "auditoria", "table", "tabla"} & tokens:
        return "auditability"
    if {"glass", "effect", "liquid"} & tokens:
        return "visual_effect"
    if kind == "text":
        return "readability"
    return kind if kind != "unknown" else "unknown"


def editable_properties(kind: str, confidence: str) -> list[str]:
    table = {
        "button": ["Texto", "Color", "Tamaño", "Tipografía", "Forma", "Material", "Estado", "Efecto", "Accesibilidad"],
        "price": ["Número/precio", "Color", "Tamaño", "Tipografía", "Contraste", "Estado", "Accesibilidad"],
        "badge": ["Texto", "Color", "Tamaño", "Forma", "Estado", "Accesibilidad"],
        "table": ["Tabla", "Tipografía", "Espaciado", "Color", "Estado", "Accesibilidad"],
        "background": ["Fondo", "Color", "Material", "Efecto", "Layout"],
        "panel": ["Color", "Tamaño", "Forma", "Material", "Efecto", "Layout", "Accesibilidad"],
        "text": ["Texto", "Color", "Tamaño", "Tipografía", "Estado", "Accesibilidad"],
        "field": ["Texto", "Color", "Tamaño", "Tipografía", "Forma", "Estado", "Accesibilidad"],
        "icon": ["Color", "Tamaño", "Estado", "Accesibilidad"],
        "layout": ["Layout", "Espaciado", "Tamaño", "Accesibilidad"],
        "effect": ["Material", "Efecto", "Fondo", "Estado"],
    }
    props = table.get(kind, ["Pendiente de clasificar"])
    return (["Pendiente de confirmar"] if confidence == "low" else []) + props


def recipe_families(kind: str, intent: str, raw: str = "") -> list[str]:
    tokens = split_tokens(kind, intent, raw)
    families: list[str] = []
    if kind == "price" or "total" in tokens:
        families += ["Total protagonista", "Auditoría tabular", "Alto contraste", "Precio discreto"]
    if kind == "button":
        families += ["CTA más fuerte", "Ghost limpio", "Disabled explicado", "Touch grande"]
    if kind == "badge":
        families += ["Estado legible", "Alto contraste", "Pill limpio"]
    if kind == "table":
        families += ["Auditoría tabular", "Densidad legible", "Alto contraste"]
    if kind == "panel":
        families += ["Panel claro", "Liquid glass suave", "Menos contenedores", "Alto contraste"]
    if kind == "background":
        families += ["Fondo transparente controlado", "Material limpio", "Alto contraste"]
    if kind == "text":
        families += ["Jerarquía tipográfica", "Lectura suave", "Alto contraste"]
    if kind == "field":
        families += ["Campo táctil claro", "Estado explicado", "Alto contraste"]
    return sorted(set(families or ["Pendiente de clasificar"]))


def has_strong_component_signal(name: str, file: str) -> bool:
    tokens = split_tokens(name, file)
    if "tablet" in tokens and len(tokens & STRONG_COMPONENT_WORDS) == 0:
        return False
    return bool(tokens & STRONG_COMPONENT_WORDS)


def has_css_target_signal(selector: str) -> bool:
    # CSS is evidence for styling and selectors, not runtime editability by itself.
    # Only target-specific data selectors are promoted as styling candidates.
    # Global theme selectors such as data-prisma-surface="tablet-pos" must not
    # inflate editable targets or confuse tablet with table.
    low = selector.lower()
    target_data_attrs = (
        "[data-role", "[data-part", "[data-kind", "[data-target",
        "[data-component", "[data-zone", "[data-panel",
    )
    if any(marker in low for marker in target_data_attrs):
        return True
    tokens = split_tokens(selector)
    if "tablet" in tokens and not (tokens & (STRONG_COMPONENT_WORDS | {"table", "tabla", "row", "cell"})):
        return False
    return bool(tokens & STRONG_COMPONENT_WORDS)


def scan_file(path: Path, repo_root: Path, surface_label: str) -> dict[str, Any]:
    text = read_text(path)
    screen = infer_screen(path, repo_root)
    tier = source_tier(path)

    data_attrs = []
    for m in DATA_ATTR_RE.finditer(text):
        expr = m.group(5)
        value = next((g for g in m.groups()[1:] if g is not None), "")
        data_attrs.append({
            "attribute": m.group(1),
            "value": value.strip(),
            "isExpression": bool(expr),
            "line": line_no(text, m.start()),
            "snippet": snippet_at(text, m.start()),
            "sourceTier": tier,
        })

    css_selectors = []
    if path.suffix.lower() in {".css", ".scss"}:
        for m in CSS_SELECTOR_RE.finditer(text):
            selector = " ".join(m.group(1).split())
            css_selectors.append({
                "selector": selector,
                "line": line_no(text, m.start()),
                "snippet": snippet_at(text, m.start()),
                "targetSignal": has_css_target_signal(selector),
            })

    components = []
    if path.suffix.lower() in {".tsx", ".ts", ".jsx", ".js"}:
        for m in EXPORT_COMPONENT_RE.finditer(text):
            components.append({
                "name": m.group(1),
                "line": line_no(text, m.start()),
                "targetSignal": has_strong_component_signal(m.group(1), rel(repo_root, path)),
            })

    jsx_tags = []
    if path.suffix.lower() in {".tsx", ".jsx"}:
        for m in JSX_TAG_RE.finditer(text):
            jsx_tags.append({"name": m.group(1), "line": line_no(text, m.start())})

    class_names = []
    if path.suffix.lower() in {".tsx", ".jsx", ".ts", ".js"}:
        for m in CLASSNAME_RE.finditer(text):
            class_names.append({"className": m.group(1) or m.group(2), "line": line_no(text, m.start())})

    text_literals = []
    if path.suffix.lower() in {".tsx", ".jsx"}:
        for m in TEXT_LITERAL_RE.finditer(text):
            lit = " ".join(m.group(1).split())
            if len(lit) >= 3 and not lit.startswith("&"):
                text_literals.append({"text": lit, "line": line_no(text, m.start())})

    return {
        "file": rel(repo_root, path),
        "surface": surface_label,
        "suffix": path.suffix.lower(),
        "sourceTier": tier,
        "sizeBytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path),
        "screen": screen,
        "dataAttributes": data_attrs,
        "cssSelectors": css_selectors[:1200],
        "components": components[:400],
        "jsxTags": jsx_tags[:600],
        "classNames": class_names[:700],
        "textLiterals": text_literals[:400],
    }


def build_route_map(repo_root: Path, surface_roots: list[Path], surface_label: str) -> list[dict[str, Any]]:
    routes = []
    seen = set()
    for root in surface_roots:
        if not root.exists() or root.is_file():
            continue
        for page in sorted(root.rglob("page.tsx")):
            if should_skip(page):
                continue
            route = route_from_page(page, repo_root)
            if route in seen:
                continue
            seen.add(route)
            screen = route_to_screen(route)
            routes.append({
                "surface": surface_label,
                "route": route,
                "screenId": screen["screenId"],
                "screenLabel": screen["screenLabel"],
                "file": rel(repo_root, page),
                "sha256": sha256_file(page),
                "confidence": "high",
                "source": "page.tsx",
            })
    return sorted(routes, key=lambda x: x["route"])


def data_target_status(scan: dict[str, Any], attr_map: dict[str, str], attrs: list[dict[str, Any]]) -> tuple[str, str, str]:
    tier = scan["sourceTier"]
    has_core = any(k in attr_map for k in ["data-role", "data-kind", "data-component", "data-part", "data-target"])
    has_expr = any(a.get("isExpression") for a in attrs)

    if tier == "runtime_jsx" and has_core and not has_expr:
        return "confirmed_runtime_data_attribute", "high", "data-attribute-runtime"
    if tier in {"runtime_jsx", "runtime_logic"} and has_core:
        return "inferred_dynamic_data_attribute", "medium", "data-attribute-runtime-dynamic"
    if tier == "style_css" and "[data-" in " ".join(a.get("snippet") or "" for a in attrs).lower():
        return "styling_candidate_data_selector", "medium", "css-data-selector"
    if tier in {"spec_support", "model_json", "data_json"}:
        return "support_only_reference", "low", tier
    return "inferred_data_attribute", "low", tier


def make_target(
    *,
    surface: str,
    screen: dict[str, Any],
    file: str,
    line: int,
    zone: str,
    panel: str,
    target_id: str,
    component: str | None,
    selector: str | None,
    data: dict[str, Any],
    kind: str,
    intent: str,
    confidence: str,
    status: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "surface": surface,
        "screenId": screen["screenId"],
        "screenLabel": screen["screenLabel"],
        "route": screen["route"],
        "zoneId": normalize_id(zone, "unknown_zone"),
        "zoneLabel": titleize(zone),
        "panelId": normalize_id(panel, "unknown_panel"),
        "panelLabel": titleize(panel),
        "targetId": normalize_id(target_id, f"line_{line}"),
        "targetLabel": titleize(target_id),
        "component": component,
        "file": file,
        "line": line,
        "selector": selector,
        "data-component": data.get("data-component"),
        "data-layer": data.get("data-layer"),
        "data-role": data.get("data-role"),
        "data-part": data.get("data-part"),
        "data-kind": data.get("data-kind"),
        "kind": kind,
        "inferredIntent": intent,
        "editableProperties": editable_properties(kind, confidence),
        "compatibleRecipeFamilies": recipe_families(kind, intent, " ".join(str(v) for v in data.values())),
        "confidence": confidence,
        "status": status,
        "evidence": evidence,
    }


def dedupe_targets(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {
        "confirmed_runtime_data_attribute": 0,
        "inferred_dynamic_data_attribute": 1,
        "styling_candidate_data_selector": 2,
        "inferred_from_component_name": 3,
        "inferred_from_css_selector": 4,
        "support_only_reference": 5,
    }
    best: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for t in targets:
        key = (t["surface"], t["screenId"], t["file"], str(t.get("line")), t["targetId"])
        current = best.get(key)
        if current is None or order.get(t["status"], 99) < order.get(current["status"], 99):
            best[key] = t
    return sorted(best.values(), key=lambda t: (t["screenId"], t["file"], t["line"], t["targetId"]))


def build_maps(scans: list[dict[str, Any]], route_map: list[dict[str, Any]], skipped_files: list[dict[str, Any]]) -> dict[str, Any]:
    data_attribute_map: list[dict[str, Any]] = []
    css_selector_map: list[dict[str, Any]] = []
    component_panel_map: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []
    low_confidence: list[dict[str, Any]] = []
    support_references: list[dict[str, Any]] = []
    css_styling_candidates: list[dict[str, Any]] = []
    unmapped: list[dict[str, Any]] = []

    for scan in scans:
        file, screen, surface = scan["file"], scan["screen"], scan["surface"]
        by_line: dict[int, list[dict[str, Any]]] = {}
        for attr in scan["dataAttributes"]:
            by_line.setdefault(attr["line"], []).append(attr)

        for line, attrs in by_line.items():
            attr_map = {a["attribute"].lower(): a["value"] for a in attrs}
            raw = " ".join(f"{k}={v}" for k, v in attr_map.items())
            status, confidence, source = data_target_status(scan, attr_map, attrs)
            kind = attr_map.get("data-kind") or infer_kind(raw, file)
            intent = attr_map.get("data-intent") or infer_intent(kind, raw)
            role = attr_map.get("data-role")
            part = attr_map.get("data-part")
            layer = attr_map.get("data-layer")
            component = attr_map.get("data-component")
            zone = attr_map.get("data-zone") or layer or role or screen["screenId"]
            panel = attr_map.get("data-panel") or component or part or role or zone
            target_id = attr_map.get("data-target") or part or role or component or f"line_{line}"
            target = make_target(
                surface=surface,
                screen=screen,
                file=file,
                line=line,
                zone=zone,
                panel=panel,
                target_id=target_id,
                component=component,
                selector=None,
                data=attr_map,
                kind=kind,
                intent=intent,
                confidence=confidence,
                status=status,
                evidence={
                    "source": source,
                    "sourceTier": scan["sourceTier"],
                    "attributes": attr_map,
                    "snippet": attrs[0].get("snippet"),
                },
            )
            if status == "support_only_reference":
                support_references.append(target)
            else:
                targets.append(target)
                if confidence == "low":
                    low_confidence.append(target)

        for attr in scan["dataAttributes"]:
            map_row = {
                "surface": surface,
                "file": file,
                "line": attr["line"],
                "attribute": attr["attribute"],
                "value": attr["value"],
                "isExpression": attr.get("isExpression", False),
                "sourceTier": scan["sourceTier"],
                "screen": screen,
                "evidence": attr.get("snippet"),
                "runtimeProof": scan["sourceTier"] == "runtime_jsx",
            }
            data_attribute_map.append(map_row)

        for c in scan["components"]:
            raw = c["name"]
            kind = infer_kind(raw, file)
            confidence = "medium" if c.get("targetSignal") and scan["sourceTier"] == "runtime_jsx" else "low"
            component_panel_map.append({
                "surface": surface,
                "file": file,
                "line": c["line"],
                "component": raw,
                "screen": screen,
                "inferredKind": kind,
                "targetSignal": c.get("targetSignal", False),
                "sourceTier": scan["sourceTier"],
                "confidence": confidence,
            })
            if c.get("targetSignal") and scan["sourceTier"] == "runtime_jsx":
                intent = infer_intent(kind, raw)
                target = make_target(
                    surface=surface,
                    screen=screen,
                    file=file,
                    line=c["line"],
                    zone=screen["screenId"],
                    panel=raw,
                    target_id=raw,
                    component=raw,
                    selector=None,
                    data={},
                    kind=kind,
                    intent=intent,
                    confidence="medium" if kind != "unknown" else "low",
                    status="inferred_from_component_name",
                    evidence={"source": "component-name", "component": raw, "sourceTier": scan["sourceTier"]},
                )
                targets.append(target)
                if target["confidence"] == "low":
                    low_confidence.append(target)

        for s in scan["cssSelectors"]:
            selector = s["selector"]
            kind = infer_kind(selector, file)
            css_row = {
                "surface": surface,
                "file": file,
                "line": s["line"],
                "selector": selector,
                "screen": screen,
                "kind": kind,
                "targetSignal": s.get("targetSignal", False),
                "confidence": "medium" if "[data-" in selector.lower() else "low",
            }
            css_selector_map.append(css_row)
            if s.get("targetSignal"):
                intent = infer_intent(kind, selector)
                target = make_target(
                    surface=surface,
                    screen=screen,
                    file=file,
                    line=s["line"],
                    zone="css_styling_candidate",
                    panel=selector,
                    target_id=selector,
                    component=None,
                    selector=selector,
                    data={},
                    kind=kind,
                    intent=intent,
                    confidence="medium" if "[data-" in selector.lower() else "low",
                    status="styling_candidate_data_selector" if "[data-" in selector.lower() else "inferred_from_css_selector",
                    evidence={"source": "css-selector", "selector": selector, "snippet": s.get("snippet")},
                )
                css_styling_candidates.append(target)
                # CSS selectors stay in CSS_SELECTOR_MAP / cssStylingCandidates.
                # They do not become editable targets until runtime JSX data-* evidence exists.
                if target["confidence"] == "low":
                    low_confidence.append(target)

        if not scan["dataAttributes"] and not scan["components"] and not scan["cssSelectors"]:
            unmapped.append({
                "file": file,
                "reason": "No data attributes, exported components, or CSS selectors detected.",
                "screen": screen,
                "sourceTier": scan["sourceTier"],
            })

    targets = dedupe_targets(targets)
    low_confidence = [t for t in targets if t["confidence"] == "low"]
    recipe_compatibility = [
        {
            "surface": t["surface"],
            "screenId": t["screenId"],
            "route": t["route"],
            "targetId": t["targetId"],
            "targetLabel": t["targetLabel"],
            "kind": t["kind"],
            "inferredIntent": t["inferredIntent"],
            "compatibleRecipeFamilies": t["compatibleRecipeFamilies"],
            "confidence": t["confidence"],
            "sourceStatus": t["status"],
        }
        for t in targets
    ]
    return {
        "targets": targets,
        "lowConfidence": low_confidence,
        "unmapped": unmapped,
        "supportReferences": support_references,
        "cssStylingCandidates": css_styling_candidates,
        "dataAttributeMap": data_attribute_map,
        "cssSelectorMap": css_selector_map,
        "componentPanelMap": component_panel_map,
        "recipeCompatibility": recipe_compatibility,
        "routeMap": route_map,
        "skippedFiles": skipped_files,
    }


CONTROL_GRAPH_SCHEMA = "PRISMA_CONTROL_GRAPH.v1"
READINESS_LEVELS = {
    "READY_FOR_VISUAL_RECIPE": 0,
    "READY_FOR_TEXT_ONLY": 1,
    "READY_FOR_INSTRUMENTATION_ONLY": 2,
    "BLOCKED_MISSING_RUNTIME_EVIDENCE": 3,
    "BLOCKED_SHARED_SELECTOR": 4,
    "BLOCKED_BUSINESS_LOGIC": 5,
    "BLOCKED_LOW_CONFIDENCE": 6,
}


def stable_control_id(*parts: Any) -> str:
    clean = [normalize_id(p, "unknown") for p in parts if str(p or "").strip()]
    return ".".join(clean) or "unknown"


def target_control_id(target: dict[str, Any]) -> str:
    return stable_control_id(
        target.get("surface"),
        target.get("screenId"),
        target.get("zoneId"),
        target.get("panelId"),
        target.get("targetId"),
    )


def semantic_role(target: dict[str, Any]) -> str:
    tokens = split_tokens(
        target.get("targetId"), target.get("targetLabel"), target.get("kind"),
        target.get("data-role"), target.get("inferredIntent"), target.get("panelId"),
    )
    if "total" in tokens and target.get("kind") == "price":
        return "primary_total"
    if target.get("kind") == "button" and ({"cta", "renew", "renovar", "submit"} & tokens):
        return "primary_action"
    if target.get("kind") == "badge" or "status" in tokens:
        return "state_indicator"
    if target.get("kind") == "table" or "audit" in tokens:
        return "audit_surface"
    if target.get("kind") == "background":
        return "visual_backplane"
    if target.get("kind") == "panel":
        return "content_container"
    return target.get("inferredIntent") or target.get("kind") or "unknown"


def missing_runtime_marks(target: dict[str, Any]) -> list[str]:
    missing = []
    required_pairs = [
        ("data-surface", target.get("surface")),
        ("data-screen", target.get("screenId")),
        ("data-zone", target.get("zoneId")),
        ("data-panel", target.get("panelId")),
        ("data-target", target.get("targetId")),
        ("data-kind", target.get("kind")),
        ("data-role", target.get("data-role") or semantic_role(target)),
    ]
    evidence = target.get("evidence") or {}
    attrs = evidence.get("attributes") if isinstance(evidence, dict) else None
    attrs = attrs if isinstance(attrs, dict) else {}
    for key, value in required_pairs:
        if not value or str(value).startswith("unknown") or key not in attrs:
            missing.append(key)
    return sorted(set(missing))



def classify_readiness(target: dict[str, Any], blast_radius: dict[str, Any] | None = None) -> dict[str, Any]:
    status = target.get("status") or "unknown"
    confidence = target.get("confidence") or "low"
    kind = target.get("kind") or "unknown"
    missing = missing_runtime_marks(target)
    shared_files = 0
    if blast_radius:
        shared_files = len(blast_radius.get("sameComponentOrSelector", []))

    allowed_visual_kinds = {"button", "price", "badge", "panel", "background", "text", "field", "icon", "table", "layout", "effect"}

    if confidence == "low":
        code = "BLOCKED_LOW_CONFIDENCE"
        reason = "Evidencia baja. Sólo inventario, no edición."
    elif missing:
        # Hard gate: visual recipes need complete runtime semantic marks. A target with
        # partial data-* may be a great candidate, but it is instrumentation-only until
        # data-surface/screen/zone/panel/target/kind/role are all present.
        code = "READY_FOR_INSTRUMENTATION_ONLY"
        reason = "Faltan marcas semánticas runtime; siguiente paso seguro es instrumentación-only, no receta visual."
    elif status == "confirmed_runtime_data_attribute" and confidence == "high":
        if shared_files > 8:
            code = "BLOCKED_SHARED_SELECTOR"
            reason = "Target confirmado, pero el blast radius parece amplio y requiere revisión antes de receta visual."
        elif kind in allowed_visual_kinds:
            code = "READY_FOR_VISUAL_RECIPE"
            reason = "Tiene evidencia runtime data-* completa para receta visual controlada."
        else:
            code = "READY_FOR_TEXT_ONLY"
            reason = "Confirmado en runtime y sin marcas faltantes, pero kind no está suficientemente clasificado para receta visual completa."
    elif status in {"inferred_dynamic_data_attribute", "styling_candidate_data_selector", "inferred_from_component_name", "inferred_data_attribute"}:
        code = "READY_FOR_INSTRUMENTATION_ONLY"
        reason = "Candidato útil, pero necesita marcas runtime completas antes de edición visual."
    else:
        code = "BLOCKED_MISSING_RUNTIME_EVIDENCE"
        reason = "Falta evidencia runtime suficiente."

    return {
        "code": code,
        "rank": READINESS_LEVELS.get(code, 99),
        "reason": reason,
        "missingRuntimeMarks": missing,
        "editableNow": code in {"READY_FOR_VISUAL_RECIPE", "READY_FOR_TEXT_ONLY"},
        "visualRecipeAllowed": code == "READY_FOR_VISUAL_RECIPE",
        "instrumentationOnlyRecommended": code == "READY_FOR_INSTRUMENTATION_ONLY" or bool(missing),
    }

def property_gate(kind: str, prop: str, readiness_code: str) -> dict[str, Any]:
    p = normalize_id(prop)
    allowed_visual = readiness_code == "READY_FOR_VISUAL_RECIPE"
    allowed_text = readiness_code in {"READY_FOR_VISUAL_RECIPE", "READY_FOR_TEXT_ONLY"}
    business_block = {"numero_precio", "number_price", "tabla", "table"}
    if p in business_block and kind in {"price", "table"}:
        return {
            "property": prop,
            "allowed": False,
            "mode": "business_logic_blocked",
            "reason": "Valor/datos de negocio no se cambian desde atlas visual. Sólo presentación cuando exista target confirmado.",
        }
    if p in {"texto", "text"}:
        return {
            "property": prop,
            "allowed": allowed_text,
            "mode": "text_or_label" if allowed_text else "blocked_until_runtime_marks",
            "reason": "Texto editable sólo con target confirmado o contrato text-only.",
        }
    return {
        "property": prop,
        "allowed": allowed_visual,
        "mode": "visual_recipe" if allowed_visual else "blocked_until_runtime_marks",
        "reason": "Propiedad visual requiere target runtime confirmado y scope claro.",
    }


def score_recipe_fit(target: dict[str, Any]) -> list[dict[str, Any]]:
    families = target.get("compatibleRecipeFamilies") or []
    kind = target.get("kind") or "unknown"
    role = semantic_role(target)
    status = target.get("status") or ""
    confidence = target.get("confidence") or "low"
    tokens = split_tokens(target.get("targetId"), target.get("targetLabel"), target.get("panelLabel"), role, kind)
    rows = []
    for family in families:
        ft = split_tokens(family)
        score = 50
        reasons = []
        if status == "confirmed_runtime_data_attribute":
            score += 20; reasons.append("runtime data-* confirmado")
        elif status in {"inferred_from_component_name", "styling_candidate_data_selector", "inferred_dynamic_data_attribute"}:
            score += 8; reasons.append("candidato estático útil")
        if confidence == "high":
            score += 12; reasons.append("confianza alta")
        elif confidence == "medium":
            score += 6; reasons.append("confianza media")
        if kind == "price" and ({"total", "precio", "price", "contraste"} & ft):
            score += 18; reasons.append("familia coincide con número/precio")
        if kind == "button" and ({"cta", "ghost", "disabled", "touch", "boton"} & ft):
            score += 18; reasons.append("familia coincide con botón")
        if kind == "panel" and ({"panel", "glass", "contenedores", "contraste"} & ft):
            score += 16; reasons.append("familia coincide con panel/material")
        if kind == "table" and ({"auditoria", "tabular", "densidad"} & ft):
            score += 16; reasons.append("familia coincide con tabla/auditoría")
        if "total" in tokens and "total" in ft:
            score += 10; reasons.append("target total detectado")
        if "disabled" in tokens and "disabled" in ft:
            score += 10; reasons.append("estado disabled detectado")
        if not reasons:
            reasons.append("fit provisional por familia base")
        rows.append({"recipeFamily": family, "fitScore": max(1, min(99, score)), "reasons": reasons})
    return sorted(rows, key=lambda x: (-x["fitScore"], x["recipeFamily"]))


def build_blast_radius(targets: list[dict[str, Any]]) -> dict[str, Any]:
    by_file: dict[str, list[dict[str, Any]]] = {}
    by_component: dict[str, list[dict[str, Any]]] = {}
    by_selector: dict[str, list[dict[str, Any]]] = {}
    for t in targets:
        by_file.setdefault(t.get("file") or "unknown", []).append(t)
        comp = t.get("component") or ""
        if comp:
            by_component.setdefault(comp, []).append(t)
        sel = t.get("selector") or ""
        if sel:
            by_selector.setdefault(sel, []).append(t)

    per_target = {}
    for t in targets:
        tid = target_control_id(t)
        related = []
        for other in by_file.get(t.get("file") or "unknown", []):
            if other is not t:
                related.append(target_control_id(other))
        comp = t.get("component") or ""
        if comp:
            for other in by_component.get(comp, []):
                if other is not t:
                    related.append(target_control_id(other))
        sel = t.get("selector") or ""
        if sel:
            for other in by_selector.get(sel, []):
                if other is not t:
                    related.append(target_control_id(other))
        related = sorted(set(related))[:80]
        screens = sorted(set(o.get("screenId") for o in by_file.get(t.get("file") or "unknown", []) if o.get("screenId")))
        level = "low"
        if len(related) > 20 or len(screens) > 3:
            level = "high"
        elif len(related) > 6 or len(screens) > 1:
            level = "medium"
        per_target[tid] = {
            "targetId": tid,
            "file": t.get("file"),
            "component": t.get("component"),
            "selector": t.get("selector"),
            "level": level,
            "sameFileTargetCount": len(by_file.get(t.get("file") or "unknown", [])),
            "screensInSameFile": screens,
            "sameComponentOrSelector": related,
            "sharedImpact": screens,
        }
    return {
        "summary": {
            "filesWithMultipleTargets": len([k for k, v in by_file.items() if len(v) > 1]),
            "componentsShared": len([k for k, v in by_component.items() if len(v) > 1]),
            "selectorsShared": len([k for k, v in by_selector.items() if len(v) > 1]),
        },
        "targets": per_target,
    }


def build_surface_intelligence_outputs(atlas: dict[str, Any], maps: dict[str, Any]) -> dict[str, Any]:
    targets = atlas.get("targets", [])
    routes = maps.get("routeMap", [])
    blast = build_blast_radius(targets)
    control_nodes: list[dict[str, Any]] = []
    control_edges: list[dict[str, Any]] = []

    surface_id = normalize_id(atlas.get("surface"), "surface")
    control_nodes.append({"id": surface_id, "type": "surface", "label": atlas.get("surface"), "targetApp": atlas.get("targetApp")})

    seen_nodes = {surface_id}
    for route in routes:
        screen_node = stable_control_id(atlas.get("surface"), route.get("screenId"))
        if screen_node not in seen_nodes:
            seen_nodes.add(screen_node)
            control_nodes.append({"id": screen_node, "type": "screen", "label": route.get("screenLabel"), "route": route.get("route"), "file": route.get("file"), "confidence": route.get("confidence")})
            control_edges.append({"from": surface_id, "to": screen_node, "type": "has_screen"})

    edit_rows = []
    recipe_rows = []
    missing_rows = []
    readiness_rows = []
    next_actions = []
    dropdown: dict[str, Any] = {"schema": "PRISMA_ATLAS_DROPDOWN_MODEL.v1", "surfaces": []}
    surface_entry = {"id": surface_id, "label": atlas.get("surface"), "screens": []}
    screens_index: dict[str, dict[str, Any]] = {}

    for t in targets:
        tid = target_control_id(t)
        br = blast["targets"].get(tid, {})
        readiness = classify_readiness(t, br)
        sem_role = semantic_role(t)
        screen_node = stable_control_id(t.get("surface"), t.get("screenId"))
        zone_node = stable_control_id(t.get("surface"), t.get("screenId"), t.get("zoneId"))
        panel_node = stable_control_id(t.get("surface"), t.get("screenId"), t.get("zoneId"), t.get("panelId"))

        for node_id, node_type, label in [
            (screen_node, "screen", t.get("screenLabel")),
            (zone_node, "zone", t.get("zoneLabel")),
            (panel_node, "panel", t.get("panelLabel")),
        ]:
            if node_id not in seen_nodes:
                seen_nodes.add(node_id)
                control_nodes.append({"id": node_id, "type": node_type, "label": label, "route": t.get("route"), "confidence": t.get("confidence")})
        if tid not in seen_nodes:
            seen_nodes.add(tid)
            control_nodes.append({
                "id": tid,
                "type": "target",
                "label": t.get("targetLabel"),
                "kind": t.get("kind"),
                "semanticRole": sem_role,
                "status": t.get("status"),
                "confidence": t.get("confidence"),
                "readiness": readiness,
                "ownership": {"component": t.get("component"), "file": t.get("file"), "line": t.get("line"), "selector": t.get("selector")},
                "evidence": t.get("evidence"),
            })
        control_edges += [
            {"from": screen_node, "to": zone_node, "type": "has_zone"},
            {"from": zone_node, "to": panel_node, "type": "has_panel"},
            {"from": panel_node, "to": tid, "type": "has_target"},
        ]

        properties = [property_gate(t.get("kind") or "unknown", p, readiness["code"]) for p in (t.get("editableProperties") or [])]
        edit_rows.append({
            "targetControlId": tid,
            "surface": t.get("surface"), "screenId": t.get("screenId"), "screenLabel": t.get("screenLabel"), "route": t.get("route"),
            "zoneId": t.get("zoneId"), "panelId": t.get("panelId"), "targetId": t.get("targetId"), "targetLabel": t.get("targetLabel"),
            "kind": t.get("kind"), "semanticRole": sem_role, "status": t.get("status"), "confidence": t.get("confidence"),
            "readiness": readiness, "properties": properties,
        })
        fits = score_recipe_fit(t)
        recipe_rows.append({
            "targetControlId": tid,
            "targetLabel": t.get("targetLabel"),
            "kind": t.get("kind"),
            "readiness": readiness["code"],
            "rankedRecipeFits": fits,
        })
        if readiness["missingRuntimeMarks"]:
            missing = {
                "targetControlId": tid,
                "file": t.get("file"),
                "line": t.get("line"),
                "targetLabel": t.get("targetLabel"),
                "status": t.get("status"),
                "confidence": t.get("confidence"),
                "missingRuntimeMarks": readiness["missingRuntimeMarks"],
                "suggestedInstrumentation": {
                    "data-surface": normalize_id(t.get("surface")),
                    "data-screen": t.get("screenId"),
                    "data-zone": t.get("zoneId"),
                    "data-panel": t.get("panelId"),
                    "data-target": t.get("targetId"),
                    "data-kind": t.get("kind"),
                    "data-role": sem_role,
                },
                "patchType": "instrumentation_only",
                "forbidden": ["visual CSS change", "business logic change", "Prisma", "package/lockfile edit"],
            }
            missing_rows.append(missing)
        readiness_rows.append({"targetControlId": tid, "readiness": readiness, "blastRadius": br})

        if readiness["code"] != "READY_FOR_VISUAL_RECIPE":
            next_actions.append({
                "targetControlId": tid,
                "priority": readiness["rank"],
                "action": "add_semantic_runtime_marks" if readiness["instrumentationOnlyRecommended"] or readiness["missingRuntimeMarks"] else "review_low_confidence_evidence",
                "patchType": "instrumentation_only" if readiness["missingRuntimeMarks"] else "read_only_review",
                "why": readiness["reason"],
                "confidenceGain": "+40% to +70%" if readiness["missingRuntimeMarks"] else "+10% to +25%",
                "file": t.get("file"), "line": t.get("line"),
                "missingRuntimeMarks": readiness["missingRuntimeMarks"],
            })

        screen_key = t.get("screenId") or "unknown_screen"
        screen_entry = screens_index.setdefault(screen_key, {"id": screen_key, "label": t.get("screenLabel"), "route": t.get("route"), "zones": []})
        zones_index = screen_entry.setdefault("_zones_index", {})
        zone_key = t.get("zoneId") or "unknown_zone"
        zone_entry = zones_index.setdefault(zone_key, {"id": zone_key, "label": t.get("zoneLabel"), "panels": []})
        panels_index = zone_entry.setdefault("_panels_index", {})
        panel_key = t.get("panelId") or "unknown_panel"
        panel_entry = panels_index.setdefault(panel_key, {"id": panel_key, "label": t.get("panelLabel"), "targets": []})
        panel_entry["targets"].append({
            "id": t.get("targetId"), "label": t.get("targetLabel"), "controlId": tid,
            "kind": t.get("kind"), "status": t.get("status"), "confidence": t.get("confidence"),
            "readiness": readiness["code"], "editableNow": readiness["editableNow"],
            "modes": {
                "Rápido": readiness["visualRecipeAllowed"] or readiness["editableNow"],
                "Receta": readiness["visualRecipeAllowed"],
                "Pro": readiness["visualRecipeAllowed"],
                "Instrumentación": readiness["instrumentationOnlyRecommended"] or bool(readiness["missingRuntimeMarks"]),
            },
            "changeTypes": t.get("editableProperties") or [],
            "topRecipes": score_recipe_fit(t)[:4],
            "missingRuntimeMarks": readiness["missingRuntimeMarks"],
        })

    for screen in screens_index.values():
        zones = []
        for zone in screen.pop("_zones_index", {}).values():
            panels = []
            for panel in zone.pop("_panels_index", {}).values():
                panel["targets"] = sorted(panel["targets"], key=lambda x: (x.get("readiness") or "", x.get("label") or ""))
                panels.append(panel)
            zone["panels"] = sorted(panels, key=lambda x: x.get("label") or "")
            zones.append(zone)
        screen["zones"] = sorted(zones, key=lambda x: x.get("label") or "")
        surface_entry["screens"].append(screen)
    surface_entry["screens"] = sorted(surface_entry["screens"], key=lambda x: x.get("label") or "")
    dropdown["surfaces"].append(surface_entry)

    readiness_counts: dict[str, int] = {}
    for row in readiness_rows:
        code = row["readiness"]["code"]
        readiness_counts[code] = readiness_counts.get(code, 0) + 1

    control_graph = {
        "schema": CONTROL_GRAPH_SCHEMA,
        "generatedAt": now_iso(),
        "surface": atlas.get("surface"),
        "targetApp": atlas.get("targetApp"),
        "counts": {"nodes": len(control_nodes), "edges": len(control_edges), **atlas.get("counts", {})},
        "nodes": control_nodes,
        "edges": control_edges,
    }
    patch_readiness = {
        "schema": "PRISMA_PATCH_READINESS.v1",
        "generatedAt": now_iso(),
        "readOnly": True,
        "authorizesPatch": False,
        "counts": readiness_counts,
        "rules": {
            "visualRecipeRequires": ["confirmed runtime data-*", "complete semantic runtime marks", "bounded blast radius", "rollback in future package"],
            "instrumentationOnlyAllows": ["adding data-* semantic marks", "no visual change", "no behavior change"],
            "alwaysForbiddenHere": ["repo write by atlas runner", "git write", "Prisma", "dev server", "package/lockfile change"],
        },
        "targets": readiness_rows,
    }
    next_actions = sorted(next_actions, key=lambda x: (x.get("priority", 99), x.get("file") or "", x.get("line") or 0))[:300]
    return {
        "controlGraph": control_graph,
        "dropdownModel": dropdown,
        "editabilityMatrix": {"schema": "PRISMA_EDITABILITY_MATRIX.v1", "generatedAt": now_iso(), "rows": edit_rows},
        "recipeFitMatrix": {"schema": "PRISMA_RECIPE_FIT_MATRIX.v1", "generatedAt": now_iso(), "rows": recipe_rows},
        "missingMarks": {"schema": "PRISMA_MISSING_MARKS_PLAN.v1", "generatedAt": now_iso(), "targets": missing_rows},
        "patchReadiness": patch_readiness,
        "blastRadiusMap": {"schema": "PRISMA_BLAST_RADIUS_MAP.v1", "generatedAt": now_iso(), **blast},
        "nextBestActions": {"schema": "PRISMA_NEXT_BEST_ACTIONS.v1", "generatedAt": now_iso(), "actions": next_actions},
        "instrumentationQueue": build_instrumentation_queue(missing_rows, readiness_rows, edit_rows),
    }


def _screen_value_score(screen_id: Any) -> int:
    screen = str(screen_id or "").lower()
    weights = {
        "pos": 100,
        "checkout": 96,
        "settings_license": 92,
        "license": 92,
        "inventory": 78,
        "inventory_low_stock": 78,
        "stock": 76,
        "catalog": 72,
        "sales": 68,
        "sales_today": 70,
        "shift": 62,
        "sync": 58,
        "tablet_lab": 52,
        "visual_os": 44,
        "prisma_pulse": 44,
        "shared_tablet": 36,
        "unknown_screen": 8,
    }
    return weights.get(screen, 30)


def _kind_value_score(kind: Any) -> int:
    k = str(kind or "").lower()
    weights = {
        "price": 24,
        "button": 22,
        "field": 18,
        "table": 17,
        "badge": 15,
        "panel": 12,
        "text": 10,
        "background": 8,
        "layout": 7,
        "icon": 5,
        "effect": 4,
        "unknown": 0,
    }
    return weights.get(k, 4)


def _confidence_value_score(confidence: Any) -> int:
    c = str(confidence or "").lower()
    if c == "high":
        return 14
    if c == "medium":
        return 9
    if c == "low":
        return -8
    return 0


def _priority_band(score: int, readiness_code: str) -> str:
    if readiness_code == "BLOCKED_LOW_CONFIDENCE":
        return "P3_REVIEW_FIRST"
    if score >= 125:
        return "P0_CORE_REVENUE_FLOW"
    if score >= 100:
        return "P1_HIGH_VALUE_SURFACE"
    if score >= 76:
        return "P2_PRODUCTIVE_SURFACE"
    return "P3_LOW_RISK_BACKLOG"


def _screen_from_control_id(control_id: Any) -> str:
    parts = str(control_id or "").split(".")
    return parts[1] if len(parts) > 1 else "unknown_screen"


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "unknown")
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def _instrumentation_queue_item(missing: dict[str, Any], edit_row: dict[str, Any] | None) -> dict[str, Any]:
    edit = edit_row or {}
    readiness = (edit.get("readiness") or {}) if isinstance(edit, dict) else {}
    screen_id = edit.get("screenId") or _screen_from_control_id(missing.get("targetControlId"))
    screen_label = edit.get("screenLabel") or titleize(screen_id)
    kind = edit.get("kind") or "unknown"
    confidence = missing.get("confidence") or edit.get("confidence") or "unknown"
    readiness_code = readiness.get("code") or "READY_FOR_INSTRUMENTATION_ONLY"
    value_score = _screen_value_score(screen_id) + _kind_value_score(kind) + _confidence_value_score(confidence)
    marks = missing.get("missingRuntimeMarks") or []
    if len(marks) <= 3:
        value_score += 10
    if readiness_code == "BLOCKED_LOW_CONFIDENCE":
        value_score -= 35
    band = _priority_band(value_score, readiness_code)
    suggested = missing.get("suggestedInstrumentation") or {}
    return {
        "queueId": "tabmarks::" + str(missing.get("targetControlId")),
        "targetControlId": missing.get("targetControlId"),
        "priorityBand": band,
        "valueScore": value_score,
        "screenId": screen_id,
        "screenLabel": screen_label,
        "targetLabel": missing.get("targetLabel") or edit.get("targetLabel") or titleize(missing.get("targetControlId")),
        "kind": kind,
        "semanticRole": suggested.get("data-role") or edit.get("semanticRole"),
        "file": missing.get("file"),
        "line": missing.get("line"),
        "readiness": readiness_code if readiness_code != "READY_FOR_VISUAL_RECIPE" else "READY_FOR_INSTRUMENTATION_ONLY",
        "confidence": confidence,
        "patchType": "instrumentation_only",
        "recommendedPackage": "tabmarks1",
        "recommendedAction": "add_semantic_runtime_marks",
        "reason": "Agregar marcas semánticas runtime antes de permitir recetas visuales o edición remota.",
        "expectedConfidenceGain": "+40% a +70%" if confidence != "low" else "+15% a +35% tras revisión",
        "missingRuntimeMarks": marks,
        "suggestedInstrumentation": suggested,
        "forbiddenInThisAction": ["visual CSS change", "business logic change", "Prisma", "package/lockfile edit", "Git write"],
    }


def _group_queue_batches(actions: list[dict[str, Any]]) -> dict[str, Any]:
    by_screen: dict[str, dict[str, Any]] = {}
    by_file: dict[str, dict[str, Any]] = {}
    for action in actions:
        screen = action.get("screenId") or "unknown_screen"
        s = by_screen.setdefault(screen, {
            "screenId": screen,
            "screenLabel": action.get("screenLabel") or titleize(screen),
            "count": 0,
            "topPriorityBand": action.get("priorityBand"),
            "files": set(),
            "targetControlIds": [],
            "valueScoreTotal": 0,
        })
        s["count"] += 1
        s["files"].add(action.get("file"))
        s["targetControlIds"].append(action.get("targetControlId"))
        s["valueScoreTotal"] += int(action.get("valueScore") or 0)
        file = action.get("file") or "unknown_file"
        f = by_file.setdefault(file, {"file": file, "count": 0, "screens": set(), "targetControlIds": [], "valueScoreTotal": 0})
        f["count"] += 1
        f["screens"].add(screen)
        f["targetControlIds"].append(action.get("targetControlId"))
        f["valueScoreTotal"] += int(action.get("valueScore") or 0)
    screen_batches = []
    for item in by_screen.values():
        item["files"] = sorted(x for x in item["files"] if x)
        item["targetControlIds"] = item["targetControlIds"][:80]
        screen_batches.append(item)
    file_batches = []
    for item in by_file.values():
        item["screens"] = sorted(x for x in item["screens"] if x)
        item["targetControlIds"] = item["targetControlIds"][:80]
        file_batches.append(item)
    screen_batches.sort(key=lambda x: (-int(x.get("valueScoreTotal") or 0), x.get("screenLabel") or ""))
    file_batches.sort(key=lambda x: (-int(x.get("valueScoreTotal") or 0), x.get("file") or ""))
    return {"byScreen": screen_batches, "byFile": file_batches}


def build_instrumentation_queue(missing_rows: list[dict[str, Any]], readiness_rows: list[dict[str, Any]], edit_rows: list[dict[str, Any]]) -> dict[str, Any]:
    edit_by_id = {row.get("targetControlId"): row for row in edit_rows}
    readiness_by_id = {row.get("targetControlId"): row for row in readiness_rows}
    actions: list[dict[str, Any]] = []
    for missing in missing_rows:
        tid = missing.get("targetControlId")
        edit = edit_by_id.get(tid, {})
        readiness = (readiness_by_id.get(tid, {}) or {}).get("readiness") or {}
        if edit and "readiness" not in edit:
            edit = {**edit, "readiness": readiness}
        actions.append(_instrumentation_queue_item(missing, edit))
    actions.sort(key=lambda x: (str(x.get("priorityBand") or "P9"), -int(x.get("valueScore") or 0), x.get("file") or "", int(x.get("line") or 0)))
    batches = _group_queue_batches(actions)
    missing_mark_counts: dict[str, int] = {}
    for action in actions:
        for mark in action.get("missingRuntimeMarks") or []:
            missing_mark_counts[mark] = missing_mark_counts.get(mark, 0) + 1
    counts = {
        "actions": len(actions),
        "byPriorityBand": _count_by(actions, "priorityBand"),
        "byScreen": _count_by(actions, "screenId"),
        "byKind": _count_by(actions, "kind"),
        "byMissingMark": dict(sorted(missing_mark_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "filesToTouchIfAccepted": len(batches["byFile"]),
        "screensToTouchIfAccepted": len(batches["byScreen"]),
    }
    return {
        "schema": "PRISMA_INSTRUMENTATION_QUEUE.v1",
        "generatedAt": now_iso(),
        "readOnly": True,
        "authorizesPatch": False,
        "purpose": "Prioritized queue for future tabmarks instrumentation-only packages. This atlas does not modify the repo.",
        "rules": {
            "allowedFuturePatchType": "instrumentation_only",
            "visualChangeAllowed": False,
            "businessLogicChangeAllowed": False,
            "requiresFreshAuthorityMesh": True,
            "requiresRollback": True,
            "noFakeGreen": True,
        },
        "counts": counts,
        "recommendedOrder": ["P0_CORE_REVENUE_FLOW", "P1_HIGH_VALUE_SURFACE", "P2_PRODUCTIVE_SURFACE", "P3_REVIEW_FIRST", "P3_LOW_RISK_BACKLOG"],
        "batches": batches,
        "actions": actions[:500],
    }


def markdown_instrumentation_queue(queue: dict[str, Any]) -> str:
    lines = ["# PRISMA_INSTRUMENTATION_QUEUE", "", f"Generated: {queue.get('generatedAt')}", "", "Cola priorizada para un futuro paquete `tabmarks1` instrumentation-only. No autoriza cambio visual ni lógico.", "", "## Counts", ""]
    counts = queue.get("counts") or {}
    for key in ["actions", "filesToTouchIfAccepted", "screensToTouchIfAccepted"]:
        lines.append(f"- {key}: {counts.get(key, 0)}")
    lines += ["", "## By priority", ""]
    for band, count in (counts.get("byPriorityBand") or {}).items():
        lines.append(f"- **{band}**: {count}")
    lines += ["", "## Top screen batches", ""]
    for batch in (queue.get("batches") or {}).get("byScreen", [])[:20]:
        lines.append(f"### {batch.get('screenLabel')} (`{batch.get('screenId')}`)")
        lines.append(f"- Targets: {batch.get('count')} | files: {len(batch.get('files') or [])} | score: {batch.get('valueScoreTotal')}")
        for file in (batch.get("files") or [])[:8]:
            lines.append(f"  - `{file}`")
        lines.append("")
    lines += ["## Top actions", ""]
    for action in (queue.get("actions") or [])[:80]:
        lines.append(f"- **{action.get('priorityBand')}** `{action.get('targetControlId')}`")
        lines.append(f"  - screen: `{action.get('screenId')}` kind=`{action.get('kind')}` confidence=`{action.get('confidence')}` score=`{action.get('valueScore')}`")
        lines.append(f"  - file: `{action.get('file')}:{action.get('line')}`")
        lines.append("  - missing: " + ", ".join(f"`{m}`" for m in action.get("missingRuntimeMarks") or []))
    return "\n".join(lines) + "\n"


def markdown_missing_marks(plan: dict[str, Any]) -> str:
    lines = ["# PRISMA_MISSING_MARKS_PLAN", "", f"Generated: {plan.get('generatedAt')}", ""]
    targets = plan.get("targets", [])
    if not targets:
        lines.append("No missing runtime marks detected for current targets.")
        return "\n".join(lines) + "\n"
    lines += ["Estos son candidatos para `tabmarks` instrumentation-only. No implican cambio visual ni lógico.", ""]
    for item in targets[:220]:
        lines.append(f"## `{item.get('targetControlId')}`")
        lines.append(f"- File: `{item.get('file')}:{item.get('line')}`")
        lines.append(f"- Status: `{item.get('status')}` confidence=`{item.get('confidence')}`")
        lines.append("- Missing: " + ", ".join(f"`{m}`" for m in item.get("missingRuntimeMarks", [])))
        lines.append("- Suggested marks:")
        for k, v in (item.get("suggestedInstrumentation") or {}).items():
            lines.append(f"  - `{k}=\"{v}\"`")
        lines.append("")
    if len(targets) > 220:
        lines.append(f"... {len(targets) - 220} más en JSON.")
    return "\n".join(lines) + "\n"


def markdown_next_actions(actions: dict[str, Any]) -> str:
    lines = ["# PRISMA_NEXT_BEST_ACTIONS", "", f"Generated: {actions.get('generatedAt')}", ""]
    rows = actions.get("actions", [])
    if not rows:
        lines.append("No next actions needed. El atlas no detectó candidatos bloqueados.")
        return "\n".join(lines) + "\n"
    for row in rows[:200]:
        lines.append(f"- `{row.get('targetControlId')}` → **{row.get('action')}** `{row.get('patchType')}`")
        lines.append(f"  - why: {row.get('why')}")
        lines.append(f"  - file: `{row.get('file')}:{row.get('line')}`")
        if row.get("missingRuntimeMarks"):
            lines.append("  - missing: " + ", ".join(f"`{m}`" for m in row.get("missingRuntimeMarks")))
    return "\n".join(lines) + "\n"


def markdown_atlas(atlas: dict[str, Any]) -> str:
    lines = [
        "# PRISMA_SURFACE_TARGET_ATLAS",
        "",
        f"Generated: {atlas['generatedAt']}",
        f"Surface: {atlas['surface']}",
        f"Target app: `{atlas['targetApp']}`",
        "",
        "## Counts",
        "",
    ]
    lines += [f"- {k}: {v}" for k, v in atlas["counts"].items()]
    lines += ["", "## Targets confirmados por runtime data-*", ""]
    confirmed = [t for t in atlas["targets"] if t["status"] == "confirmed_runtime_data_attribute"]
    for t in confirmed[:160]:
        lines.append(
            f"- `{t['screenId']}` → `{t['zoneId']}` → `{t['panelId']}` → `{t['targetId']}` "
            f"kind=`{t['kind']}` confidence=`{t['confidence']}` file=`{t['file']}:{t['line']}`"
        )
    if len(confirmed) > 160:
        lines.append(f"- ... {len(confirmed) - 160} más")
    lines += ["", "## Inferidos útiles", ""]
    inferred = [t for t in atlas["targets"] if t["status"] in {"inferred_from_component_name", "styling_candidate_data_selector"}]
    for t in inferred[:160]:
        lines.append(
            f"- `{t['screenId']}` → `{t['targetLabel']}` kind=`{t['kind']}` "
            f"status=`{t['status']}` confidence=`{t['confidence']}` file=`{t['file']}:{t['line']}`"
        )
    if len(inferred) > 160:
        lines.append(f"- ... {len(inferred) - 160} más")
    return "\n".join(lines) + "\n"


def zip_dir(source: Path, dest: Path) -> None:
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as zf:
        for p in sorted(source.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(source).as_posix())


def target_roots(repo_root: Path, target_app: str) -> tuple[str, str, str, list[Path]]:
    key = (target_app or "tablet").strip().lower()
    if key == "all":
        roots = [
            repo_root / rel_root
            for rel_root, _label, _base in SURFACE_ROOTS.values()
            if (repo_root / rel_root).exists()
        ]
        return "all", "Todas", "surfaceatlas1", roots

    rel_root, label, base = SURFACE_ROOTS.get(key, SURFACE_ROOTS["tablet"])
    root = repo_root / rel_root

    if key == "tablet":
        candidates = [
            root / "app" / "app",
            root / "app" / "components",
            root / "app" / "src",
            root / "app" / "lib",
            root / "app" / "styles",
            repo_root / "apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md",
        ]
        roots = [p for p in candidates if p.exists()]
        if not roots:
            roots = [root]
    else:
        roots = [root]
    return key, label, base, roots


def write_fail_zip(staging: Path, fail_zip: Path, exc: BaseException, validation: dict[str, Any]) -> None:
    write_text(staging / "ERROR.txt", traceback.format_exc())
    validation["status"] = "FAIL_SURFACE_TARGET_ATLAS"
    validation["error"] = repr(exc)
    write_json(staging / "reports" / "validation.json", validation)
    write_text(staging / "SUMMARY_FOR_CHAT.md", f"# SUMMARY_FOR_CHAT\n\nStatus: FAIL_SURFACE_TARGET_ATLAS\n\nError: `{repr(exc)}`\n")
    write_text(staging / "CONTINUATION.md", "# CONTINUATION\n\nSurface Target Atlas falló. Revisa `ERROR.txt` y `reports/validation.json`.\n")
    zip_dir(staging, fail_zip)


def run_surface_target_atlas(
    selected_path: str,
    *,
    target_app: str = "tablet",
    output_root: str | os.PathLike[str] = r"F:\descargasf",
    notify: Callable[[str, str], None] | None = None,
) -> str:
    repo_root = find_repo_root(selected_path)
    out_root = Path(output_root).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    app_key, surface_label, zip_base, roots = target_roots(repo_root, target_app)
    stamp = datetime.now().strftime("%d%m %H%M")
    work_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    staging = out_root / f"_{zip_base}_work_{work_stamp}_{os.getpid()}"
    result_zip = out_root / f"{zip_base} {stamp} result.zip"
    fail_zip = out_root / f"{zip_base} {stamp} fail.zip"

    validation = {
        "status": "RUNNING",
        "generatedAt": now_iso(),
        "generatorVersion": "catlas2fix2.surface_intelligence.v3",
        "readOnly": True,
        "authorizesPatch": False,
        "repoRoot": str(repo_root),
        "selectedPath": str(selected_path),
        "targetApp": app_key,
        "surface": surface_label,
        "outputRoot": str(out_root),
        "resultZip": str(result_zip),
        "failZipIfFailure": str(fail_zip),
        "classificationPolicy": {
            "confirmedTargets": "Only literal runtime JSX data-* attributes with target evidence.",
            "supportOnly": "Markdown and JSON specs support context but do not confirm runtime editability.",
            "css": "CSS selectors are mapped; only data selectors enter targets automatically.",
            "generated": "Generated/mechanical Prisma/client/build paths are excluded.",
            "tabletVsTable": "Tokenized classifier prevents 'tablet' from becoming 'table'.",
        },
        "rules": {
            "repoModified": False,
            "gitWrites": False,
            "processKill": False,
            "portFreeing": False,
            "devServerStart": False,
            "prisma": False,
            "packageOrLockfileChanges": False,
            "visualPatch": False,
            "importantAdded": False,
        },
        "checks": {},
        "counts": {},
    }

    try:
        staging.mkdir(parents=True, exist_ok=True)
        (staging / "reports").mkdir(parents=True, exist_ok=True)
        _notify(notify, "Surface Target Atlas · preflight", f"{surface_label} | {repo_root}")

        validation["checks"]["repo_exists"] = repo_root.exists()
        validation["checks"]["app_root_exists"] = (repo_root / "apps" / "terminal-de-venta-system").exists()
        validation["checks"]["surface_roots"] = [{"path": str(p), "exists": p.exists()} for p in roots]
        if not repo_root.exists():
            raise FileNotFoundError(f"Repo root no existe: {repo_root}")

        git_status = run_cmd(["git", "-C", str(repo_root), "status", "--short", "--branch"])
        write_text(
            staging / "reports" / "git_status.txt",
            "## git status --short --branch\n"
            + git_status.get("stdout", "")
            + "\n## stderr\n"
            + git_status.get("stderr", ""),
        )

        _notify(notify, "Surface Target Atlas · escaneando archivos", f"roots={len(roots)}")
        files, skipped = iter_scan_files(roots)
        scans: list[dict[str, Any]] = []
        max_workers = max(1, min(18, int(os.environ.get("CODE_ATLAS_SURFACE_ATLAS_WORKERS", "18") or "18")))
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futs = {pool.submit(scan_file, p, repo_root, surface_label): p for p in files}
            done, total = 0, len(futs)
            for fut in as_completed(futs):
                scans.append(fut.result())
                done += 1
                if total and (done == total or done % max(1, total // 10 or 1) == 0):
                    _notify(notify, f"Surface Target Atlas · {int(done * 100 / total)}% archivos", f"{done}/{total}")

        scans.sort(key=lambda x: x["file"].lower())
        route_map = build_route_map(repo_root, roots, surface_label)
        maps = build_maps(scans, route_map, skipped)

        atlas = {
            "schema": "PRISMA_SURFACE_TARGET_ATLAS.v2",
            "generatedAt": now_iso(),
            "readOnly": True,
            "authorizesPatch": False,
            "repoRoot": str(repo_root),
            "targetApp": app_key,
            "surface": surface_label,
            "selection": {"selectedPath": str(selected_path), "roots": [str(p) for p in roots]},
            "counts": {
                "filesScanned": len(scans),
                "filesSkippedGeneratedOrMechanical": len(skipped),
                "routes": len(route_map),
                "dataAttributes": len(maps["dataAttributeMap"]),
                "cssSelectors": len(maps["cssSelectorMap"]),
                "components": len(maps["componentPanelMap"]),
                "targets": len(maps["targets"]),
                "confirmedRuntimeTargets": len([t for t in maps["targets"] if t["status"] == "confirmed_runtime_data_attribute"]),
                "supportOnlyReferences": len(maps["supportReferences"]),
                "cssStylingCandidates": len(maps["cssStylingCandidates"]),
                "lowConfidenceTargets": len(maps["lowConfidence"]),
                "unmappedFiles": len(maps["unmapped"]),
            },
            "targets": maps["targets"],
            "supportReferences": maps["supportReferences"],
            "cssStylingCandidates": maps["cssStylingCandidates"],
        }

        intelligence = build_surface_intelligence_outputs(atlas, maps)

        validation["status"] = "PASS_SURFACE_INTELLIGENCE_ATLAS_GENERATED"
        validation["counts"] = atlas["counts"]
        validation["checks"]["has_required_outputs"] = True
        validation["checks"]["no_repo_writes_by_runner"] = True
        validation["checks"]["generated_paths_skipped"] = len(skipped)
        validation["checks"]["markdown_not_confirmed"] = True
        validation["checks"]["tablet_not_table_guard"] = True
        validation["checks"]["control_graph_generated"] = True
        validation["checks"]["editability_matrix_generated"] = True
        validation["checks"]["patch_readiness_generated"] = True
        validation["checks"]["instrumentation_queue_generated"] = True

        _notify(notify, "Surface Target Atlas · escribiendo reportes", str(staging))
        files_scanned = [
            {
                "file": s["file"],
                "surface": s["surface"],
                "suffix": s["suffix"],
                "sourceTier": s["sourceTier"],
                "sizeBytes": s["sizeBytes"],
                "sha256": s["sha256"],
                "screen": s["screen"],
                "dataAttributeCount": len(s["dataAttributes"]),
                "cssSelectorCount": len(s["cssSelectors"]),
                "componentCount": len(s["components"]),
                "textLiteralCount": len(s["textLiterals"]),
            }
            for s in scans
        ]

        write_text(
            staging / "SUMMARY_FOR_CHAT.md",
            "\n".join([
                "# SUMMARY_FOR_CHAT",
                "",
                f"Status: {validation['status']}",
                "",
                f"Surface/App: {surface_label} (`{app_key}`)",
                f"ZIP: `{result_zip}`",
                "",
                "Counts:",
                *(f"- {k}: {v}" for k, v in atlas["counts"].items()),
                "",
                "Surface Intelligence outputs:",
                "- Control Graph, Editability Matrix, Recipe Fit Matrix, Missing Marks, Blast Radius, Patch Readiness, Next Best Actions e Instrumentation Queue.",
                "",
                "Cambios base heredados:",
                "- Excluye `.generated`, `prisma-client`, builds y rutas mecánicas.",
                "- Markdown/JSON quedan como apoyo, no como prueba runtime.",
                "- CSS queda en mapa; sólo selectores `data-*` entran automáticamente como candidatos.",
                "- `tablet` ya no se clasifica como `table`.",
                "- Targets confirmados requieren evidencia runtime `data-*`.",
                "",
                "Este atlas es read-only. No modifica repo, Git, procesos, puertos, Prisma, package.json ni lockfiles.",
                "",
            ]),
        )
        write_text(
            staging / "CONTINUATION.md",
            "# CONTINUATION\n\n"
            "Usar este ZIP limpio para diseñar dropdowns dependientes o integrar el atlas a Tablet Lab en una fase posterior.\n\n"
            "Reglas: runtime data attributes primero; TSX/CSS como inferencia; markdown y JSON sólo apoyo; no declarar editable sin evidencia suficiente.\n",
        )
        write_json(staging / "PRISMA_SURFACE_TARGET_ATLAS.json", atlas)
        write_text(staging / "PRISMA_SURFACE_TARGET_ATLAS.md", markdown_atlas(atlas))
        write_json(staging / "TARGET_REGISTRY_DRAFT.json", maps["targets"])
        write_json(staging / "SCREEN_ROUTE_MAP.json", maps["routeMap"])
        write_json(staging / "COMPONENT_PANEL_MAP.json", maps["componentPanelMap"])
        write_json(staging / "DATA_ATTRIBUTE_MAP.json", maps["dataAttributeMap"])
        write_json(staging / "CSS_SELECTOR_MAP.json", maps["cssSelectorMap"])
        write_json(staging / "RECIPE_COMPATIBILITY_DRAFT.json", maps["recipeCompatibility"])
        write_json(staging / "PRISMA_CONTROL_GRAPH.json", intelligence["controlGraph"])
        write_json(staging / "PRISMA_ATLAS_DROPDOWN_MODEL.json", intelligence["dropdownModel"])
        write_json(staging / "PRISMA_EDITABILITY_MATRIX.json", intelligence["editabilityMatrix"])
        write_json(staging / "PRISMA_RECIPE_FIT_MATRIX.json", intelligence["recipeFitMatrix"])
        write_json(staging / "PRISMA_MISSING_MARKS_PLAN.json", intelligence["missingMarks"])
        write_text(staging / "PRISMA_MISSING_MARKS_PLAN.md", markdown_missing_marks(intelligence["missingMarks"]))
        write_json(staging / "PRISMA_PATCH_READINESS.json", intelligence["patchReadiness"])
        write_json(staging / "PRISMA_BLAST_RADIUS_MAP.json", intelligence["blastRadiusMap"])
        write_json(staging / "PRISMA_NEXT_BEST_ACTIONS.json", intelligence["nextBestActions"])
        write_text(staging / "PRISMA_NEXT_BEST_ACTIONS.md", markdown_next_actions(intelligence["nextBestActions"]))
        write_json(staging / "PRISMA_INSTRUMENTATION_QUEUE.json", intelligence["instrumentationQueue"])
        write_text(staging / "PRISMA_INSTRUMENTATION_QUEUE.md", markdown_instrumentation_queue(intelligence["instrumentationQueue"]))
        write_json(staging / "reports" / "files_scanned.json", {
            "files": files_scanned,
            "skippedGeneratedOrMechanical": maps["skippedFiles"][:2000],
        })
        write_json(staging / "reports" / "validation.json", validation)

        write_text(
            staging / "UNMAPPED_TARGETS.md",
            "# UNMAPPED_TARGETS\n\n"
            + "\n".join(f"- `{u['file']}`: {u['reason']} sourceTier=`{u['sourceTier']}`" for u in maps["unmapped"][:500])
            + "\n",
        )
        write_text(
            staging / "LOW_CONFIDENCE_TARGETS.md",
            "# LOW_CONFIDENCE_TARGETS\n\n"
            + "\n".join(
                f"- `{t['screenId']}` → `{t['targetLabel']}` kind=`{t['kind']}` status=`{t['status']}` file=`{t['file']}:{t['line']}`"
                for t in maps["lowConfidence"][:500]
            )
            + "\n",
        )
        write_text(
            staging / "SURFACE_SCOPE_GUARD.md",
            f"""# SURFACE_SCOPE_GUARD

Status: {validation['status']}
Surface/App: {surface_label}

## Allowed

- Read files under selected surface roots.
- Generate atlas outputs in `F:\\descargasf`.
- Use Git status as read-only context.

## Forbidden

- Repo writes.
- Git writes.
- Process kill.
- Port freeing.
- Dev server start.
- Prisma generation.
- package.json or lockfile changes.
- Visual patches.
- Declaring markdown/JSON support references as confirmed runtime edit targets.
- Treating generated Prisma/client code as visual surface.

## Classification

- Confirmed target: literal `data-*` evidence in runtime JSX.
- Medium candidate: dynamic runtime `data-*` or CSS data selector.
- Low candidate: component/CSS inference.
- Support-only: markdown and JSON specs.
""",
        )

        required = [
            "SUMMARY_FOR_CHAT.md",
            "CONTINUATION.md",
            "PRISMA_SURFACE_TARGET_ATLAS.json",
            "PRISMA_SURFACE_TARGET_ATLAS.md",
            "TARGET_REGISTRY_DRAFT.json",
            "SCREEN_ROUTE_MAP.json",
            "COMPONENT_PANEL_MAP.json",
            "DATA_ATTRIBUTE_MAP.json",
            "CSS_SELECTOR_MAP.json",
            "RECIPE_COMPATIBILITY_DRAFT.json",
            "UNMAPPED_TARGETS.md",
            "LOW_CONFIDENCE_TARGETS.md",
            "SURFACE_SCOPE_GUARD.md",
            "reports/git_status.txt",
            "reports/files_scanned.json",
            "reports/validation.json",
            "PRISMA_CONTROL_GRAPH.json",
            "PRISMA_ATLAS_DROPDOWN_MODEL.json",
            "PRISMA_EDITABILITY_MATRIX.json",
            "PRISMA_RECIPE_FIT_MATRIX.json",
            "PRISMA_MISSING_MARKS_PLAN.json",
            "PRISMA_MISSING_MARKS_PLAN.md",
            "PRISMA_PATCH_READINESS.json",
            "PRISMA_BLAST_RADIUS_MAP.json",
            "PRISMA_NEXT_BEST_ACTIONS.json",
            "PRISMA_NEXT_BEST_ACTIONS.md",
            "PRISMA_INSTRUMENTATION_QUEUE.json",
            "PRISMA_INSTRUMENTATION_QUEUE.md",
        ]
        missing = [p for p in required if not (staging / p).exists()]
        if missing:
            raise RuntimeError(f"Faltan outputs requeridos: {missing}")

        zip_dir(staging, result_zip)
        _notify(notify, "Surface Target Atlas · listo", str(result_zip))
        return str(result_zip)

    except Exception as exc:
        try:
            write_fail_zip(staging, fail_zip, exc, validation)
        except Exception:
            pass
        _notify(notify, "Surface Target Atlas · FAIL", repr(exc))
        return str(fail_zip)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PRISMA Surface Target Atlas read-only generator")
    parser.add_argument("--selected-path", required=True)
    parser.add_argument("--target-app", default="tablet")
    parser.add_argument("--output-root", default=r"F:\descargasf")
    args = parser.parse_args(argv)
    print(run_surface_target_atlas(selected_path=args.selected_path, target_app=args.target_app, output_root=args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
