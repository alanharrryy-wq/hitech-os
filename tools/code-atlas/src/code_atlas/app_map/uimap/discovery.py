from __future__ import annotations

import hashlib
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .contracts import (
    ADAPTERS,
    CONDITIONAL_STATES,
    REQUIRED_STATES,
    add_integrity,
    sha256_file,
    slug,
    stable_id,
    upper_token,
)

EXCLUDED_PARTS = {
    ".git", ".hg", ".svn", ".next", ".turbo", "node_modules", "dist", "build", "coverage",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv", "env",
    ".mam-runtime", "playwright", "ms-playwright", "fixtures", "screenshots",
    "_dependency_graphs", ".prisma_backups", ".prisma_installer_backups", "tools/_local",
}
SOURCE_EXTS = {".tsx", ".jsx", ".ts", ".js", ".mjs", ".cjs", ".vue", ".svelte"}
STYLE_EXTS = {".css", ".scss", ".sass", ".less"}
CONFIG_EXTS = {".json", ".jsonl", ".md", ".csv"}
SCAN_EXTS = SOURCE_EXTS | STYLE_EXTS | {".json"}

RUNTIME_ROOT_CANDIDATES: dict[str, tuple[str, ...]] = {
    "tb": (
        "apps/terminal-de-venta-system/products/tablet/app",
        "apps/terminal-de-venta-system/products/tablet",
        "products/tablet/app",
        "products/tablet",
    ),
    "pc": (
        "apps/terminal-de-venta-system/products/pc/app",
        "apps/terminal-de-venta-system/products/pc",
        "products/pc/app",
        "products/pc",
    ),
    "mb": (
        "apps/terminal-de-venta-system/products/mobile/app",
        "apps/terminal-de-venta-system/products/mobile",
        "products/mobile/app",
        "products/mobile",
    ),
    "web": (
        "apps/terminal-de-venta-system/products/web/app",
        "apps/terminal-de-venta-system/products/web",
        "apps/terminal-de-venta-system/products/prisma-web/app",
        "apps/terminal-de-venta-system/products/prisma-web",
        "products/web/app",
        "products/web",
    ),
    "cl": (
        "apps/terminal-de-venta-system/products/chart-lab/app",
        "apps/terminal-de-venta-system/products/chart-lab",
        "products/chart-lab/app",
        "products/chart-lab",
    ),
    "cc": (
        "apps/terminal-de-venta-system/Control Center",
        "apps/terminal-de-venta-system/products/control-center",
        "products/control-center",
    ),
    "cmd": (
        "apps/terminal-de-venta-system/prisma-control-center",
        "apps/terminal-de-venta-system/Prisma Cloud Ctr",
        "apps/terminal-de-venta-system/products/cloud-command-center",
        "products/cloud-command-center",
    ),
    "shared": (
        "apps/terminal-de-venta-system/shared",
        "apps/terminal-de-venta-system/packages/ui",
        "packages/ui",
        "packages/shared-ui",
        "shared/ui",
    ),
}

RUNTIME_LABELS = {
    "tb": "3120 Tablet POS",
    "pc": "3130 PC Admin",
    "mb": "3140 Mobile Companion",
    "web": "3110 Web/Portal/Marketplace",
    "cl": "3000 Chart Lab",
    "cc": "3150 SaaS Control Center",
    "cmd": "3160 Cloud Command Center",
    "shared": "Shared UI cross-runtime",
}

HTML_WIDGETS = {
    "button": "button", "input": "input", "select": "select", "textarea": "input", "form": "form",
    "table": "table", "ul": "list", "ol": "list", "li": "row", "nav": "navigation", "dialog": "modal",
    "svg": "icon", "img": "image", "a": "action", "canvas": "chart", "progress": "kpi",
}
WIDGET_TYPE_SUFFIX = {
    "button": "BTN", "action": "ACT", "input": "INP", "select": "SEL", "form": "FRM", "table": "TBL",
    "list": "LST", "row": "ROW", "kpi": "KPI", "chart": "CHT", "card": "CARD", "panel": "PNL",
    "navigation": "NAV", "tab": "TAB", "toolbar": "TBR", "breadcrumb": "BC", "modal": "MOD",
    "drawer": "DRW", "popover": "POP", "tooltip": "TIP", "menu": "MNU", "toast": "TST",
    "alert": "ALT", "loading": "LOD", "empty": "EMP", "error": "ERR", "icon": "ICO", "image": "IMG",
    "overlay": "OVR", "container": "CTR", "text": "TXT", "control": "CTL",
}

@dataclass(slots=True)
class RouteRecord:
    runtime_alias: str
    route_id: str
    route_path: str
    source_file: str
    source_hash: str
    kind: str
    imports: list[str] = field(default_factory=list)

@dataclass(slots=True)
class CssTarget:
    class_name: str
    selector: str
    source_file: str
    source_hash: str
    pseudo_element: str | None
    state_selector: str
    at_rule: str | None
    anchor_kind: str
    target_role: str
    declarations: dict[str, str] = field(default_factory=dict)

@dataclass(slots=True)
class UiCandidate:
    runtime_alias: str
    route_path: str
    route_id: str
    route_source_file: str
    render_source_file: str
    render_symbol: str
    owner_file: str
    owner_symbol: str
    class_name: str | None
    tag_name: str
    widget_kind: str
    text_hint: str
    instance_policy: str
    data_attributes: dict[str, str]
    source_hash: str
    projection_of_component_id: str | None = None
    generated_projection: bool = False
    multiple_owner_candidates: list[str] = field(default_factory=list)


def norm_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def excluded(path: Path) -> bool:
    low_parts = [p.lower() for p in path.parts]
    for part in low_parts:
        if part in EXCLUDED_PARTS:
            return True
    joined = "/".join(low_parts)
    if "liquid glass capsules" in joined or "liquid-glass-capsules" in joined or "liquid_glass_capsules" in joined:
        return True
    return False


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def iter_files(root: Path, extensions: set[str] | None = None) -> Iterable[Path]:
    if not root.exists():
        return []
    extset = extensions or SCAN_EXTS
    out: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in extset and not excluded(path):
            out.append(path)
    return out


def parallel_hash(paths: Iterable[Path], workers: int = 18) -> dict[Path, str]:
    unique = sorted(set(paths), key=lambda p: str(p).lower())
    result: dict[Path, str] = {}
    with ThreadPoolExecutor(max_workers=max(1, min(18, workers))) as pool:
        futures = {pool.submit(sha256_file, p): p for p in unique}
        for future in as_completed(futures):
            path = futures[future]
            try:
                result[path] = future.result()
            except Exception:
                result[path] = ""
    return result


def resolve_runtime_roots(product_root: Path) -> dict[str, list[Path]]:
    resolved: dict[str, list[Path]] = {}
    for alias, candidates in RUNTIME_ROOT_CANDIDATES.items():
        found: list[Path] = []
        for raw in candidates:
            path = product_root / raw
            if path.exists() and path.is_dir():
                found.append(path.resolve())
        # Deduplicate nested mirrors. Prefer the most specific first existing candidate.
        unique: list[Path] = []
        for path in found:
            if path not in unique:
                unique.append(path)
        resolved[alias] = unique[:1]
    return resolved


NEXT_ROUTE_ENTRYPOINT_KINDS = {
    "page": "page",
    "route": "api_route",
    "layout": "layout",
    "template": "template",
    "loading": "loading",
    "error": "error_boundary",
    "global-error": "global_error_boundary",
    "not-found": "not_found_boundary",
    "default": "parallel_route_default",
}


def route_path_from_file(root: Path, path: Path) -> tuple[str, str] | None:
    rel = path.relative_to(root).as_posix()
    stem = path.stem.lower()
    is_next_route_entrypoint = stem in NEXT_ROUTE_ENTRYPOINT_KINDS and path.suffix.lower() in SOURCE_EXTS
    if not is_next_route_entrypoint:
        # classic pages router
        if "/pages/" not in f"/{rel.lower()}" and not rel.lower().startswith("pages/"):
            return None
    parts = list(path.relative_to(root).parts)
    kind = NEXT_ROUTE_ENTRYPOINT_KINDS.get(stem, "page")
    if "app" in [p.lower() for p in parts]:
        idx = [p.lower() for p in parts].index("app")
        route_parts = parts[idx + 1 : -1]
    elif "pages" in [p.lower() for p in parts]:
        idx = [p.lower() for p in parts].index("pages")
        route_parts = parts[idx + 1 :]
        if route_parts:
            route_parts[-1] = Path(route_parts[-1]).stem
            if route_parts[-1].lower() == "index":
                route_parts = route_parts[:-1]
    else:
        route_parts = parts[:-1]
    cleaned = []
    for segment in route_parts:
        if segment.startswith("(") and segment.endswith(")"):
            continue
        if segment.startswith("@"):
            continue
        cleaned.append(segment)
    route = "/" + "/".join(cleaned)
    route = re.sub(r"/+", "/", route)
    if route != "/" and route.endswith("/"):
        route = route[:-1]
    return route or "/", kind


def parse_imports(text: str) -> list[str]:
    patterns = [
        r"(?:import|export)\s+(?:[^;]*?\s+from\s+)?[\"']([^\"']+)[\"']",
        r"require\(\s*[\"']([^\"']+)[\"']\s*\)",
        r"import\(\s*[\"']([^\"']+)[\"']\s*\)",
    ]
    found: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            value = match.group(1)
            if value not in found:
                found.append(value)
    return found


RESOLUTION_EXTS = (
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte",
    ".json", ".css", ".scss", ".sass", ".less",
)


def load_tsconfig_path_aliases(root: Path) -> list[dict[str, Any]]:
    """Load deterministic path aliases for source reachability only.

    Alias targets are always confined to the current runtime root. A path alias
    may prove that a file is reachable; it never grants ownership or visual
    authority by itself.
    """
    config = next(
        (candidate for candidate in (root / "tsconfig.json", root / "jsconfig.json") if candidate.is_file()),
        None,
    )
    if config is None:
        return []
    try:
        payload = json.loads(read_text(config))
    except Exception:
        return []
    compiler = payload.get("compilerOptions") or {}
    paths = compiler.get("paths") or {}
    if not isinstance(paths, dict):
        return []
    base_dir = (config.parent / str(compiler.get("baseUrl") or ".")).resolve()
    rules: list[dict[str, Any]] = []
    for pattern, raw_targets in paths.items():
        if not isinstance(pattern, str) or pattern.count("*") > 1:
            continue
        targets = raw_targets if isinstance(raw_targets, list) else [raw_targets]
        targets = [str(value) for value in targets if isinstance(value, str) and value.strip()]
        if not targets:
            continue
        if "*" in pattern:
            prefix, suffix = pattern.split("*", 1)
            exact = False
        else:
            prefix, suffix, exact = pattern, "", True
        rules.append({
            "pattern": pattern,
            "prefix": prefix,
            "suffix": suffix,
            "exact": exact,
            "targets": targets,
            "baseDir": base_dir,
        })
    return sorted(
        rules,
        key=lambda row: (
            -int(bool(row["exact"])),
            -len(str(row["prefix"])),
            -len(str(row["suffix"])),
            str(row["pattern"]),
        ),
    )


def _resolve_file_base(base: Path, root: Path) -> Path | None:
    root_resolved = root.resolve()
    candidates = [base.resolve()]
    candidates.extend(Path(str(base) + ext).resolve() for ext in RESOLUTION_EXTS)
    candidates.extend((base / ("index" + ext)).resolve() for ext in RESOLUTION_EXTS)
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            candidate.relative_to(root_resolved)
        except Exception:
            continue
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _alias_match(rule: dict[str, Any], spec: str) -> str | None:
    pattern = str(rule["pattern"])
    if rule["exact"]:
        return "" if spec == pattern else None
    prefix = str(rule["prefix"])
    suffix = str(rule["suffix"])
    if not spec.startswith(prefix) or (suffix and not spec.endswith(suffix)):
        return None
    end = len(spec) - len(suffix) if suffix else len(spec)
    if end < len(prefix):
        return None
    return spec[len(prefix):end]


def resolve_import(
    source: Path,
    spec: str,
    root: Path,
    alias_rules: list[dict[str, Any]] | None = None,
) -> Path | None:
    if spec.startswith("."):
        return _resolve_file_base((source.parent / spec).resolve(), root)

    rules = alias_rules if alias_rules is not None else load_tsconfig_path_aliases(root)
    matches: list[tuple[tuple[int, int, int], dict[str, Any], str]] = []
    for rule in rules:
        wildcard = _alias_match(rule, spec)
        if wildcard is None:
            continue
        score = (
            int(bool(rule["exact"])),
            len(str(rule["prefix"])),
            len(str(rule["suffix"])),
        )
        matches.append((score, rule, wildcard))
    if not matches:
        return None

    best_score = max(score for score, _, _ in matches)
    best = [(rule, wildcard) for score, rule, wildcard in matches if score == best_score]
    resolved: set[Path] = set()
    for rule, wildcard in sorted(best, key=lambda item: str(item[0]["pattern"])):
        chosen: Path | None = None
        for target_pattern in rule["targets"]:
            if target_pattern.count("*") > 1:
                continue
            substituted = target_pattern.replace("*", wildcard) if "*" in target_pattern else target_pattern
            chosen = _resolve_file_base((Path(rule["baseDir"]) / substituted).resolve(), root)
            if chosen is not None:
                break
        if chosen is not None:
            resolved.add(chosen.resolve())
    return next(iter(resolved)) if len(resolved) == 1 else None


def discover_routes(runtime_alias: str, root: Path, product_root: Path, hashes: dict[Path, str]) -> list[RouteRecord]:
    routes: list[RouteRecord] = []
    for path in sorted(iter_files(root, SOURCE_EXTS), key=lambda p: str(p).lower()):
        info = route_path_from_file(root, path)
        if not info:
            continue
        route_path, kind = info
        source_rel = norm_rel(product_root, path)
        route_slug = slug(route_path.strip("/") or "home")
        route_id = stable_id("ROUTE", runtime_alias, route_slug)
        routes.append(RouteRecord(
            runtime_alias=runtime_alias,
            route_id=route_id,
            route_path=route_path,
            source_file=source_rel,
            source_hash=hashes.get(path, ""),
            kind=kind,
            imports=parse_imports(read_text(path)),
        ))
    return routes


def build_route_reachability(root: Path, product_root: Path, routes: list[RouteRecord]) -> dict[str, list[RouteRecord]]:
    alias_rules = load_tsconfig_path_aliases(root)
    rel_to_path: dict[str, Path] = {}
    for path in iter_files(root, SOURCE_EXTS | STYLE_EXTS | {".json"}):
        rel_to_path[norm_rel(product_root, path)] = path
    path_to_rel = {path.resolve(): rel for rel, path in rel_to_path.items()}
    reach: dict[str, list[RouteRecord]] = {}
    for route in routes:
        start = rel_to_path.get(route.source_file)
        if not start:
            continue
        queue = [start]
        visited: set[Path] = set()
        while queue and len(visited) < 12000:
            current = queue.pop(0).resolve()
            if current in visited:
                continue
            visited.add(current)
            rel = path_to_rel.get(current)
            if rel:
                reach.setdefault(rel, []).append(route)
            text = read_text(current)
            for spec in parse_imports(text):
                target = resolve_import(current, spec, root, alias_rules)
                if target is not None and target.resolve() not in visited:
                    queue.append(target)
    for rel in list(reach):
        reach[rel] = sorted(reach[rel], key=lambda r: (r.route_path, r.source_file))
    return reach


def extract_css_blocks(text: str) -> list[tuple[str, str, str | None]]:
    # Conservative, brace-aware enough for CSS/SCSS surface mapping. Nested blocks remain evidence, not patch instructions.
    blocks: list[tuple[str, str, str | None]] = []
    stack: list[tuple[int, str]] = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        if text[i] == "{":
            start = i - 1
            while start >= 0 and text[start] not in "{};":
                start -= 1
            header = text[start + 1 : i].strip()
            stack.append((i, header))
        elif text[i] == "}" and stack:
            open_pos, header = stack.pop()
            body = text[open_pos + 1 : i]
            at_rule = None
            if header.startswith("@"):
                at_rule = header
            elif header and not header.startswith("$"):
                parent_at = next((h for _, h in reversed(stack) if h.startswith("@")), None)
                blocks.append((header, body, parent_at))
        i += 1
    return blocks


def declaration_map(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for match in re.finditer(r"(?:^|;)\s*([\w-]+)\s*:\s*([^;{}]+)", body, flags=re.MULTILINE):
        out[match.group(1).strip()] = match.group(2).strip()
    return out


def infer_target_role(selector: str) -> str:
    low = selector.lower()
    if "::before" in low or "::after" in low:
        return "PSEUDO_ELEMENT"
    if any(word in low for word in ("icon", "glyph", "svg")):
        return "ICON"
    if any(word in low for word in ("overlay", "backdrop", "scrim")):
        return "OVERLAY"
    if any(word in low for word in ("text", "label", "copy", "title", "subtitle", "amount", "price")):
        return "TEXT"
    if any(word in low for word in ("error", "warning", "success", "feedback", "toast", "alert")):
        return "FEEDBACK"
    if any(word in low for word in ("button", "btn", "input", "select", "control", "checkbox", "radio")):
        return "CONTROL"
    if any(word in low for word in ("background", "scene", "wallpaper")):
        return "BACKGROUND"
    if any(word in low for word in ("card", "panel", "container", "shell", "section")):
        return "CONTAINER"
    return "ROOT"


def state_from_selector(selector: str, at_rule: str | None) -> str:
    low = selector.lower()
    if "focus-visible" in low:
        return "focus-visible"
    if ":focus" in low:
        return "focus"
    if ":hover" in low:
        return "hover"
    if ":active" in low or "[data-state=\"pressed\"]" in low or "[aria-pressed=\"true\"]" in low:
        return "pressed"
    if ":disabled" in low or "[disabled]" in low or "[aria-disabled=\"true\"]" in low:
        return "disabled"
    for state in ("loading", "success", "warning", "error"):
        if state in low:
            return state
    if at_rule and "prefers-reduced-motion" in at_rule.lower():
        return "reduced-motion"
    return "default"


def extract_css_targets(style_path: Path, product_root: Path, source_hash: str) -> list[CssTarget]:
    text = read_text(style_path)
    rel = norm_rel(product_root, style_path)
    targets: list[CssTarget] = []
    for header, body, at_rule in extract_css_blocks(text):
        for selector in [s.strip() for s in header.split(",") if s.strip()]:
            for match in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_-]*)", selector):
                class_name = match.group(1)
                pseudo = None
                if "::before" in selector:
                    pseudo = "::before"
                elif "::after" in selector:
                    pseudo = "::after"
                targets.append(CssTarget(
                    class_name=class_name,
                    selector=selector,
                    source_file=rel,
                    source_hash=source_hash,
                    pseudo_element=pseudo,
                    state_selector=state_from_selector(selector, at_rule),
                    at_rule=at_rule,
                    anchor_kind="CSS_MODULE_CLASS" if ".module." in style_path.name.lower() else "CSS_SELECTOR",
                    target_role=infer_target_role(selector),
                    declarations=declaration_map(body),
                ))
    # stable dedupe
    dedupe: dict[tuple[str, str, str, str], CssTarget] = {}
    for target in targets:
        key = (target.class_name, target.selector, target.state_selector, target.at_rule or "")
        dedupe[key] = target
    return [dedupe[key] for key in sorted(dedupe)]


def extract_export_symbols(text: str, fallback: str) -> list[str]:
    symbols: list[str] = []
    patterns = [
        r"export\s+(?:default\s+)?function\s+([A-Za-z_$][\w$]*)",
        r"export\s+(?:default\s+)?class\s+([A-Za-z_$][\w$]*)",
        r"export\s+(?:default\s+)?const\s+([A-Za-z_$][\w$]*)",
        r"export\s*\{([^}]+)\}",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            if "," in match.group(1) or " as " in match.group(1):
                for item in match.group(1).split(","):
                    name = item.strip().split(" as ")[-1].strip()
                    if re.match(r"^[A-Za-z_$][\w$]*$", name) and name not in symbols:
                        symbols.append(name)
            else:
                name = match.group(1)
                if name not in symbols:
                    symbols.append(name)
    return symbols or [fallback]


def infer_widget_kind(tag: str, class_name: str | None, symbol: str, attrs: str = "") -> str:
    low = " ".join([tag, class_name or "", symbol, attrs]).lower()
    if tag.lower() in HTML_WIDGETS:
        base = HTML_WIDGETS[tag.lower()]
    else:
        base = "control"
    priority = [
        ("tooltip", "tooltip"), ("popover", "popover"), ("drawer", "drawer"), ("modal", "modal"),
        ("dialog", "modal"), ("toast", "toast"), ("alert", "alert"), ("breadcrumb", "breadcrumb"),
        ("toolbar", "toolbar"), ("tabs", "tab"), ("tab", "tab"), ("chart", "chart"), ("graph", "chart"),
        ("kpi", "kpi"), ("metric", "kpi"), ("card", "card"), ("panel", "panel"), ("container", "container"),
        ("overlay", "overlay"), ("backdrop", "overlay"), ("menu", "menu"), ("nav", "navigation"),
        ("select", "select"), ("combobox", "select"), ("input", "input"), ("form", "form"),
        ("table", "table"), ("list", "list"), ("row", "row"), ("icon", "icon"), ("image", "image"),
        ("loading", "loading"), ("spinner", "loading"), ("empty", "empty"), ("error", "error"),
        ("button", "button"), ("btn", "button"), ("action", "action"),
    ]
    for needle, kind in priority:
        if needle in low:
            return kind
    return base


def infer_region(route_path: str, class_name: str | None, symbol: str, widget_kind: str) -> str:
    low = " ".join([route_path, class_name or "", symbol, widget_kind]).lower()
    if any(x in low for x in ("cobrar", "checkout", "payment", "pay", "tender")):
        return "payment"
    if any(x in low for x in ("header", "topbar", "appbar")):
        return "header"
    if any(x in low for x in ("footer", "bottom")):
        return "footer"
    if any(x in low for x in ("nav", "menu", "sidebar", "breadcrumb", "tabs")):
        return "navigation"
    if any(x in low for x in ("filter", "search", "query")):
        return "filters"
    if any(x in low for x in ("form", "input", "select", "editor")):
        return "form"
    if any(x in low for x in ("table", "list", "grid", "catalog")):
        return "content"
    if any(x in low for x in ("modal", "drawer", "popover", "tooltip", "overlay")):
        return "overlay"
    if any(x in low for x in ("toast", "alert", "error", "success", "warning")):
        return "feedback"
    return "main"


def route_surface_slug(route_path: str) -> str:
    route = route_path.strip("/")
    if not route:
        return "home"
    if route.startswith("pos"):
        return "pos"
    first = route.split("/")[0]
    return slug(first)


def extract_text_hint(attrs: str, body_hint: str = "") -> str:
    for key in ("aria-label", "title", "name", "id", "data-testid", "data-prisma-id"):
        match = re.search(rf"{re.escape(key)}\s*=\s*[\"']([^\"']+)[\"']", attrs)
        if match:
            return match.group(1)
    text = re.sub(r"\{[^}]*\}", " ", body_hint)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:80]


def extract_data_attributes(attrs: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for match in re.finditer(r"\b(data-[A-Za-z0-9_-]+)\s*=\s*(?:[\"']([^\"']*)[\"']|\{([^}]*)\})", attrs):
        out[match.group(1)] = (match.group(2) or match.group(3) or "").strip()
    return out


def extract_class_names(attrs: str) -> list[str]:
    classes: list[str] = []
    for match in re.finditer(r"styles\.([A-Za-z_][A-Za-z0-9_]*)", attrs):
        if match.group(1) not in classes:
            classes.append(match.group(1))
    for match in re.finditer(r"className\s*=\s*[\"']([^\"']+)[\"']", attrs):
        for item in re.split(r"\s+", match.group(1).strip()):
            if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*$", item) and item not in classes:
                classes.append(item)
    return classes


def repeated_by_data(text: str, position: int) -> bool:
    window = text[max(0, position - 500) : position]
    return bool(re.search(r"\.(?:map|flatMap)\s*\(", window) or re.search(r"for\s*\(", window))


def _candidate_routes(
    runtime_alias: str,
    rel: str,
    source_hash: str,
    routes_for_file: list[RouteRecord],
) -> list[RouteRecord]:
    if not routes_for_file:
        return [RouteRecord(
            runtime_alias=runtime_alias,
            route_id=stable_id("ROUTE", runtime_alias, "unrouted"),
            route_path="/",
            source_file=rel,
            source_hash=source_hash,
            kind="unrouted",
        )]

    kind_priority = {
        "page": 0, "screen": 0, "layout": 1, "template": 2,
        "loading": 3, "error_boundary": 4, "global_error_boundary": 5,
        "not_found_boundary": 6, "parallel_route_default": 7, "api_route": 8,
    }
    ordered = sorted(
        routes_for_file,
        key=lambda route: (
            route.route_path,
            route.route_id,
            kind_priority.get(route.kind, 50),
            route.source_file,
        ),
    )
    by_identity: dict[tuple[str, str], RouteRecord] = {}
    for route in ordered:
        by_identity.setdefault((route.route_id, route.route_path), route)
    return [
        by_identity[key]
        for key in sorted(by_identity, key=lambda item: (item[1], item[0]))
    ]


def extract_ui_candidates_from_file(
    runtime_alias: str,
    path: Path,
    product_root: Path,
    routes_for_file: list[RouteRecord],
    source_hash: str,
) -> list[UiCandidate]:
    text = read_text(path)
    rel = norm_rel(product_root, path)
    symbols = extract_export_symbols(text, path.stem)
    owner_symbol = symbols[0]
    routes = _candidate_routes(runtime_alias, rel, source_hash, routes_for_file)
    tag_pattern = re.compile(r"<([A-Za-z][A-Za-z0-9_.:-]*)(\s[^<>]*?)?\s*/?>", flags=re.MULTILINE | re.DOTALL)
    tag_matches = list(tag_pattern.finditer(text))
    style_matches = list(re.finditer(r"styles\.([A-Za-z_][A-Za-z0-9_]*)", text))
    candidates: list[UiCandidate] = []

    for route in routes:
        route_candidates: list[UiCandidate] = []
        for match in tag_matches:
            tag = match.group(1)
            attrs = match.group(2) or ""
            if tag.lower() in {"fragment", "react.fragment"}:
                continue
            classes = extract_class_names(attrs)
            data_attrs = extract_data_attributes(attrs)
            is_native_visual = tag.lower() in HTML_WIDGETS
            is_component = tag[0].isupper()
            if not classes and not data_attrs and not is_native_visual and not is_component:
                continue
            if not classes:
                classes = [None]
            for class_name in classes:
                widget_kind = infer_widget_kind(tag, class_name, owner_symbol, attrs)
                route_candidates.append(UiCandidate(
                    runtime_alias=runtime_alias,
                    route_path=route.route_path,
                    route_id=route.route_id,
                    route_source_file=route.source_file,
                    render_source_file=rel,
                    render_symbol=owner_symbol,
                    owner_file=rel,
                    owner_symbol=owner_symbol,
                    class_name=class_name,
                    tag_name=tag,
                    widget_kind=widget_kind,
                    text_hint=extract_text_hint(attrs),
                    instance_policy="REPEATED_BY_DATA" if repeated_by_data(text, match.start()) else "SINGLE_OR_STATIC",
                    data_attributes=data_attrs,
                    source_hash=source_hash,
                    generated_projection="generated" in rel.lower() or "/dist/" in f"/{rel.lower()}/",
                ))

        # CSS-only fallback fills classes not already observed on a real JSX element.
        # JSX candidates can carry data-prisma-* evidence; a later fallback must
        # never compete with or erase that richer source observation.
        seen_class_keys = {
            (c.class_name, c.render_source_file)
            for c in route_candidates
            if c.class_name
        }
        for match in style_matches:
            class_name = match.group(1)
            if (class_name, rel) in seen_class_keys:
                continue
            route_candidates.append(UiCandidate(
                runtime_alias=runtime_alias,
                route_path=route.route_path,
                route_id=route.route_id,
                route_source_file=route.source_file,
                render_source_file=rel,
                render_symbol=owner_symbol,
                owner_file=rel,
                owner_symbol=owner_symbol,
                class_name=class_name,
                tag_name="styled-slot",
                widget_kind=infer_widget_kind("styled-slot", class_name, owner_symbol),
                text_hint=class_name,
                instance_policy="REPEATED_BY_DATA" if repeated_by_data(text, match.start()) else "SINGLE_OR_STATIC",
                data_attributes={},
                source_hash=source_hash,
                generated_projection="generated" in rel.lower(),
            ))
        candidates.extend(route_candidates)

    # Keep distinct real JSX identities when their governed data-prisma-* markers
    # differ. Ordinary runtime data-* values are intentionally excluded so state
    # variants of the same governed component do not multiply the map.
    dedupe: dict[tuple[Any, ...], UiCandidate] = {}
    for candidate in candidates:
        prisma_fingerprint = tuple(sorted(
            (key, value)
            for key, value in candidate.data_attributes.items()
            if key.startswith("data-prisma-")
        ))
        key = (
            candidate.render_source_file,
            candidate.class_name or candidate.tag_name,
            candidate.route_path,
            candidate.route_id,
            candidate.widget_kind,
            prisma_fingerprint,
        )
        existing = dedupe.get(key)
        if existing is None:
            dedupe[key] = candidate
            continue
        existing_prisma = tuple(sorted(
            (attr, value)
            for attr, value in existing.data_attributes.items()
            if attr.startswith("data-prisma-")
        ))
        candidate_score = (
            len(prisma_fingerprint),
            len(candidate.data_attributes),
            candidate.tag_name != "styled-slot",
        )
        existing_score = (
            len(existing_prisma),
            len(existing.data_attributes),
            existing.tag_name != "styled-slot",
        )
        if candidate_score > existing_score:
            dedupe[key] = candidate
    return [dedupe[key] for key in sorted(dedupe)]


def discover_runtime(
    runtime_alias: str,
    root: Path,
    product_root: Path,
    workers: int = 18,
) -> dict[str, Any]:
    files = sorted(iter_files(root), key=lambda p: str(p).lower())
    hashes = parallel_hash(files, workers=workers)
    routes = discover_routes(runtime_alias, root, product_root, hashes)
    reach = build_route_reachability(root, product_root, routes)
    css_targets: list[CssTarget] = []
    source_paths = [p for p in files if p.suffix.lower() in SOURCE_EXTS]
    style_paths = [p for p in files if p.suffix.lower() in STYLE_EXTS]
    with ThreadPoolExecutor(max_workers=max(1, min(18, workers))) as pool:
        futures = {
            pool.submit(extract_css_targets, p, product_root, hashes.get(p, "")): p for p in style_paths
        }
        for future in as_completed(futures):
            try:
                css_targets.extend(future.result())
            except Exception:
                pass
    candidates: list[UiCandidate] = []
    with ThreadPoolExecutor(max_workers=max(1, min(18, workers))) as pool:
        futures = {}
        for path in source_paths:
            rel = norm_rel(product_root, path)
            futures[pool.submit(
                extract_ui_candidates_from_file,
                runtime_alias,
                path,
                product_root,
                reach.get(rel, []),
                hashes.get(path, ""),
            )] = path
        for future in as_completed(futures):
            try:
                candidates.extend(future.result())
            except Exception:
                pass
    return {
        "runtimeAlias": runtime_alias,
        "runtimeLabel": RUNTIME_LABELS[runtime_alias],
        "root": norm_rel(product_root, root),
        "routes": sorted(routes, key=lambda r: (r.route_path, r.source_file)),
        "cssTargets": sorted(css_targets, key=lambda t: (t.class_name, t.source_file, t.selector, t.state_selector)),
        "candidates": sorted(candidates, key=lambda c: (c.route_path, c.render_source_file, c.class_name or "", c.tag_name)),
        "files": files,
        "hashes": hashes,
    }


def load_json_files(roots: Iterable[Path], name_patterns: tuple[str, ...], max_size: int = 12_000_000) -> list[tuple[Path, Any]]:
    found: list[tuple[Path, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            if excluded(path) or path.stat().st_size > max_size:
                continue
            low = path.name.lower()
            if name_patterns and not any(pattern in low for pattern in name_patterns):
                continue
            try:
                found.append((path, json.loads(read_text(path))))
            except Exception:
                continue
    return found


def walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def build_authority_indexes(product_root: Path, governor_root: Path) -> dict[str, Any]:
    layer_files = load_json_files(
        [product_root, governor_root],
        ("layers", "layer-certification", "layer_map", "layers_map"),
    )
    binding_files = load_json_files(
        [product_root, governor_root],
        ("binding", "identity-layer-certifications", "visual-stack", "recipe"),
    )
    layers_by_selector: dict[str, list[dict[str, Any]]] = {}
    layers_by_impl: dict[str, list[dict[str, Any]]] = {}
    for path, payload in layer_files:
        for item in walk_dicts(payload):
            selector = item.get("selector") or item.get("anchorValue")
            layer_id = item.get("layerId") or item.get("layer_id")
            implementation = item.get("implementationLayerId") or item.get("expectedImplementationLayerId")
            if selector and (layer_id or implementation):
                row = {
                    "selector": str(selector),
                    "layerId": layer_id,
                    "implementationLayerId": implementation,
                    "sourceFile": norm_rel(governor_root if str(path).startswith(str(governor_root)) else product_root, path),
                    "sourceHash": sha256_file(path),
                    "raw": item,
                }
                layers_by_selector.setdefault(str(selector), []).append(row)
                if implementation:
                    layers_by_impl.setdefault(str(implementation), []).append(row)
    bindings_by_selector: dict[str, list[dict[str, Any]]] = {}
    for path, payload in binding_files:
        for item in walk_dicts(payload):
            selector = item.get("selector") or (item.get("trace") or {}).get("selector")
            binding_id = item.get("bindingId") or (item.get("bindingRequirements") or {}).get("bindingId")
            if selector and binding_id:
                row = {
                    "selector": str(selector),
                    "bindingId": str(binding_id),
                    "sourceFile": norm_rel(governor_root if str(path).startswith(str(governor_root)) else product_root, path),
                    "sourceHash": sha256_file(path),
                    "raw": item,
                }
                bindings_by_selector.setdefault(str(selector), []).append(row)
    return {
        "layersBySelector": layers_by_selector,
        "layersByImplementation": layers_by_impl,
        "bindingsBySelector": bindings_by_selector,
        "layerFiles": [str(p) for p, _ in layer_files],
        "bindingFiles": [str(p) for p, _ in binding_files],
    }


def css_target_index(targets: list[CssTarget]) -> dict[str, list[CssTarget]]:
    index: dict[str, list[CssTarget]] = {}
    for target in targets:
        index.setdefault(target.class_name, []).append(target)
    return index


def make_state_support(targets: list[CssTarget], runtime_alias: str) -> dict[str, str]:
    defined = {target.state_selector for target in targets}
    support: dict[str, str] = {}
    for state in REQUIRED_STATES:
        if state in defined:
            support[state] = "SOURCE_DEFINED"
        elif state == "hover" and runtime_alias in {"tb", "mb"} and "pressed" in defined:
            support[state] = "NOT_APPLICABLE"
        elif state == "default":
            support[state] = "SOURCE_DEFINED" if targets else "OWNER_INHERITED"
        else:
            support[state] = "MISSING_REQUIRED"
    for state in CONDITIONAL_STATES:
        support[state] = "SOURCE_DEFINED" if state in defined else "NOT_APPLICABLE"
    return support


def widget_type_id(kind: str) -> str:
    return stable_id("WID", kind)


def component_locator(
    runtime_alias: str,
    route_path: str,
    region: str,
    element: str,
    kind: str,
    ordinal: int,
    owner_identity: str | None = None,
) -> str:
    route_identity = slug(route_path.strip("/") or "home")
    surface = upper_token(route_identity, "HOME", 64)
    zone = upper_token(region, "MAIN", 12)
    owner = upper_token(owner_identity or "owner", "OWNER", 160)
    item = upper_token(element, "ITEM", 24)
    suffix = WIDGET_TYPE_SUFFIX.get(kind, "CTL")
    return f"{runtime_alias.upper()}-{surface}-{zone}-{owner}-{item}-{suffix}-{ordinal:02d}"


def source_snapshot_hash(file_hashes: dict[str, str]) -> str:
    payload = {key: file_hashes[key] for key in sorted(file_hashes)}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest().upper()
