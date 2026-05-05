from __future__ import annotations

import ast
import re
from pathlib import Path, PurePosixPath
from typing import Any

from pya.system.canon_policy import classify_source_path

TEXT_KINDS = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".json": "json",
    ".html": "html",
    ".css": "css",
    ".md": "markdown",
}

INTERESTING_SURFACE_KINDS = {
    "module",
    "entrypoint",
    "route_surface",
    "screen",
    "component",
    "desktop_bridge",
    "module_config",
}

IMPORT_RE = re.compile(r'''(?:import\s+(?:[\w*{}, ]+\s+from\s+)?|export\s+[^;]*?from\s+|require\()\s*['"]([^'"]+)['"]''')
ROUTE_RE = re.compile(r'''path\s*[=:]\s*['"]([^'"]+)['"]''')


def classify_file(relative_path: str) -> str:
    suffix = Path(relative_path).suffix.lower()
    return TEXT_KINDS.get(suffix, "other")


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def strip_all_suffixes(relative_path: str) -> str:
    pure = PurePosixPath(relative_path)
    base = pure.as_posix()
    for suffix in pure.suffixes:
        if suffix and base.endswith(suffix):
            base = base[: -len(suffix)]
    return base


def surface_module_name(relative_path: str) -> str:
    base = strip_all_suffixes(relative_path).replace("/", ".")
    base = re.sub(r"[^0-9A-Za-z_.]+", "_", base)
    base = re.sub(r"\.+", ".", base).strip(".")
    return base or "root"


def detect_surface_kind(relative_path: str, text: str) -> str:
    lower_path = relative_path.lower()
    filename = Path(relative_path).name.lower()
    if lower_path.endswith("modules.config.json"):
        return "module_config"
    if "/routes/" in lower_path or "router" in filename or lower_path.endswith("routes/register.ts"):
        return "route_surface"
    if "/pages/" in lower_path:
        return "screen"
    if "/components/" in lower_path:
        return "component"
    if filename == "main.tsx":
        return "entrypoint"
    if "bridge" in filename or "qwebchannel" in text.lower():
        return "desktop_bridge"
    if lower_path.endswith(".css"):
        return "style_asset"
    if lower_path.endswith(".html"):
        return "html_asset"
    if lower_path.endswith(".json"):
        return "json_asset"
    if lower_path.endswith((".ts", ".tsx", ".js", ".jsx")):
        return "module"
    if lower_path.endswith(".py"):
        return "python_module"
    if lower_path.endswith(".md"):
        return "markdown_asset"
    return "other_asset"


def detect_tags(text: str, relative_path: str, surface_kind: str) -> list[str]:
    tags: set[str] = set()
    low = text.lower()
    rel_low = relative_path.lower()
    if surface_kind in {"route_surface", "entrypoint"} or "react-router-dom" in low or " path:" in low or "path=" in low:
        tags.add("route-aware")
    if "modules.config.json" in rel_low:
        tags.add("registry-config")
    if "modules.registry" in rel_low or "loadregistry" in low or "moduledef" in low:
        tags.add("schema-driven")
    if "bridge" in rel_low or "qwebchannel" in low or "sendtodesktop" in low:
        tags.add("backend-driven")
        tags.add("desktop-bridge")
    if "i18n" in low or "translate" in low or "translations" in low or "locale" in low:
        tags.add("i18n-boundary")
    if "/pages/" in rel_low:
        tags.add("screen")
    if "/components/" in rel_low:
        tags.add("widget")
    if "math.random" in low or "date.now" in low:
        tags.add("nondeterministic-demo")
    return sorted(tags)


def detect_boundary_kinds(text: str, relative_path: str) -> list[str]:
    rel_low = relative_path.lower()
    low = text.lower()
    kinds: list[str] = []
    if rel_low.endswith("src/main.tsx"):
        kinds.append("runtime_entry")
    if rel_low.endswith("routes/register.ts"):
        kinds.append("route_registration")
    if rel_low.endswith("modules.registry.ts"):
        kinds.append("module_registry_contract")
    if "hitechbridge.ts" in rel_low or "qwebchannel" in low:
        kinds.append("desktop_bridge_boundary")
    if "modules.config.json" in rel_low:
        kinds.append("public_registry_boundary")
    if "i18n" in low:
        kinds.append("i18n_boundary")
    return kinds


def extract_text_imports(text: str) -> list[str]:
    values = []
    for value in IMPORT_RE.findall(text):
        candidate = value.strip()
        if candidate:
            values.append(candidate)
    return sorted(set(values))


def extract_routes(text: str) -> list[str]:
    values = []
    for value in ROUTE_RE.findall(text):
        candidate = value.strip()
        if candidate:
            values.append(candidate)
    return sorted(set(values))


def parse_python_file(path: Path) -> dict[str, Any]:
    source = read_text_file(path)
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {
            "ok": False,
            "imports": [],
            "exports": [],
            "error": {
                "message": exc.msg,
                "lineno": exc.lineno,
                "offset": exc.offset,
            },
        }

    imports: list[str] = []
    exports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level + (node.module or "")
            imports.append(prefix)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and getattr(node, "col_offset", 1) == 0:
            exports.append(node.name)
        elif isinstance(node, ast.Assign) and getattr(node, "col_offset", 1) == 0:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    try:
                        value = ast.literal_eval(node.value)
                    except Exception:
                        continue
                    if isinstance(value, (list, tuple)):
                        exports.extend(str(item) for item in value)

    return {
        "ok": True,
        "imports": sorted(set(imports)),
        "exports": sorted(set(exports)),
        "error": None,
    }


def parse_text_surface(path: Path, relative_path: str) -> dict[str, Any]:
    text = read_text_file(path)
    surface_kind = detect_surface_kind(relative_path, text)
    tags = detect_tags(text, relative_path, surface_kind)
    path_policy = classify_source_path(relative_path)
    canonical_source = path_policy.canonical_source
    boundaries = detect_boundary_kinds(text, relative_path) if canonical_source else []
    routes = extract_routes(text) if canonical_source else []
    imports = extract_text_imports(text) if canonical_source else []
    should_emit_module_candidate = canonical_source and surface_kind in INTERESTING_SURFACE_KINDS
    return {
        "ok": True,
        "text": text,
        "surface_kind": surface_kind,
        "tags": tags,
        "boundaries": boundaries,
        "routes": routes,
        "imports": imports,
        "canonical_source": canonical_source,
        "non_product_class": path_policy.non_product_class,
        "module_name": surface_module_name(relative_path),
        "should_emit_module_candidate": should_emit_module_candidate,
    }
