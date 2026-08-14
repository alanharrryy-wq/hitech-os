from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from code_atlas.operational.runtime_profile import ROUTE_FILENAMES, public_path, resolve_runtime_profile


TEXT_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css", ".scss", ".json", ".md", ".mdx", ".html", ".py"}
SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "coverage", ".turbo", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
DATA_ATTR_RE = re.compile(r"(data-(?:component|layer|role|part|kind|surface|screen|zone|panel|target|state|intent|slot|testid|cy))\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|`([^`]*)`|\{([^}\n]+)\})", re.I)
COMPONENT_RE = re.compile(r"(?:export\s+)?(?:default\s+)?(?:function|const|class)\s+([A-Z][A-Za-z0-9_]*)", re.M)
CSS_SELECTOR_RE = re.compile(r"^\s*((?:\.[A-Za-z_][\w-]*|\[[^\]]+\]|#[A-Za-z_][\w-]*|:[\w-]+|[A-Za-z][\w-]*)(?:[^{;]*))\s*\{", re.M)
KIND_TERMS = {
    "button": ("button", "btn", "cta", "submit", "action"),
    "price": ("price", "total", "amount", "currency"),
    "badge": ("badge", "pill", "chip", "status"),
    "table": ("table", "row", "cell", "grid"),
    "background": ("background", "backdrop", "canvas"),
    "panel": ("panel", "card", "drawer", "modal", "sheet", "pane"),
    "field": ("input", "field", "select", "textarea", "form"),
    "icon": ("icon", "glyph", "svg"),
    "layout": ("layout", "stack", "section", "zone", "container"),
    "effect": ("glass", "shadow", "blur", "glow", "effect", "material"),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _notify(callback: Callable[[str, str], None] | None, status: str, detail: str = "") -> None:
    if callback:
        callback(status, detail)
    else:
        print(f"{status} {detail}".rstrip(), flush=True)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_json(path: Path, value: Any) -> None:
    _write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _zip_dir(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=8) as bundle:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(source).as_posix())


def _find_repo_root(selected_path: str | Path) -> Path:
    start = Path(selected_path).expanduser().resolve()
    if start.is_file():
        start = start.parent
    markers = (".git", "pyproject.toml", "package.json", "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "requirements.txt")
    for candidate in (start, *start.parents):
        if any((candidate / marker).exists() for marker in markers):
            return candidate
    return start


def _iter_files(roots: Iterable[Path]) -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            candidates = [root]
        else:
            candidates = []
            for current, dirs, files in os.walk(root):
                dirs[:] = [name for name in dirs if name not in SKIP_DIRS and not name.startswith(".")]
                candidates.extend(Path(current) / name for name in files)
        for path in candidates:
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                if path.stat().st_size > 3_000_000:
                    continue
            except OSError:
                continue
            key = str(path.resolve()).lower()
            if key not in seen:
                seen.add(key)
                found.append(path)
    return sorted(found, key=lambda path: str(path).lower())


def _surface_roots(repo: Path, output_root: Path, target_app: str) -> tuple[str, list[tuple[str, str, Path]]]:
    profile = resolve_runtime_profile(repo, output_root, None)
    requested = str(target_app or "all").strip().lower()
    surfaces = []
    for spec in profile.surfaces:
        root = Path(spec.root)
        root = root.resolve() if root.is_absolute() else (repo / root).resolve()
        surfaces.append((spec.surface_id, spec.label, root))
    if requested in {"", "all", "*"}:
        return "all", surfaces
    matches = [row for row in surfaces if requested in {str(row[0]).lower(), str(row[1]).lower()}]
    if not matches:
        candidate = Path(target_app)
        candidate = candidate.resolve() if candidate.is_absolute() else (repo / candidate).resolve()
        if candidate.exists():
            matches = [(requested, candidate.name, candidate)]
    if not matches:
        raise ValueError(f"UNKNOWN_SURFACE:{target_app}")
    return requested, matches


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, max(0, offset)) + 1


def _normalize(value: Any, fallback: str = "unknown") -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(value or "").strip())
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text or fallback


def _infer_kind(*values: Any) -> str:
    haystack = " ".join(str(value or "") for value in values).lower()
    for kind, terms in KIND_TERMS.items():
        if any(re.search(rf"(?:^|[^a-z0-9]){re.escape(term)}(?:[^a-z0-9]|$)", haystack) for term in terms):
            return kind
    return "unknown"


def _route_from_file(path: Path, surface_root: Path) -> str:
    try:
        relative = path.relative_to(surface_root).as_posix()
    except Exception:
        return "/"
    parts = relative.split("/")
    if path.name not in ROUTE_FILENAMES:
        return "/"
    route_parts = [part for part in parts[:-1] if part not in {"app", "src", "pages", "routes"} and not (part.startswith("(") and part.endswith(")"))]
    return "/" + "/".join(route_parts) if route_parts else "/"


def _scan_one(path: Path, repo: Path, surface_id: str, surface_label: str, surface_root: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {"file": public_path(path, repo), "surface": surface_id, "surfaceLabel": surface_label, "readStatus": f"READ_ERROR:{type(exc).__name__}", "targets": [], "components": [], "selectors": []}

    attrs_by_line: dict[int, dict[str, str]] = {}
    for match in DATA_ATTR_RE.finditer(text):
        value = next((group for group in match.groups()[1:] if group is not None), "")
        attrs_by_line.setdefault(_line_number(text, match.start()), {})[match.group(1).lower()] = value.strip()

    components = [{"name": match.group(1), "line": _line_number(text, match.start())} for match in COMPONENT_RE.finditer(text)]
    selectors = [{"selector": match.group(1).strip(), "line": _line_number(text, match.start())} for match in CSS_SELECTOR_RE.finditer(text)]
    route = _route_from_file(path, surface_root)
    screen = _normalize(route.strip("/") or surface_id, "root")
    targets: list[dict[str, Any]] = []

    for line, attrs in attrs_by_line.items():
        raw = " ".join(f"{key}={value}" for key, value in attrs.items())
        target_id = attrs.get("data-target") or attrs.get("data-part") or attrs.get("data-role") or attrs.get("data-component") or f"line_{line}"
        kind = attrs.get("data-kind") or _infer_kind(raw, path.name)
        required_marks = ("data-surface", "data-screen", "data-zone", "data-panel", "data-target", "data-kind", "data-role")
        missing = [mark for mark in required_marks if not attrs.get(mark)]
        targets.append({
            "surface": surface_id,
            "surfaceLabel": surface_label,
            "screenId": attrs.get("data-screen") or screen,
            "route": route,
            "zoneId": attrs.get("data-zone") or attrs.get("data-layer") or "unknown_zone",
            "panelId": attrs.get("data-panel") or attrs.get("data-component") or "unknown_panel",
            "targetId": _normalize(target_id, f"line_{line}"),
            "kind": kind,
            "role": attrs.get("data-role") or "unknown",
            "file": public_path(path, repo),
            "line": line,
            "attributes": attrs,
            "status": "CONFIRMED_RUNTIME_SEMANTIC_TARGET" if not missing else "INSTRUMENTATION_REQUIRED",
            "confidence": "high" if not missing else "medium",
            "missingRuntimeMarks": missing,
            "editableNow": not missing and kind != "unknown",
            "authorizesPatch": False,
        })

    return {
        "file": public_path(path, repo),
        "surface": surface_id,
        "surfaceLabel": surface_label,
        "route": route,
        "readStatus": "OK",
        "sha256": _sha256(path),
        "targets": targets,
        "components": components,
        "selectors": selectors,
    }


def _build_outputs(scans: list[dict[str, Any]]) -> dict[str, Any]:
    targets = [target for scan in scans for target in scan.get("targets", [])]
    routes = sorted({(scan.get("surface"), scan.get("route"), scan.get("file")) for scan in scans if scan.get("route") is not None})
    route_map = [{"surface": surface, "route": route, "file": file} for surface, route, file in routes]
    components = [{"surface": scan.get("surface"), "file": scan.get("file"), **component} for scan in scans for component in scan.get("components", [])]
    selectors = [{"surface": scan.get("surface"), "file": scan.get("file"), **selector} for scan in scans for selector in scan.get("selectors", [])]
    missing = [target for target in targets if target.get("missingRuntimeMarks")]
    readiness = [{"targetId": target["targetId"], "surface": target["surface"], "file": target["file"], "line": target["line"], "status": target["status"], "editableNow": target["editableNow"], "missingRuntimeMarks": target["missingRuntimeMarks"], "authorizesPatch": False} for target in targets]
    graph_nodes = []
    graph_edges = []
    seen: set[str] = set()
    for target in targets:
        surface_node = f"surface:{target['surface']}"
        screen_node = f"screen:{target['surface']}:{target['screenId']}"
        target_node = f"target:{target['surface']}:{target['screenId']}:{target['targetId']}"
        for node_id, kind, label in ((surface_node, "surface", target["surfaceLabel"]), (screen_node, "screen", target["screenId"]), (target_node, "target", target["targetId"])):
            if node_id not in seen:
                seen.add(node_id)
                graph_nodes.append({"id": node_id, "type": kind, "label": label})
        graph_edges.extend(({"from": surface_node, "to": screen_node, "type": "has_screen"}, {"from": screen_node, "to": target_node, "type": "has_target"}))
    return {
        "targets": targets,
        "routeMap": route_map,
        "componentMap": components,
        "selectorMap": selectors,
        "missingMarks": missing,
        "patchReadiness": readiness,
        "controlGraph": {"schema": "CODE_ATLAS_CONTROL_GRAPH.v1", "nodes": graph_nodes, "edges": graph_edges},
    }


def _fail_zip(staging: Path, fail_zip: Path, exc: BaseException) -> str:
    staging.mkdir(parents=True, exist_ok=True)
    _write_text(staging / "ERROR.txt", traceback.format_exc())
    _write_json(staging / "RUN_MANIFEST.json", {"status": "FAIL_SURFACE_TARGET_ATLAS", "error": f"{type(exc).__name__}: {exc}", "readOnly": True, "authorizesPatch": False, "environmentNeutral": True})
    _zip_dir(staging, fail_zip)
    return str(fail_zip)


def run_surface_target_atlas(
    selected_path: str,
    *,
    target_app: str = "all",
    output_root: str | os.PathLike[str] | None = None,
    notify: Callable[[str, str], None] | None = None,
) -> str:
    repo = _find_repo_root(selected_path)
    default_out = os.environ.get("CODE_ATLAS_OUTPUT_ROOT", "./code-atlas-out")
    out_root = Path(output_root or default_out).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    app_key, surfaces = _surface_roots(repo, out_root, target_app)
    stamp = datetime.now().strftime("%d%m %H%M%S")
    staging = out_root / f"_surfaceatlas_work_{os.getpid()}"
    result_zip = out_root / f"surfaceatlas {stamp} result.zip"
    fail_zip = out_root / f"surfaceatlas {stamp} fail.zip"

    try:
        if staging.exists():
            for child in sorted(staging.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
        staging.mkdir(parents=True, exist_ok=True)
        roots = [root for _, _, root in surfaces]
        _notify(notify, "Surface Target Atlas · preflight", f"surfaces={len(surfaces)}")
        files = _iter_files(roots)
        scans: list[dict[str, Any]] = []
        workers = max(1, min(18, int(os.environ.get("CODE_ATLAS_SURFACE_ATLAS_WORKERS", "18"))))
        surface_by_path = sorted(surfaces, key=lambda row: len(str(row[2])), reverse=True)

        def owner(path: Path) -> tuple[str, str, Path]:
            for surface_id, label, root in surface_by_path:
                try:
                    path.resolve().relative_to(root.resolve())
                    return surface_id, label, root
                except Exception:
                    continue
            return "repository", repo.name or "Repository", repo

        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_map = {}
            for path in files:
                surface_id, label, root = owner(path)
                future_map[pool.submit(_scan_one, path, repo, surface_id, label, root)] = path
            total = len(future_map)
            for index, future in enumerate(as_completed(future_map), 1):
                scans.append(future.result())
                if total and (index == total or index % max(1, total // 10) == 0):
                    _notify(notify, f"Surface Target Atlas · {int(index * 100 / total)}%", f"{index}/{total}")
        scans.sort(key=lambda row: str(row.get("file", "")).lower())
        outputs = _build_outputs(scans)

        manifest = {
            "schema": "CODE_ATLAS_SURFACE_TARGET_ATLAS.v3",
            "generatedAt": now_iso(),
            "status": "PASS_SURFACE_TARGET_ATLAS_GENERATED",
            "readOnly": True,
            "authorizesPatch": False,
            "environmentNeutral": True,
            "targetSelection": app_key,
            "repoRootName": repo.name,
            "repoPathDigest": "sha256:" + hashlib.sha256(str(repo).encode("utf-8", errors="ignore")).hexdigest()[:20],
            "surfaces": [{"id": surface_id, "label": label, "root": public_path(root, repo)} for surface_id, label, root in surfaces],
            "counts": {
                "filesScanned": len(scans),
                "targets": len(outputs["targets"]),
                "confirmedTargets": sum(target.get("status") == "CONFIRMED_RUNTIME_SEMANTIC_TARGET" for target in outputs["targets"]),
                "instrumentationRequired": len(outputs["missingMarks"]),
                "routes": len(outputs["routeMap"]),
                "components": len(outputs["componentMap"]),
                "selectors": len(outputs["selectorMap"]),
            },
            "productionCertified": False,
        }
        _write_json(staging / "RUN_MANIFEST.json", manifest)
        _write_json(staging / "CODE_ATLAS_SURFACE_TARGET_ATLAS.json", {**manifest, "targets": outputs["targets"]})
        _write_json(staging / "TARGET_REGISTRY_DRAFT.json", outputs["targets"])
        _write_json(staging / "SCREEN_ROUTE_MAP.json", outputs["routeMap"])
        _write_json(staging / "COMPONENT_MAP.json", outputs["componentMap"])
        _write_json(staging / "CSS_SELECTOR_MAP.json", outputs["selectorMap"])
        _write_json(staging / "CODE_ATLAS_CONTROL_GRAPH.json", outputs["controlGraph"])
        _write_json(staging / "CODE_ATLAS_MISSING_MARKS_PLAN.json", {"schema": "CODE_ATLAS_MISSING_MARKS_PLAN.v1", "targets": outputs["missingMarks"], "authorizesPatch": False})
        _write_json(staging / "CODE_ATLAS_PATCH_READINESS.json", {"schema": "CODE_ATLAS_PATCH_READINESS.v1", "targets": outputs["patchReadiness"], "readOnly": True, "authorizesPatch": False})
        _write_json(staging / "reports" / "files_scanned.json", scans)
        _write_text(staging / "SUMMARY_FOR_CHAT.md", f"# Surface Target Atlas\n\nStatus: `{manifest['status']}`\n\nFiles: `{manifest['counts']['filesScanned']}`\nTargets: `{manifest['counts']['targets']}`\nConfirmed: `{manifest['counts']['confirmedTargets']}`\n\nRead-only. No source, Git, database, process, port or dependency mutation.\n")
        _write_text(staging / "CONTINUATION.md", "# Continuation\n\nUse runtime semantic attributes as evidence. Static component and selector discovery is context only. This atlas never authorizes a patch by itself.\n")
        _zip_dir(staging, result_zip)
        _notify(notify, "Surface Target Atlas · ready", result_zip.name)
        return str(result_zip)
    except Exception as exc:
        _notify(notify, "Surface Target Atlas · FAIL", f"{type(exc).__name__}: {exc}")
        return _fail_zip(staging, fail_zip, exc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Code Atlas Surface Target Atlas read-only generator")
    parser.add_argument("--selected-path", required=True)
    parser.add_argument("--target-app", default="all")
    parser.add_argument("--output-root", default=None)
    args = parser.parse_args(argv)
    result = run_surface_target_atlas(selected_path=args.selected_path, target_app=args.target_app, output_root=args.output_root)
    print(result)
    return 2 if result.endswith("fail.zip") else 0


if __name__ == "__main__":
    raise SystemExit(main())
