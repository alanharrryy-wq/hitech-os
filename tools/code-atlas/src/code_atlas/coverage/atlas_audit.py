from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from code_atlas.core.io_utils import (
    DEFAULT_IGNORE_DIRS,
    iso_now,
    iter_project_files,
    read_json,
    safe_rel,
    write_json,
    write_text,
)

PATH_KEY_RE = re.compile(r"(?i)(path|file|entry|relative|rel|relpath|source|target)$")
IMPORTANT_KEY_RE = re.compile(r"(?i)(important|entrypoint|critical|required|must|gate)")
NOISE_PREFIXES = (".next/", "node_modules/", "__pycache__/", ".git/")
MAX_DISCOVERY_FILES_PER_ROOT = int(os.environ.get("CODE_ATLAS_META_DISCOVERY_LIMIT", "2400") or "2400")
MAX_JSON_BYTES_FROM_ZIP = int(os.environ.get("CODE_ATLAS_META_JSON_MAX_BYTES", str(18 * 1024 * 1024)) or str(18 * 1024 * 1024))


@dataclass(frozen=True)
class CoverageAuditConfig:
    project_root: Path
    atlas_paths: tuple[Path, ...] = ()
    meta_paths: tuple[Path, ...] = ()
    package_paths: tuple[Path, ...] = ()
    output_dir: Path | None = None


def _norm_path(value: Any) -> str:
    text = str(value or "").strip().strip('"').strip("'").replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    text = text.strip("/")
    for prefix in ("project/", "payload/", "repo/", "root/"):
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    return text


def _looks_like_path(value: Any) -> bool:
    text = _norm_path(value)
    if not text or len(text) > 500 or "\n" in text or "\r" in text:
        return False
    if text.startswith(("http://", "https://", "data:")):
        return False
    return "/" in text or bool(re.search(r"\.[A-Za-z0-9]{1,14}$", text))


def _walk_json_paths(data: Any, *, important_only: bool = False, stack: tuple[str, ...] = ()) -> set[str]:
    found: set[str] = set()
    important_context = bool(IMPORTANT_KEY_RE.search("/".join(stack)))
    if isinstance(data, dict):
        for key, value in data.items():
            key_text = str(key)
            eligible = bool(PATH_KEY_RE.search(key_text)) or important_context or not important_only
            if isinstance(value, str) and eligible and _looks_like_path(value):
                found.add(_norm_path(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and eligible and _looks_like_path(item):
                        found.add(_norm_path(item))
                    elif isinstance(item, (dict, list)):
                        found.update(_walk_json_paths(item, important_only=important_only, stack=stack + (key_text,)))
            elif isinstance(value, (dict, list)):
                found.update(_walk_json_paths(value, important_only=important_only, stack=stack + (key_text,)))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                found.update(_walk_json_paths(item, important_only=important_only, stack=stack))
            elif isinstance(item, str) and not important_only and _looks_like_path(item):
                found.add(_norm_path(item))
    return {path for path in found if path}


def _split_env_paths(name: str) -> list[Path]:
    raw = os.environ.get(name, "")
    if not raw:
        return []
    normalized = raw.replace("|", os.pathsep)
    return [Path(chunk.strip().strip('"').strip("'")) for chunk in normalized.split(os.pathsep) if chunk.strip()]


def _candidate_context_roots(project_root: Path) -> list[Path]:
    candidates = [
        *_split_env_paths("CODE_ATLAS_CONTEXT_ROOTS"),
        *_split_env_paths("CODE_ATLAS_META_ROOTS"),
        *_split_env_paths("CODE_ATLAS_ATLAS_ROOTS"),
        project_root,
        project_root / "_dependency_graphs",
        project_root / "evidence",
        project_root / "reports",
    ]
    seen: set[str] = set()
    roots: list[Path] = []
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except Exception:
            continue
        key = os.path.normcase(str(resolved))
        if key in seen or not resolved.exists():
            continue
        seen.add(key)
        roots.append(resolved)
    return roots


def _iter_candidate_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    emitted = 0
    ignored = {name.lower() for name in DEFAULT_IGNORE_DIRS}
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(name for name in dirs if name.lower() not in ignored and not name.startswith("."))
        for name in sorted(files):
            path = Path(current) / name
            if path.suffix.lower() not in {".json", ".zip"}:
                continue
            yield path
            emitted += 1
            if emitted >= MAX_DISCOVERY_FILES_PER_ROOT:
                return


def _kind_name(path_text: str, kind: str) -> bool:
    low = path_text.lower().replace("\\", "/")
    name = Path(low).name
    if kind == "atlas":
        return any(token in name or token in low for token in ("atlas", "dependency_graph", "dependency-map", "dependency_map", "graph.json"))
    if kind == "meta":
        return any(token in name or token in low for token in ("kept", "manifest", "checksum", "meta", "summary")) and "excluded" not in name
    if kind == "package":
        return name.endswith(".zip") and not any(token in name for token in ("fail", "diagnostic"))
    return False


def discover_coverage_sources(root: Path) -> tuple[list[Path], list[Path], list[Path], list[str]]:
    atlas: dict[str, Path] = {}
    meta: dict[str, Path] = {}
    packages: dict[str, Path] = {}
    roots = _candidate_context_roots(root)
    for scan_root in roots:
        for path in _iter_candidate_files(scan_root):
            key = os.path.normcase(str(path.resolve()))
            if _kind_name(str(path), "atlas"):
                atlas[key] = path.resolve()
            if _kind_name(str(path), "meta"):
                meta[key] = path.resolve()
            if _kind_name(str(path), "package"):
                packages[key] = path.resolve()
    notes = ["auto_discovery_roots=" + "; ".join(path.name or "." for path in roots[:12])] if roots else []
    return list(atlas.values())[:80], list(meta.values())[:120], list(packages.values())[:80], notes


def _load_json_sources(paths: Iterable[Path], *, kind: str) -> list[tuple[str, Any, str]]:
    rows: list[tuple[str, Any, str]] = []
    for raw in paths:
        path = Path(raw)
        try:
            if path.suffix.lower() == ".zip":
                with zipfile.ZipFile(path) as bundle:
                    matches = [info for info in bundle.infolist() if info.filename.lower().endswith(".json") and info.file_size <= MAX_JSON_BYTES_FROM_ZIP and _kind_name(info.filename, kind)]
                    for info in matches:
                        try:
                            rows.append((f"{path.name}::{info.filename}", json.loads(bundle.read(info).decode("utf-8", errors="replace")), "ok"))
                        except Exception as exc:
                            rows.append((f"{path.name}::{info.filename}", None, f"error:{type(exc).__name__}"))
                    if not matches:
                        rows.append((path.name, None, "zip_ok_no_matching_json"))
            else:
                rows.append((path.name, read_json(path), "ok"))
        except Exception as exc:
            rows.append((path.name, None, f"error:{type(exc).__name__}"))
    return rows


def _classify_missing(paths: Iterable[str]) -> dict[str, list[str]]:
    critical: list[str] = []
    generated: list[str] = []
    unknown: list[str] = []
    for path in sorted(set(paths)):
        low = path.lower()
        if any(low.startswith(prefix) for prefix in NOISE_PREFIXES) or any(token in low for token in ("generated", "cache", "coverage")):
            generated.append(path)
        elif any(token in low for token in ("schema", "migration", "entry", "main.", "index.", "package.json", "pyproject.toml", "go.mod", "cargo.toml")):
            critical.append(path)
        else:
            unknown.append(path)
    return {"critical": critical, "generated_or_noise": generated, "unknown": unknown}


def run_audit(config: CoverageAuditConfig) -> dict[str, Any]:
    root = config.project_root.expanduser().resolve()
    physical = {_norm_path(safe_rel(path, root)) for path in iter_project_files(root)}
    atlas_paths = list(config.atlas_paths)
    meta_paths = list(config.meta_paths)
    package_paths = list(config.package_paths)
    notes: list[str] = []
    if not atlas_paths and not meta_paths and not package_paths:
        atlas_paths, meta_paths, package_paths, notes = discover_coverage_sources(root)

    atlas_sources = _load_json_sources(atlas_paths, kind="atlas")
    meta_sources = _load_json_sources(meta_paths, kind="meta")
    expected: set[str] = set()
    important: set[str] = set()
    source_status: list[dict[str, Any]] = []
    for source_id, data, status in atlas_sources:
        source_status.append({"source": source_id, "kind": "atlas", "status": status})
        if data is not None:
            expected.update(_walk_json_paths(data))
            important.update(_walk_json_paths(data, important_only=True))
    for source_id, data, status in meta_sources:
        source_status.append({"source": source_id, "kind": "meta", "status": status})
        if data is not None:
            expected.update(_walk_json_paths(data))
            important.update(_walk_json_paths(data, important_only=True))

    expected = {_norm_path(path) for path in expected if _norm_path(path)}
    important = {_norm_path(path) for path in important if _norm_path(path)}
    present = sorted(path for path in expected if path in physical)
    missing = sorted(path for path in expected if path not in physical)
    missing_important = sorted(path for path in important if path not in physical)
    classes = _classify_missing(missing)
    validation = "PASS" if not missing_important and not classes["critical"] else "FAIL"

    return {
        "kind": "atlas_coverage_audit_v2",
        "created_at": iso_now(),
        "validation": validation,
        "project_name": root.name,
        "project_path_digest": "sha256:" + hashlib.sha256(str(root).encode("utf-8", errors="ignore")).hexdigest()[:20],
        "environment_neutral": True,
        "expected_paths": sorted(expected),
        "present_paths": present,
        "missing_paths": missing,
        "missing_important": missing_important,
        "missing_classification": classes,
        "source_status": source_status,
        "package_sources": [Path(path).name for path in package_paths],
        "notes": notes,
        "counts": {
            "physical_files": len(physical),
            "expected_paths": len(expected),
            "present_paths": len(present),
            "missing_paths": len(missing),
            "missing_important": len(missing_important),
            "critical_missing": len(classes["critical"]),
            "unknown_missing": len(classes["unknown"]),
        },
    }


def render_audit_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Atlas Coverage Audit",
        "",
        f"- Validation: **{report.get('validation')}**",
        f"- Project: `{report.get('project_name')}`",
        f"- Expected paths: **{report.get('counts', {}).get('expected_paths', 0)}**",
        f"- Missing paths: **{report.get('counts', {}).get('missing_paths', 0)}**",
        f"- Missing important: **{report.get('counts', {}).get('missing_important', 0)}**",
        "",
    ]
    for title, values in (
        ("Missing important", report.get("missing_important", [])),
        ("Critical missing", report.get("missing_classification", {}).get("critical", [])),
        ("Unknown missing", report.get("missing_classification", {}).get("unknown", [])),
    ):
        if values:
            lines.extend([f"## {title}", ""])
            lines.extend(f"- `{value}`" for value in values[:200])
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def save_audit(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "atlas_coverage_audit.json"
    md_path = output_dir / "atlas_coverage_audit.md"
    write_json(json_path, report)
    write_text(md_path, render_audit_markdown(report))
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Code Atlas coverage audit.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--atlas", action="append", default=[])
    parser.add_argument("--meta", action="append", default=[])
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--out", default="reports/atlas_plus")
    args = parser.parse_args(argv)
    report = run_audit(CoverageAuditConfig(Path(args.project_root), tuple(Path(x) for x in args.atlas), tuple(Path(x) for x in args.meta), tuple(Path(x) for x in args.package), Path(args.out)))
    _, md = save_audit(report, Path(args.out))
    print(f"Atlas Coverage Audit: {report['validation']} -> {md}")
    return 0 if report["validation"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
