"""Repository-neutral App Map generator.

This is the default App Map execution path. Targets come only from the active
project profile, or from the selected repository root when no apps are declared.
Product-specific App Map implementations remain explicit adapters.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from code_atlas.core.project_profile import load_project_profile
from .strict_classifier import (
    SCAN_EXTENSIONS,
    classify_file,
    derive_route,
    extract_selectors,
    extract_tokens,
    is_route_file,
    is_valid_selector,
)

EXCLUDE = {".git", "node_modules", ".next", "dist", "build", "coverage", ".turbo", "__pycache__", ".pytest_cache"}
CLASS_USAGE = re.compile(r"className\s*=\s*[\"']([^\"']+)[\"']|styles\.([A-Za-z0-9_]+)")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _stamp() -> str:
    return datetime.now().strftime("%d%m %H%M")


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.name


def _iter_files(root: Path):
    if not root.exists():
        return
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in EXCLUDE and not name.startswith(".")]
        for name in files:
            path = Path(current) / name
            if path.suffix.lower() in SCAN_EXTENSIONS:
                yield path


def _read(path: Path) -> str:
    try:
        if path.stat().st_size > 3_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields, rows = ["status"], [{"status": "EMPTY"}]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False, sort_keys=True) if isinstance(row.get(key), (dict, list)) else row.get(key, "") for key in fields})


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _targets(repo: Path, target_app: str) -> list[tuple[str, str, str, bool, Path]]:
    profile = load_project_profile()
    rows: list[tuple[str, str, str, bool, Path]] = []
    for app in profile.apps:
        if target_app not in {"", "all", app.id}:
            continue
        raw = str(app.root or ".")
        candidate = (repo / raw).resolve()
        try:
            candidate.relative_to(repo)
        except ValueError:
            continue
        rows.append((app.id, app.label, app.kind, bool(app.protected), candidate))
    if rows:
        return rows
    if target_app not in {"", "all", "repository"}:
        return []
    return [("repository", profile.project_name or "Repository", "repository", False, repo)]


def _class_usage(text: str) -> list[str]:
    values: set[str] = set()
    for match in CLASS_USAGE.finditer(text):
        if match.group(1):
            values.update(part for part in re.split(r"\s+", match.group(1).strip()) if part)
        if match.group(2):
            values.add(match.group(2))
    return sorted(values)


def run_app_map(
    selected_path: str,
    target_app: str = "all",
    output_root: str | None = None,
    notify: Callable[[str, str], None] | None = None,
) -> str:
    selected = Path(selected_path).expanduser().resolve()
    repo = selected if selected.is_dir() else selected.parent
    profile = load_project_profile()
    configured_repo = Path(profile.project_root).expanduser()
    if str(profile.project_root).strip() not in {"", ".", "${CODE_ATLAS_PROJECT_ROOT}"} and configured_repo.exists():
        repo = configured_repo.resolve()
    out_root = Path(output_root or os.environ.get("CODE_ATLAS_OUTPUT_ROOT") or (repo / "code-atlas-out")).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    targets = _targets(repo, target_app or "all")
    if notify:
        notify("App Map profile targets", ", ".join(row[0] for row in targets) or "none")

    with tempfile.TemporaryDirectory(prefix="code-atlas-appmap-") as tmp:
        atlas = Path(tmp) / "app_map_atlas"
        atlas.mkdir()
        surface_registry: list[dict[str, Any]] = []
        route_component: list[dict[str, Any]] = []
        component_owner: list[dict[str, Any]] = []
        selector_rows: list[dict[str, Any]] = []
        selector_usage: list[dict[str, Any]] = []
        token_rows: list[dict[str, Any]] = []
        layer_rows: list[dict[str, Any]] = []
        file_index: list[dict[str, Any]] = []
        rejected_rows: list[dict[str, Any]] = []

        for app_id, label, kind, protected, root in targets:
            files = list(_iter_files(root)) if root.exists() else []
            routes = []
            for path in files:
                file_kind = classify_file(path, root)
                rel = _rel(root, path)
                file_index.append({"appId": app_id, "file": rel, "fileKind": file_kind, "suffix": path.suffix.lower()})
                if is_route_file(path, root):
                    route = derive_route(root, path)
                    row = {"appId": app_id, "route": route, "file": rel, "fileKind": "route"}
                    routes.append(row)
                    route_component.append(row)

            surface_registry.append({
                "appId": app_id,
                "label": label,
                "kind": kind,
                "root": _rel(repo, root),
                "exists": root.exists(),
                "fileCount": len(files),
                "routeCount": len(routes),
                "protected": protected,
                "source": "project-profile" if app_id != "repository" else "repository-fallback",
            })

            for path in files:
                file_kind = classify_file(path, root)
                text = _read(path)
                rel = _rel(root, path)
                if file_kind in {"component", "component_candidate"}:
                    classes = _class_usage(text)
                    component_owner.append({
                        "appId": app_id,
                        "componentFile": rel,
                        "componentId": path.stem,
                        "classUsageCount": len(classes),
                        "protected": protected,
                    })
                    for class_name in classes:
                        selector_usage.append({"appId": app_id, "selectorOrToken": class_name, "usedIn": rel})
                if file_kind == "style":
                    selectors, rejected = extract_selectors(text)
                    for item in rejected:
                        rejected_rows.append({"appId": app_id, "file": rel, **item})
                    for selector in selectors:
                        if not is_valid_selector(selector):
                            rejected_rows.append({"appId": app_id, "file": rel, "candidate": selector, "reason": "validator_reject"})
                            continue
                        states = [state for state in (":hover", ":focus", ":focus-visible", ":disabled", ":active", "[aria-", "[data-") if state in selector]
                        selector_rows.append({"appId": app_id, "selector": selector, "definedIn": rel, "states": "|".join(states)})
                        layer_rows.append({"appId": app_id, "layer": selector, "kind": "selector", "stateCount": len(states)})
                    for token in extract_tokens(text):
                        token_rows.append({
                            "appId": app_id,
                            "token": token.get("token", ""),
                            "tokenKind": token.get("kind", "unknown"),
                            "defaultValue": token.get("defaultValue", ""),
                            "definedOrUsedIn": rel,
                        })

        artifacts = {
            "01_SURFACE_REGISTRY.json": surface_registry,
            "02_ROUTE_COMPONENT_MAP.json": route_component,
            "03_COMPONENT_OWNERSHIP_MAP.json": component_owner,
            "04_LAYER_ROLE_KIND_MAP.json": layer_rows,
            "05_SELECTOR_MAP.json": selector_rows,
            "06_SELECTOR_USAGE.json": selector_usage,
            "07_TOKEN_MAP.json": token_rows,
            "08_FILE_INDEX.json": file_index,
            "09_REJECTED_CANDIDATES.json": rejected_rows,
        }
        for name, value in artifacts.items():
            _json(atlas / name, value)
            if isinstance(value, list):
                _csv(atlas / name.replace(".json", ".csv"), value)

        manifest = {
            "schemaVersion": "code_atlas_app_map.v2",
            "status": "PASS_APP_MAP_GENERATED" if targets else "BLOCKED_NO_PROFILE_TARGETS",
            "generatedAt": _now(),
            "profileId": profile.profile_id,
            "targetApp": target_app or "all",
            "targetCount": len(targets),
            "surfaceCount": len(surface_registry),
            "routeCount": len(route_component),
            "componentCount": len(component_owner),
            "selectorCount": len(selector_rows),
            "tokenCount": len(token_rows),
            "readOnly": True,
            "productAdapterSelected": False,
            "certifiable": False,
            "productionCertified": False,
        }
        _json(atlas / "APP_MAP_MANIFEST.json", manifest)
        (atlas / "README.md").write_text(
            "# Code Atlas App Map\n\nTargets are derived from the explicit project profile. This artifact is read-only and does not certify production.\n",
            encoding="utf-8",
        )

        final_zip = out_root / f"appmap {_stamp()} result.zip"
        if final_zip.exists():
            final_zip.unlink()
        with zipfile.ZipFile(final_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as bundle:
            for path in sorted(atlas.rglob("*")):
                if path.is_file():
                    bundle.write(path, path.relative_to(atlas).as_posix())
        manifest["artifactSha256"] = _sha(final_zip)
        return str(final_zip)
