from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .graph import sort_ui_dictionary
from .ids import asset_id, component_id, hotspot_id, route_id, state_id, style_id
from .io_utils import list_files, read_text, relpath

TS_EXTS = {".ts", ".tsx", ".js", ".jsx"}
STYLE_EXTS = {".css"}
ASSET_EXTS = {".svg", ".png"}
ALL_EXTS = TS_EXTS | STYLE_EXTS | ASSET_EXTS

IMPORT_FROM_RE = re.compile(r"import\s+(?P<clause>[\s\S]*?)\s+from\s+[\"'](?P<source>[^\"']+)[\"']\s*;?", re.MULTILINE)
IMPORT_SIDE_RE = re.compile(r"import\s+[\"'](?P<source>[^\"']+)[\"']\s*;?", re.MULTILINE)
EXPORT_DECL_RE = re.compile(r"export\s+(?:async\s+)?(?:function|const|let|var|class)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
EXPORT_DEFAULT_RE = re.compile(r"export\s+default\s+(?:async\s+)?(?:function|class|[A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
EXPORT_LIST_RE = re.compile(r"export\s*\{(?P<body>[^}]+)\}(?:\s*from\s*[\"'](?P<source>[^\"']+)[\"'])?\s*;?", re.MULTILINE)
EXPORT_STAR_RE = re.compile(r"export\s*\*\s*from\s*[\"'](?P<source>[^\"']+)[\"']", re.MULTILINE)
JSX_TAG_RE = re.compile(r"<(?P<tag>[A-Z][A-Za-z0-9_]*(?:\.[A-Z][A-Za-z0-9_]*)?)\b")
HOOK_RE = re.compile(r"\b(?P<hook>use[A-Z][A-Za-z0-9_]*)\s*\(")
STORE_RE = re.compile(r"\b(?P<token>[A-Za-z_][A-Za-z0-9_]*(?:Store|store|State|state))\b")
WRITER_RE = re.compile(r"\b(set[A-Z][A-Za-z0-9_]*|dispatch|advance|reset|cycle[A-Za-z0-9_]*|force[A-Za-z0-9_]*|toggle[A-Za-z0-9_]*|update[A-Za-z0-9_]*)\b")
URL_RE = re.compile(r"url\((?P<url>[^)]+)\)")
EVENT_RE = re.compile(r"\b(?P<name>[a-z][A-Za-z0-9_]*)\s*:\s*\(")


@dataclass
class ImportItem:
    source_spec: str
    source_file: str | None
    default_name: str | None
    namespace_name: str | None
    named: list[tuple[str, str]]


def _norm(path: str) -> str:
    raw = path.replace("\\", "/")
    while "//" in raw:
        raw = raw.replace("//", "/")
    parts: list[str] = []
    for token in raw.split("/"):
        if token in {"", "."}:
            continue
        if token == "..":
            if parts:
                parts.pop()
            continue
        parts.append(token)
    return "/".join(parts)


def _is_external(spec: str) -> bool:
    if spec.startswith("."):
        return False
    if spec.startswith("@/") or spec.startswith("@hitech/ui-kit") or spec.startswith("@hitech/keystone"):
        return False
    return True


def _candidate_paths(stem: str) -> list[str]:
    base = _norm(stem)
    ext = Path(base).suffix.lower()
    candidates: list[str] = [base]
    if ext == ".js":
        candidates.extend([base[:-3] + ".ts", base[:-3] + ".tsx"])
    if ext == ".jsx":
        candidates.extend([base[:-4] + ".tsx", base[:-4] + ".ts"])
    if ext == "":
        for suffix in [".ts", ".tsx", ".js", ".jsx", ".css", ".svg", ".png"]:
            candidates.append(base + suffix)
    for suffix in ["index.ts", "index.tsx", "index.js", "index.jsx", "index.css"]:
        candidates.append(base.rstrip("/") + "/" + suffix)
    deduped: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _resolve_alias(current_file: str, spec: str) -> str:
    if spec.startswith("./") or spec.startswith("../"):
        return _norm((Path(current_file).parent / spec).as_posix())
    if spec.startswith("@/"):
        return _norm((Path("apps/keystone") / spec[2:]).as_posix())
    if spec.startswith("@hitech/ui-kit"):
        suffix = spec[len("@hitech/ui-kit") :].lstrip("/")
        return _norm((Path("packages/ui-kit/src") / suffix).as_posix()) if suffix else "packages/ui-kit/src/index.ts"
    if spec.startswith("@hitech/keystone"):
        suffix = spec[len("@hitech/keystone") :].lstrip("/")
        return _norm((Path("apps/keystone") / suffix).as_posix()) if suffix else "apps/keystone/app/page.tsx"
    return spec


def _resolve_source(current_file: str, spec: str, file_lookup: set[str]) -> str | None:
    if _is_external(spec):
        return None
    stem = _resolve_alias(current_file, spec)
    for candidate in _candidate_paths(stem):
        if candidate in file_lookup:
            return candidate
    return None


def _parse_named(body: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for part in body.split(","):
        token = part.strip()
        if not token:
            continue
        if token.startswith("type "):
            token = token[5:].strip()
        if " as " in token:
            imported, local = [p.strip() for p in token.split(" as ", 1)]
        else:
            imported = token
            local = token
        items.append((imported, local))
    return items


def _parse_clause(clause: str) -> tuple[str | None, str | None, list[tuple[str, str]]]:
    text = " ".join(clause.replace("\n", " ").split())
    default_name: str | None = None
    namespace_name: str | None = None
    named: list[tuple[str, str]] = []
    if text.startswith("type "):
        text = text[5:].strip()
    if text.startswith("{") and text.endswith("}"):
        named = _parse_named(text[1:-1])
    elif text.startswith("* as "):
        namespace_name = text[5:].strip()
    elif "," in text:
        first, rest = [p.strip() for p in text.split(",", 1)]
        if first and not first.startswith("{") and not first.startswith("*"):
            default_name = first
        remainder = rest
        if remainder.startswith("{") and remainder.endswith("}"):
            named = _parse_named(remainder[1:-1])
        elif remainder.startswith("* as "):
            namespace_name = remainder[5:].strip()
        elif remainder:
            default_name = default_name or remainder
    elif text and default_name is None and not text.startswith("{"):
        default_name = text
    return default_name, namespace_name, named

def _parse_imports(content: str, current_file: str, file_lookup: set[str]) -> list[ImportItem]:
    items: list[ImportItem] = []
    for match in IMPORT_FROM_RE.finditer(content):
        spec = match.group("source")
        resolved = _resolve_source(current_file, spec, file_lookup)
        default_name, namespace_name, named = _parse_clause(match.group("clause").strip())
        items.append(
            ImportItem(
                source_spec=spec,
                source_file=resolved,
                default_name=default_name,
                namespace_name=namespace_name,
                named=named,
            )
        )
    for match in IMPORT_SIDE_RE.finditer(content):
        spec = match.group("source")
        resolved = _resolve_source(current_file, spec, file_lookup)
        if any(item.source_spec == spec and item.source_file == resolved for item in items):
            continue
        items.append(ImportItem(source_spec=spec, source_file=resolved, default_name=None, namespace_name=None, named=[]))
    return items


def _parse_exports(content: str, current_file: str, file_lookup: set[str]) -> tuple[set[str], list[tuple[str, str, str]], list[str]]:
    local_exports: set[str] = set()
    explicit: list[tuple[str, str, str]] = []
    stars: list[str] = []
    if EXPORT_DEFAULT_RE.search(content):
        local_exports.add("default")
    for match in EXPORT_DECL_RE.finditer(content):
        local_exports.add(match.group("name"))
    for match in EXPORT_LIST_RE.finditer(content):
        source = match.group("source")
        named_items = _parse_named(match.group("body"))
        if source:
            target = _resolve_source(current_file, source, file_lookup)
            if not target:
                continue
            for imported, alias in named_items:
                explicit.append((alias, target, imported))
        else:
            for _, alias in named_items:
                local_exports.add(alias)
    for match in EXPORT_STAR_RE.finditer(content):
        target = _resolve_source(current_file, match.group("source"), file_lookup)
        if target:
            stars.append(target)
    return local_exports, explicit, stars


def _classify_component(file_path: str, export_name: str) -> str:
    path = file_path.lower()
    name = export_name.lower()
    if path.startswith("apps/keystone/app/") and path.endswith("/page.tsx"):
        return "route"
    if "/screen-" in path or "/screens/" in path:
        return "screen"
    if "layout" in path:
        return "layout"
    if "/nav/" in path or "-nav" in path:
        return "nav"
    if "/brand/" in path or "brand" in path:
        return "brand"
    if "store" in path or "state" in path or name.endswith("store"):
        return "state"
    if any(token in path for token in ["sparkline", "gauge", "meter", "chart", "visual", "bars"]):
        return "dataviz"
    if any(token in path for token in ["control", "panel", "toggle", "slider", "dropdown", "button"]):
        return "control"
    return "block"


def _route_path_from_file(file_path: str) -> str:
    parts = list(Path(file_path).parts)
    try:
        app_idx = parts.index("app")
    except ValueError:
        return "/"
    route_parts = parts[app_idx + 1 : -1]
    return "/" + "/".join(route_parts) if route_parts else "/"


def _collect_layout(route_file: str, file_lookup: set[str]) -> str | None:
    current = Path(route_file).parent
    root = Path("apps/keystone/app")
    while True:
        candidate = _norm((current / "layout.tsx").as_posix())
        if candidate in file_lookup:
            return candidate
        if current == root or current.parent == current:
            return None
        current = current.parent


def _owners(file_to_components: dict[str, list[str]], file_path: str) -> list[str]:
    values = list(file_to_components.get(file_path, []))
    values.sort()
    return values


def _components_matching(components: list[dict[str, Any]], tokens: list[str]) -> list[str]:
    hits: set[str] = set()
    for component in components:
        path = component["file_path"].lower()
        if any(token.lower() in path for token in tokens):
            hits.add(component["component_id"])
    return sorted(hits)

def analyze_repository(repo_root: Path) -> dict[str, Any]:
    searched = ["apps/keystone/**", "packages/ui-kit/**"]
    targets = [repo_root / "apps" / "keystone", repo_root / "packages" / "ui-kit"]

    all_files: list[Path] = []
    for target in targets:
        if target.exists():
            all_files.extend(list_files(target, ALL_EXTS))
    all_files = sorted(set(path.resolve() for path in all_files), key=lambda item: item.as_posix().lower())

    rel_files = [relpath(path, repo_root) for path in all_files]
    file_lookup = set(rel_files)

    module_files = [file_path for file_path in rel_files if Path(file_path).suffix.lower() in TS_EXTS]
    module_files.sort()

    module_data: dict[str, dict[str, Any]] = {}
    explicit_reexports: dict[str, list[tuple[str, str, str]]] = {}
    star_reexports: dict[str, list[str]] = {}
    local_exports: dict[str, set[str]] = {}

    for file_path in module_files:
        content = read_text(repo_root / file_path)
        imports = _parse_imports(content, file_path, file_lookup)
        local, explicit, stars = _parse_exports(content, file_path, file_lookup)
        module_data[file_path] = {
            "content": content,
            "imports": imports,
            "jsx_tags": {m.group("tag") for m in JSX_TAG_RE.finditer(content)},
            "hooks": {m.group("hook") for m in HOOK_RE.finditer(content)},
            "stores": {m.group("token") for m in STORE_RE.finditer(content)},
            "css_imports": sorted({item.source_file for item in imports if item.source_file and Path(item.source_file).suffix.lower() in STYLE_EXTS}),
            "asset_imports": sorted({item.source_file for item in imports if item.source_file and Path(item.source_file).suffix.lower() in ASSET_EXTS}),
        }
        explicit_reexports[file_path] = explicit
        star_reexports[file_path] = stars
        local_exports[file_path] = local

    export_cache: dict[tuple[str, str], tuple[str, str] | None] = {}

    def resolve_export(module_file: str, export_name: str, stack: set[tuple[str, str]] | None = None) -> tuple[str, str] | None:
        key = (module_file, export_name)
        if key in export_cache:
            return export_cache[key]
        trail = stack or set()
        if key in trail:
            export_cache[key] = None
            return None
        trail.add(key)
        if export_name in local_exports.get(module_file, set()):
            export_cache[key] = (module_file, export_name)
            return export_cache[key]
        for alias, target_file, target_export in explicit_reexports.get(module_file, []):
            if alias != export_name:
                continue
            resolved = resolve_export(target_file, target_export, trail)
            export_cache[key] = resolved if resolved else (target_file, target_export)
            return export_cache[key]
        for target_file in star_reexports.get(module_file, []):
            resolved = resolve_export(target_file, export_name, trail)
            if resolved:
                export_cache[key] = resolved
                return resolved
        export_cache[key] = None
        return None

    components: list[dict[str, Any]] = []
    component_by_export: dict[tuple[str, str], str] = {}
    file_to_components: dict[str, list[str]] = {}

    for file_path in module_files:
        exports = sorted(local_exports.get(file_path, set()))
        if not exports:
            continue
        for export_name in exports:
            cid = component_id(file_path, export_name)
            record = {
                "component_id": cid,
                "export_name": export_name,
                "file_path": file_path,
                "kind": _classify_component(file_path, export_name),
                "imports": sorted({entry.source_file for entry in module_data[file_path]["imports"] if entry.source_file}),
                "renders": [],
                "uses": {
                    "hooks": sorted(module_data[file_path]["hooks"]),
                    "stores": sorted(module_data[file_path]["stores"]),
                    "css": list(module_data[file_path]["css_imports"]),
                    "assets": list(module_data[file_path]["asset_imports"]),
                },
            }
            components.append(record)
            component_by_export[(file_path, export_name)] = cid
            file_to_components.setdefault(file_path, []).append(cid)

    for values in file_to_components.values():
        values.sort()

    component_index = {item["component_id"]: item for item in components}
    edge_set: set[tuple[str, str, str, str | None]] = set()

    def add_edge(from_id: str, to_id: str, edge_type: str, notes: str | None = None) -> None:
        edge_set.add((from_id, to_id, edge_type, notes))

    def resolve_target(source_file: str, export_name: str) -> str | None:
        resolved = resolve_export(source_file, export_name)
        if not resolved:
            return None
        return component_by_export.get(resolved)

    for file_path in module_files:
        owners = _owners(file_to_components, file_path)
        if not owners:
            continue
        imports = module_data[file_path]["imports"]
        tags = module_data[file_path]["jsx_tags"]
        import_targets: set[str] = set()
        render_targets: set[str] = set()
        for entry in imports:
            if not entry.source_file:
                continue
            if entry.default_name:
                target = resolve_target(entry.source_file, "default")
                if target:
                    import_targets.add(target)
                    if entry.default_name in tags:
                        render_targets.add(target)
            for imported_name, local_name in entry.named:
                target = resolve_target(entry.source_file, imported_name)
                if target:
                    import_targets.add(target)
                    if local_name in tags:
                        render_targets.add(target)
            if entry.namespace_name:
                prefix = f"{entry.namespace_name}."
                for tag in tags:
                    if not tag.startswith(prefix):
                        continue
                    member = tag.split(".", 1)[1]
                    target = resolve_target(entry.source_file, member)
                    if target:
                        import_targets.add(target)
                        render_targets.add(target)
        for owner in owners:
            for target in sorted(import_targets):
                add_edge(owner, target, "imports")
            component_index[owner]["renders"] = sorted(set(component_index[owner]["renders"]) | render_targets)
            for target in sorted(render_targets):
                add_edge(owner, target, "renders")

    state_files = [
        file_path
        for file_path in module_files
        if "store" in file_path.lower() or "state" in file_path.lower() or ("zustand" in module_data[file_path]["content"] and "create(" in module_data[file_path]["content"])
    ]
    state_files.sort()

    states: list[dict[str, Any]] = []
    for state_file in state_files:
        readers: set[str] = set()
        writers: set[str] = set()
        for importer in module_files:
            if importer == state_file:
                continue
            entries = [entry for entry in module_data[importer]["imports"] if entry.source_file == state_file]
            if not entries:
                continue
            aliases: list[str] = []
            for entry in entries:
                if entry.default_name:
                    aliases.append(entry.default_name)
                aliases.extend(local for _, local in entry.named)
            called = any(re.search(rf"\b{re.escape(alias)}\s*\(", module_data[importer]["content"]) for alias in aliases)
            owners = _owners(file_to_components, importer)
            if called:
                readers.update(owners)
                if WRITER_RE.search(module_data[importer]["content"]):
                    writers.update(owners)
        writer_anchor = sorted(writers)[0] if writers else (sorted(readers)[0] if readers else "")
        events: list[dict[str, Any]] = []
        seen: set[str] = set()
        for match in EVENT_RE.finditer(module_data[state_file]["content"]):
            name = match.group("name")
            if name in {"if", "for", "while", "return", "switch"} or name in seen:
                continue
            seen.add(name)
            events.append({"name": name, "writer_component_id": writer_anchor, "notes": "heuristic event extraction"})
        note: str | None = None
        content = module_data[state_file]["content"]
        if "Date.now(" in content:
            note = "contains Date.now usage; review deterministic assumptions"
        elif "new Date(" in content and "BASE_TS" not in content:
            note = "contains runtime date construction; review deterministic assumptions"
        elif "BASE_TS" in content:
            note = "uses deterministic BASE_TS sequence"
        record: dict[str, Any] = {
            "state_id": state_id(state_file),
            "file_path": state_file,
            "readers": sorted(readers),
            "writers": sorted(writers),
            "events": events,
        }
        if note:
            record["determinism_notes"] = note
        states.append(record)
        for reader in sorted(readers):
            add_edge(reader, record["state_id"], "reads")
        for writer in sorted(writers):
            add_edge(writer, record["state_id"], "writes")

    style_files = sorted([file_path for file_path in rel_files if Path(file_path).suffix.lower() in STYLE_EXTS])
    style_refs: dict[str, set[str]] = {file_path: set() for file_path in style_files}
    for file_path in module_files:
        owners = _owners(file_to_components, file_path)
        if not owners:
            continue
        for style_file in module_data[file_path]["css_imports"]:
            if style_file in style_refs:
                style_refs[style_file].update(owners)

    styles: list[dict[str, Any]] = []
    for style_file in style_files:
        sid = style_id(style_file)
        refs = sorted(style_refs[style_file])
        styles.append({"style_id": sid, "file_path": style_file, "referenced_by": refs})
        for cid in refs:
            add_edge(cid, sid, "uses_style")

    direct_assets: dict[str, set[str]] = {}
    css_assets: dict[str, set[str]] = {}
    for file_path in module_files:
        owners = _owners(file_to_components, file_path)
        if not owners:
            continue
        for asset_file in module_data[file_path]["asset_imports"]:
            direct_assets.setdefault(asset_file, set()).update(owners)

    for style_file in style_files:
        content = read_text(repo_root / style_file)
        for match in URL_RE.finditer(content):
            raw = match.group("url").strip().strip("\"\'")
            if raw.startswith("data:") or "://" in raw or raw.startswith("/"):
                continue
            resolved = _resolve_source(style_file, raw, file_lookup)
            if resolved and Path(resolved).suffix.lower() in ASSET_EXTS:
                css_assets.setdefault(resolved, set()).add(style_file)

    existing_assets = sorted([file_path for file_path in rel_files if Path(file_path).suffix.lower() in ASSET_EXTS])
    asset_files = sorted(set(existing_assets) | set(direct_assets) | set(css_assets))
    assets: list[dict[str, Any]] = []
    for asset_file in asset_files:
        refs = set(direct_assets.get(asset_file, set()))
        css_sources = css_assets.get(asset_file, set())
        for css_source in css_sources:
            refs.update(style_refs.get(css_source, set()))
        suffix = Path(asset_file).suffix.lower()
        kind = "css-bg" if css_sources and not direct_assets.get(asset_file) else ("svg" if suffix == ".svg" else "png" if suffix == ".png" else "other")
        aid = asset_id(asset_file)
        assets.append({"asset_id": aid, "file_path": asset_file, "referenced_by": sorted(refs), "kind": kind})
        for cid in sorted(refs):
            add_edge(cid, aid, "uses_asset")

    route_files = sorted([file_path for file_path in module_files if file_path.startswith("apps/keystone/app/") and file_path.endswith("/page.tsx")])
    routes: list[dict[str, Any]] = []
    screen_mapping: dict[str, dict[str, str]] = {}

    for route_file in route_files:
        path = _route_path_from_file(route_file)
        rid = route_id(path)
        owners = _owners(file_to_components, route_file)
        route_component = owners[0] if owners else None
        rendered = component_index.get(route_component, {}).get("renders", []) if route_component else []
        screen_component = None
        nav_component = None
        screen_candidates: list[tuple[int, str]] = []
        for cid in sorted(rendered):
            component = component_index[cid]
            kind = component["kind"]
            file_path = component["file_path"]
            if kind == "nav" and nav_component is None:
                nav_component = cid
            if "components/pitch" not in file_path:
                continue
            if kind not in {"screen", "control", "block"}:
                continue

            priority = 4
            if kind == "screen":
                priority = 1
            elif "/screen-" in file_path:
                priority = 1
            elif "/run1/" in file_path or "/run2/" in file_path:
                priority = 2
            elif "pitch-shell" in file_path:
                priority = 9
            elif kind == "control":
                priority = 3
            screen_candidates.append((priority, cid))

        if screen_candidates:
            screen_candidates.sort(key=lambda item: (item[0], item[1]))
            screen_component = screen_candidates[0][1]
        route_record: dict[str, Any] = {"route_id": rid, "path": path, "entry_file": route_file, "data_source_ids": []}
        layout_file = _collect_layout(route_file, file_lookup)
        if layout_file:
            route_record["layout_file"] = layout_file
            layout_components = _owners(file_to_components, layout_file)
            if layout_components:
                layout_id = next((cid for cid in layout_components if component_index[cid]["export_name"] == "default"), layout_components[0])
                add_edge(layout_id, rid, "layout_wraps")
        if screen_component:
            route_record["screen_component_id"] = screen_component
            add_edge(rid, screen_component, "route_to_screen")
        if nav_component:
            route_record["nav_component_id"] = nav_component
        routes.append(route_record)

        match = re.search(r"/pitch/(?P<num>[0-9]{2})-", path)
        if match and screen_component:
            screen_id = f"screen-{match.group('num')}"
            screen_mapping[screen_id] = {
                "route_path": path,
                "route_id": rid,
                "route_file": route_file,
                "component_id": screen_component,
                "component_file": component_index[screen_component]["file_path"],
            }

    ordered = [f"screen-{index:02d}" for index in range(1, 7)]
    pitch_routes = [route for route in routes if route["path"].startswith("/pitch/")]
    pitch_routes.sort(key=lambda item: item["path"])
    for screen_id in ordered:
        if screen_id in screen_mapping:
            continue
        fallback = pitch_routes.pop(0) if pitch_routes else None
        if not fallback:
            screen_mapping[screen_id] = {"route_path": "(undiscovered)", "route_id": "(undiscovered)", "route_file": "(undiscovered)", "component_id": "(undiscovered)", "component_file": "(undiscovered)"}
            continue
        component_id_value = fallback.get("screen_component_id", "(undiscovered)")
        component_file = component_index.get(component_id_value, {}).get("file_path", "(undiscovered)")
        screen_mapping[screen_id] = {
            "route_path": fallback["path"],
            "route_id": fallback["route_id"],
            "route_file": fallback["entry_file"],
            "component_id": component_id_value,
            "component_file": component_file,
        }

    hotspots: list[dict[str, Any]] = []

    def add_hotspot(screen_or_global: str, title: str, files: list[str], tokens: list[str], change_types: list[str], risk: str, notes: str) -> None:
        hotspots.append(
            {
                "hotspot_id": hotspot_id(screen_or_global, title),
                "screen_or_global": screen_or_global,
                "title": title,
                "files": sorted(set(files)),
                "components": _components_matching(components, tokens),
                "change_types": sorted(set(change_types)),
                "risk": risk,
                "notes": notes,
            }
        )

    add_hotspot("global", "Pitch shell orchestration", ["apps/keystone/components/pitch/pitch-shell.tsx", "apps/keystone/components/pitch/shell/pitch-shell.tsx", "apps/keystone/components/pitch/view-model/pitch-shell-model.ts"], ["pitch-shell", "pitch-shell-model"], ["layout", "interactions"], "high", "Global shell wraps all pitch routes; changes cascade across slides.")
    add_hotspot("global", "Pitch navigation and route rail", ["apps/keystone/components/pitch/pitch-nav.tsx", "apps/keystone/components/pitch/nav/pitch-rail-nav.tsx", "apps/keystone/components/pitch/route-index/pitch-route-chooser.tsx"], ["pitch-nav", "pitch-rail-nav", "route-chooser"], ["layout", "interactions", "validation"], "med", "Navigation and chooser must remain consistent with deck slug ordering.")
    add_hotspot("global", "Layer resolution and profile flags", ["apps/keystone/lib/pitch/layer-resolution.ts", "apps/keystone/app/pitch/page.tsx", "packages/ui-kit/src/layers/resolveLayerFlags.ts"], ["layer", "resolveLayerFlags"], ["state", "validation", "interactions"], "high", "Layer flags control profile rendering and debug overlays.")
    add_hotspot("global", "Brand presence central config", ["packages/ui-kit/src/brand/brand-presence.config.ts", "packages/ui-kit/src/brand/BrandPresenceLayer.tsx", "apps/keystone/components/pitch/shell/pitch-shell-brand-layer.tsx"], ["brand-presence", "BrandPresence", "pitch-shell-brand-layer"], ["brand", "state"], "high", "Edit brand only through central config and createBrandPresenceRootStyle; never override :root globally.")
    add_hotspot("global", "UI kit premium controls", ["packages/ui-kit/src/components/premium/controls/index.ts", "packages/ui-kit/src/components/premium/controls/ToggleSwitch.tsx", "packages/ui-kit/src/components/premium/controls/DropdownSelect.tsx"], ["premium/controls", "ToggleSwitch", "DropdownSelect"], ["interactions", "validation", "layout"], "med", "Premium control changes can impact multiple screens.")

    add_hotspot("screen-01", "Screen 01 double engine narrative", ["apps/keystone/app/pitch/01-double-engine/page.tsx", "apps/keystone/components/pitch/screen-double-engine.tsx"], ["screen-double-engine"], ["layout", "copy", "charts"], "med", "Narrative and KPI framing for screen 01.")
    add_hotspot("screen-02", "Screen 02 industrial flow", ["apps/keystone/app/pitch/02-industrial-flow/page.tsx", "apps/keystone/components/pitch/screen-industrial-flow.tsx"], ["screen-industrial-flow"], ["layout", "charts", "interactions"], "med", "Flow visuals rely on chart and panel composition.")
    add_hotspot("screen-03", "Screen 03 hitech os map", ["apps/keystone/app/pitch/03-hitech-os/page.tsx", "apps/keystone/components/pitch/screen-hitech-os.tsx"], ["screen-hitech-os"], ["layout", "copy", "charts"], "med", "Architecture storyline center for screen 03.")
    add_hotspot("screen-04", "Screen 04 valuation controls", ["apps/keystone/app/pitch/04-valuation/page.tsx", "apps/keystone/components/pitch/screen-valuation.tsx", "apps/keystone/components/pitch/valuation-blocks.tsx"], ["screen-valuation", "valuation-blocks"], ["layout", "charts", "interactions"], "high", "Valuation and charts are high-risk for metric interpretation.")
    add_hotspot("screen-05", "Screen 05 deepest: state machine + gating + docs vault + RBAC", ["apps/keystone/app/pitch/05-inventory-foundation/page.tsx", "apps/keystone/components/pitch/run1/store.ts", "apps/keystone/components/pitch/run1/InventoryFoundationControlRoom.tsx", "apps/keystone/components/pitch/run1/DocumentVaultPanel.tsx", "apps/keystone/components/pitch/run1/RBACMatrixPanel.tsx"], ["run1/store", "InventoryFoundationControlRoom", "DocumentVaultPanel", "RBACMatrixPanel"], ["state", "validation", "interactions", "layout"], "high", "Deepest overlap hotspot: deterministic state transitions, gating, document vault lifecycle, and RBAC controls.")
    add_hotspot("screen-06", "Screen 06 deepest: receiving gate + controls + mismatch handling + RBAC handoff", ["apps/keystone/app/pitch/06-shipments-receiving/page.tsx", "apps/keystone/components/pitch/run2/store.ts", "apps/keystone/components/pitch/run2/ShipmentsReceivingControlRoom.tsx", "apps/keystone/components/pitch/run2/RiskAndNextGatePanel.tsx", "apps/keystone/components/pitch/run2/MismatchHandlingPanel.tsx"], ["run2/store", "ShipmentsReceivingControlRoom", "RiskAndNextGatePanel", "MismatchHandlingPanel"], ["state", "validation", "interactions", "layout"], "high", "Deepest overlap hotspot: receiving state machine, customs/doc gates, mismatch/deviation, and gate progression logic.")

    edges = [{"from": frm, "to": to, "type": edge_type, **({"notes": notes} if notes else {})} for frm, to, edge_type, notes in sorted(edge_set)]

    dictionary = {
        "version": "1.0.0",
        "generated_by": {"tool": "tools/ui_map", "mode": "deterministic"},
        "repo_root": ".",
        "routes": routes,
        "components": components,
        "states": states,
        "styles": styles,
        "assets": assets,
        "edges": edges,
        "hotspots": hotspots,
    }
    dictionary = sort_ui_dictionary(dictionary)

    screen_roots = [
        info["component_file"]
        for _, info in sorted(screen_mapping.items(), key=lambda item: item[0])
        if info.get("component_file") and info.get("component_file") != "(undiscovered)"
    ]

    return {
        "ui_dictionary": dictionary,
        "discovery": {
            "paths_searched": searched,
            "route_files": route_files,
            "screen_roots": screen_roots,
            "screen_mapping": {key: screen_mapping[key] for key in sorted(screen_mapping)},
            "component_count": len(dictionary["components"]),
            "route_count": len(dictionary["routes"]),
            "notes": [
                "Import graph parsed from TS/TSX modules with barrel export resolution heuristics.",
                "Render graph inferred from JSX tag usage against imported symbols.",
                "State readers/writers/events extracted with deterministic regex heuristics.",
            ],
        },
    }
