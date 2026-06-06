from __future__ import annotations

import argparse
import json
import os
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from code_atlas.core.io_utils import (
    DEFAULT_IGNORE_DIRS,
    human_bytes,
    iter_project_files,
    read_json,
    safe_rel,
    sha256_file,
    write_json,
    write_text,
    zip_entries,
    iso_now,
)

PATH_KEY_RE = re.compile(r"(?i)(path|file|entry|relative|rel|relpath|source|target)$")
IMPORTANT_KEY_RE = re.compile(r"(?i)(important|entrypoint|critical|required|must|gate)")
VIRTUAL_OR_NOISE = {
    ".clock", ".sanitize", ".memory_store", ".rollback_planner", ".secret_scanner", ".zip_inspector",
}
NOISE_PREFIXES = (".next/", "node_modules/", "__pycache__/", ".git/", "_dependency_graphs/")
DISCOVERY_IGNORE_DIRS = set(DEFAULT_IGNORE_DIRS) - {"_dependency_graphs"}
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
    # Normalize common archive wrappers without hiding the original matching behavior.
    if text.startswith("project/"):
        text = text.split("/", 1)[1]
    return text


def _looks_like_file_path(value: Any) -> bool:
    text = _norm_path(value)
    if not text or text in VIRTUAL_OR_NOISE:
        return False
    if "\n" in text or "\r" in text or len(text) > 500:
        return False
    if text.startswith(("http://", "https://", "data:")):
        return False
    return ("/" in text) or bool(re.search(r"\.[A-Za-z0-9]{1,14}$", text))


def _walk_json_paths(data: Any, *, mode: str, key_stack: tuple[str, ...] = ()) -> set[str]:
    found: set[str] = set()
    stack_text = "/".join(key_stack)
    important_context = bool(IMPORTANT_KEY_RE.search(stack_text))

    if isinstance(data, dict):
        for key, value in data.items():
            k = str(key)
            pathish_key = bool(PATH_KEY_RE.search(k))
            if isinstance(value, str) and (pathish_key or important_context or mode == "kept") and _looks_like_file_path(value):
                found.add(_norm_path(value))
            elif isinstance(value, list) and (important_context or mode == "kept"):
                for item in value:
                    if isinstance(item, str) and _looks_like_file_path(item):
                        found.add(_norm_path(item))
                    elif isinstance(item, dict):
                        found.update(_walk_json_paths(item, mode=mode, key_stack=key_stack + (k,)))
            found.update(_walk_json_paths(value, mode=mode, key_stack=key_stack + (k,)))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str) and mode == "kept" and _looks_like_file_path(item):
                found.add(_norm_path(item))
            elif isinstance(item, dict):
                found.update(_walk_json_paths(item, mode=mode, key_stack=key_stack))
            else:
                found.update(_walk_json_paths(item, mode=mode, key_stack=key_stack))
    return found


def _split_env_paths(name: str) -> list[Path]:
    raw = os.environ.get(name, "")
    out: list[Path] = []
    for chunk in raw.replace("|", os.pathsep).split(os.pathsep):
        chunk = chunk.strip().strip('"').strip("'")
        if chunk:
            out.append(Path(chunk))
    return out


def _candidate_context_roots(project_root: Path) -> list[Path]:
    roots: list[Path] = []
    explicit_roots = (
        _split_env_paths("CODE_ATLAS_CONTEXT_ROOTS")
        + _split_env_paths("CODE_ATLAS_META_ROOTS")
        + _split_env_paths("CODE_ATLAS_ATLAS_ROOTS")
    )
    roots.extend(explicit_roots)
    roots.append(project_root)
    # Parents are useful on Windows repo layouts, but do not climb to the
    # filesystem root. Scanning `/`, `/tmp`, or an entire drive turns meta
    # discovery into a garbage vacuum. Keep nearby ancestors only on Windows.
    if os.name == "nt":
        for parent in list(project_root.parents)[:4]:
            if parent == parent.parent:
                continue
            roots.append(parent)
    roots.extend([
        project_root / "_dependency_graphs",
        project_root / "evidence",
        project_root / "reports",
        Path(r"F:\PRISMA_CTX"),
        Path(r"F:\PRISMA_CTX\00_ALL\ALV"),
        Path(r"F:\descargasf"),
    ])
    seen: set[str] = set()
    final: list[Path] = []
    for root in roots:
        try:
            resolved = root.expanduser().resolve()
        except Exception:
            resolved = root
        key = str(resolved).lower()
        if key in seen:
            continue
        seen.add(key)
        if resolved.exists() and resolved.is_dir():
            final.append(resolved)
    return final


def _iter_candidate_files(root: Path) -> Iterable[Path]:
    emitted = 0
    if root.is_file():
        yield root
        return
    # Downloads can be huge; keep it shallow unless user explicitly points deeper.
    shallow = str(root).lower().rstrip("\\/") == r"f:\descargasf".lower().rstrip("\\/")
    try:
        if shallow:
            for p in sorted(root.glob("*")):
                if p.is_file() and p.suffix.lower() in {".json", ".zip"}:
                    yield p
            return
        for current, dirs, files in os.walk(root):
            current_path = Path(current)
            dirs[:] = sorted(d for d in dirs if d.lower() not in {x.lower() for x in DISCOVERY_IGNORE_DIRS})
            for name in sorted(files):
                p = current_path / name
                if p.suffix.lower() not in {".json", ".zip"}:
                    continue
                yield p
                emitted += 1
                if emitted >= MAX_DISCOVERY_FILES_PER_ROOT:
                    return
    except OSError:
        return


def _is_atlas_name(path_text: str) -> bool:
    text = path_text.lower().replace("\\", "/")
    name = Path(text).name
    return any(token in name or token in text for token in (
        "atlas", "dependency_graph", "dependency-map", "dependency_map", "graph.json", "summary.json",
    ))


def _is_meta_name(path_text: str) -> bool:
    text = path_text.lower().replace("\\", "/")
    name = Path(text).name
    return any(token in name or token in text for token in (
        "kept", "manifest", "checksum", "checksums", "todoalv", "meta", "summary",
    )) and "excluded" not in name


def _is_package_name(path_text: str) -> bool:
    text = path_text.lower().replace("\\", "/")
    name = Path(text).name
    if not name.endswith(".zip"):
        return False
    if any(bad in name for bad in ("fail", "result", "diagnostic", "meta")):
        return False
    return any(token in name for token in ("todoalv", "code-atlas", "catlas"))


def discover_coverage_sources(root: Path) -> tuple[list[Path], list[Path], list[Path], list[str]]:
    """Auto-discover atlas/meta/package evidence around the project.

    This is intentionally conservative: it prefers explicit env roots, the selected
    project, `_dependency_graphs`, `evidence`, `F:\\PRISMA_CTX`, and top-level
    `F:\\descargasf`. It avoids treating random capatch/report manifests as truth.
    """
    atlas: dict[str, Path] = {}
    meta: dict[str, Path] = {}
    packages: dict[str, Path] = {}
    notes: list[str] = []
    roots = _candidate_context_roots(root)
    for scan_root in roots:
        for p in _iter_candidate_files(scan_root):
            try:
                rel_text = p.name.lower() if scan_root == p.parent else safe_rel(p, scan_root).lower()
            except Exception:
                rel_text = p.name.lower()
            abs_key = str(p.resolve()).lower()
            trusted_zone = (
                "_dependency_graphs" in rel_text
                or rel_text.startswith("evidence/")
                or "todoalv" in rel_text
                or "atlas" in rel_text
                or "kept" in rel_text
                or "meta" in rel_text
                or p.name.lower() in {"kept.json", "atlas.json", "dependency_graph.json", "dependency_map.json"}
            )
            if p.suffix.lower() == ".zip":
                if _is_package_name(str(p)):
                    packages[abs_key] = p.resolve()
                if trusted_zone and _is_meta_name(str(p)):
                    meta[abs_key] = p.resolve()
                if trusted_zone and _is_atlas_name(str(p)):
                    atlas[abs_key] = p.resolve()
                continue
            if p.suffix.lower() != ".json":
                continue
            if not trusted_zone:
                continue
            if rel_text.startswith("capatch_system/.capatch/") or "/.capatch/" in rel_text:
                continue
            if "/reports/" in rel_text and not any(t in rel_text for t in ("atlas", "todoalv", "kept", "meta")):
                continue
            if _is_atlas_name(str(p)):
                atlas[abs_key] = p.resolve()
            if _is_meta_name(str(p)):
                meta[abs_key] = p.resolve()
    if roots:
        notes.append("auto_discovery_roots=" + "; ".join(str(r) for r in roots[:12]))
    return list(atlas.values())[:80], list(meta.values())[:120], list(packages.values())[:80], notes


def _zip_json_entry_wanted(entry: zipfile.ZipInfo, *, kind: str) -> bool:
    name = entry.filename.replace("\\", "/")
    lower = name.lower()
    base = Path(lower).name
    if not lower.endswith(".json"):
        return False
    if "excluded" in base or entry.file_size > MAX_JSON_BYTES_FROM_ZIP:
        return False
    if kind == "atlas":
        return _is_atlas_name(lower)
    if kind == "meta":
        return _is_meta_name(lower)
    return False


def _load_json_sources(paths: Iterable[Path], *, kind: str) -> list[tuple[str, Any, str]]:
    out: list[tuple[str, Any, str]] = []
    for path in paths:
        try:
            p = Path(path)
            if p.suffix.lower() == ".zip":
                with zipfile.ZipFile(p, "r", allowZip64=True) as zf:
                    matched = [i for i in zf.infolist() if _zip_json_entry_wanted(i, kind=kind)]
                    if not matched:
                        out.append((str(p), None, "zip_ok_no_matching_json"))
                    for info in matched:
                        try:
                            data = json.loads(zf.read(info).decode("utf-8", errors="replace"))
                            out.append((f"{p}::{info.filename}", data, "ok"))
                        except Exception as exc:
                            out.append((f"{p}::{info.filename}", None, f"error: {exc}"))
                continue
            out.append((str(p), read_json(p), "ok"))
        except Exception as exc:
            out.append((str(path), None, f"error: {exc}"))
    return out


def _project_file_records(root: Path) -> dict[str, dict[str, Any]]:
    records = {}
    for p in iter_project_files(root):
        rel = _norm_path(safe_rel(p, root))
        try:
            records[rel] = {"size": p.stat().st_size, "sha256": sha256_file(p)}
        except Exception:
            records[rel] = {"size": 0, "sha256": ""}
    return records


def _path_match_variants(path: str, root_name: str = "") -> set[str]:
    norm = _norm_path(path)
    variants = {norm}
    parts = norm.split("/")
    if len(parts) > 1:
        variants.add(parts[-1])
        variants.add("/".join(parts[1:]))
    if root_name and norm.startswith(root_name + "/"):
        variants.add(norm.split("/", 1)[1])
    return {v for v in variants if v}


def _strict_project_overlap(candidate_paths: Iterable[str], physical_files: set[str], root_name: str = "") -> tuple[int, int, list[str]]:
    """Return exact project overlap for auto-discovered global evidence.

    This deliberately avoids basename-only matching. A giant global META can
    contain many generic names such as ``app.py`` or ``schema.prisma``; counting
    those as overlap poisoned the smoke test. Global sources are accepted only
    when they match real relative project paths, optionally after stripping the
    selected project folder name as an archive wrapper.
    """
    physical_norm = {_norm_path(p) for p in physical_files if _norm_path(p)}
    matched: set[str] = set()
    checked = 0
    wrapper = _norm_path(root_name)

    for raw in candidate_paths or ():
        path = _norm_path(raw)
        if not path:
            continue
        checked += 1
        probes = {path}
        if wrapper and path.startswith(wrapper + "/"):
            probes.add(path.split("/", 1)[1])
        # Common archive wrappers created by context bundles.
        for prefix in ("project/", "payload/", "repo/", "root/"):
            if path.startswith(prefix):
                probes.add(path.split("/", 1)[1])
        hit = probes & physical_norm
        if hit:
            matched.update(hit)

    return len(matched), checked, sorted(matched)[:40]


def _path_set_overlap(candidate_paths: Iterable[str], physical_files: set[str], root_name: str = "") -> int:
    # Backward-compatible helper, now strict enough for source acceptance.
    return _strict_project_overlap(candidate_paths, physical_files, root_name)[0]


def _source_is_local_to_project(source_id: str, root: Path) -> bool:
    """Return True when a source is inside the selected project root."""
    raw = source_id.split("::", 1)[0]
    try:
        Path(raw).resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def _should_accept_auto_source(
    *,
    source_id: str,
    extracted_paths: set[str],
    physical_files: set[str],
    root: Path,
    explicit: bool,
    kind: str,
) -> tuple[bool, str]:
    """Decide whether an auto-discovered source belongs to this project.

    Explicit sources are always trusted. Local sources are trusted. Global
    sources must overlap the selected project unless they are tiny enough to be
    harmless. This fixes the final3 failure where the self-test fixture found
    TodoALV META from downloads and compared four fixture files against
    thousands of unrelated kept paths.
    """
    if explicit:
        return True, "accepted_explicit"
    if not extracted_paths:
        return True, "accepted_no_paths"
    if _source_is_local_to_project(source_id, root):
        return True, "accepted_local_project_source"

    overlap, checked, matches = _strict_project_overlap(extracted_paths, physical_files, root.name)
    # Global auto-discovered sources must prove they belong to the selected
    # project. One or two generic matches are too weak; real META/package files
    # from the same project produce many exact relative-path matches.
    required_overlap = max(3, min(12, max(1, len(physical_files) // 80)))
    if overlap >= required_overlap:
        return True, f"accepted_auto_project_overlap_{overlap}_of_{checked}_required_{required_overlap}"

    # Tiny non-meta atlas files may be harmless, but only with at least one
    # strict project match. META/package sources stay strict because they can
    # contain thousands of unrelated paths.
    if kind == "atlas" and len(extracted_paths) <= 8 and overlap >= 1:
        return True, f"accepted_small_auto_atlas_overlap_{overlap}"

    return False, f"skipped_incompatible_auto_source_overlap_{overlap}_of_{checked}_required_{required_overlap}"


def _package_entries(path: Path) -> set[str]:
    entries: set[str] = set()
    try:
        for entry in zip_entries(path):
            norm = _norm_path(entry)
            if not norm:
                continue
            entries.add(norm)
            parts = norm.split("/", 1)
            if len(parts) == 2:
                entries.add(parts[1])
    except Exception:
        pass
    return entries


def _filtered_package_file_set(
    package_paths: Iterable[Path],
    *,
    physical_files: set[str],
    root: Path,
    explicit: bool,
    source_status: list[dict[str, str]] | None = None,
) -> set[str]:
    files: set[str] = set()
    for zp in package_paths:
        entries = _package_entries(zp)
        if not entries:
            if source_status is not None:
                source_status.append({"kind": "package", "path": str(zp), "status": "zip_ok_no_entries"})
            continue
        accepted, reason = _should_accept_auto_source(
            source_id=str(zp),
            extracted_paths=entries,
            physical_files=physical_files,
            root=root,
            explicit=explicit,
            kind="package",
        )
        if source_status is not None:
            source_status.append({"kind": "package", "path": str(zp), "status": reason, "entries": str(len(entries))})
        if accepted:
            files.update(entries)
    return files


def _package_file_set(package_paths: Iterable[Path]) -> set[str]:
    # Backward-compatible helper retained for external callers.
    files: set[str] = set()
    for zp in package_paths:
        files.update(_package_entries(zp))
    return files


def classify_missing(paths: Iterable[str]) -> dict[str, list[str]]:
    result = {"critical": [], "generated_or_cache": [], "virtual_or_noise": [], "unknown": []}
    for path in sorted({_norm_path(p) for p in paths if _norm_path(p)}):
        lower = path.lower()
        if path in VIRTUAL_OR_NOISE or lower.split("/", 1)[0] in VIRTUAL_OR_NOISE:
            result["virtual_or_noise"].append(path)
        elif lower.startswith(NOISE_PREFIXES) or "/.next/" in lower or "/node_modules/" in lower:
            result["generated_or_cache"].append(path)
        elif re.search(r"(?i)(schema\.prisma|migration|seed|database|sqlite|\.db$|\.sqlite|code-atlas\.py|visualgdeep\.py|tools/|src/)", path):
            result["critical"].append(path)
        else:
            result["unknown"].append(path)
    return result


def run_audit(config: CoverageAuditConfig) -> dict[str, Any]:
    root = config.project_root.resolve()
    atlas_paths = list(config.atlas_paths)
    meta_paths = list(config.meta_paths)
    package_paths = list(config.package_paths)
    discovery_notes: list[str] = []
    if not atlas_paths and not meta_paths and not package_paths:
        discovered_atlas, discovered_meta, discovered_packages, discovery_notes = discover_coverage_sources(root)
        atlas_paths = discovered_atlas
        meta_paths = discovered_meta
        package_paths = discovered_packages

    project_records = _project_file_records(root)
    physical_files = set(project_records)

    important: set[str] = set()
    atlas_nodes: set[str] = set()
    kept: set[str] = set()
    source_status: list[dict[str, str]] = []

    package_files = _filtered_package_file_set(
        package_paths,
        physical_files=physical_files,
        root=root,
        explicit=bool(config.package_paths),
        source_status=source_status,
    )
    physical_plus_packages = physical_files | package_files

    for source_id, data, status in _load_json_sources(atlas_paths, kind="atlas"):
        if data is None:
            source_status.append({"kind": "atlas", "path": source_id, "status": status})
            continue
        extracted_important = _walk_json_paths(data, mode="important")
        extracted_nodes = _walk_json_paths(data, mode="kept")
        extracted_all = extracted_important | extracted_nodes
        accepted, reason = _should_accept_auto_source(
            source_id=source_id,
            extracted_paths=extracted_all,
            physical_files=physical_files,
            root=root,
            explicit=bool(config.atlas_paths),
            kind="atlas",
        )
        source_status.append({"kind": "atlas", "path": source_id, "status": f"{status}; {reason}"})
        if not accepted:
            continue
        important.update(extracted_important)
        atlas_nodes.update(extracted_nodes)

    for source_id, data, status in _load_json_sources(meta_paths, kind="meta"):
        if data is None:
            source_status.append({"kind": "meta", "path": source_id, "status": status})
            continue
        extracted_kept = _walk_json_paths(data, mode="kept")
        accepted, reason = _should_accept_auto_source(
            source_id=source_id,
            extracted_paths=extracted_kept,
            physical_files=physical_files,
            root=root,
            explicit=bool(config.meta_paths),
            kind="meta",
        )
        source_status.append({"kind": "meta", "path": source_id, "status": f"{status}; {reason}"})
        if not accepted:
            continue
        kept.update(extracted_kept)

    # If no external atlas was present, create a pragmatic important set from this project.
    if not important:
        for candidate in ("code-atlas.py", "visualgdeep.py", "tools/code_atlas_dependency_map_bridge.py"):
            if candidate in physical_files:
                important.add(candidate)
        for rel in physical_files:
            if rel.startswith("src/code_atlas/") and rel.endswith(".py"):
                important.add(rel)
            if rel.startswith("tools/") and rel.endswith(".py"):
                important.add(rel)
            if "schema.prisma" in rel.lower():
                important.add(rel)

    def _missing(paths: Iterable[str]) -> list[str]:
        out: list[str] = []
        root_name = root.name
        for p in paths:
            variants = _path_match_variants(p, root_name)
            if not (variants & physical_plus_packages):
                out.append(_norm_path(p))
        return sorted(set(out))

    missing_important = _missing(important)
    missing_atlas_nodes = _missing(atlas_nodes)
    missing_kept = _missing(kept)
    extras = sorted(physical_files - kept) if kept else []

    missing_classes = classify_missing(set(missing_important) | set(missing_atlas_nodes) | set(missing_kept))
    meta_mode = "explicit" if config.meta_paths else ("auto" if meta_paths else "fallback")
    atlas_mode = "explicit" if config.atlas_paths else ("auto" if atlas_paths else "fallback")

    report = {
        "kind": "atlas_coverage_audit_v2_meta_auto",
        "created_at": iso_now(),
        "project_root": str(root),
        "discovery": {
            "atlas_mode": atlas_mode,
            "meta_mode": meta_mode,
            "package_mode": "explicit" if config.package_paths else ("auto" if package_paths else "none"),
            "notes": discovery_notes,
            "atlas_candidates": [str(p) for p in atlas_paths],
            "meta_candidates": [str(p) for p in meta_paths],
            "package_candidates": [str(p) for p in package_paths],
        },
        "sources": source_status,
        "counts": {
            "project_files": len(physical_files),
            "package_files": len(package_files),
            "important_paths": len(important),
            "atlas_nodes": len(atlas_nodes),
            "kept_paths": len(kept),
            "missing_important": len(missing_important),
            "missing_atlas_nodes": len(missing_atlas_nodes),
            "missing_kept": len(missing_kept),
            "extras_vs_kept": len(extras),
        },
        "validation": "PASS" if not missing_important and not missing_kept else "FAIL",
        "important_paths": sorted(important),
        "missing_important": missing_important,
        "missing_atlas_nodes": missing_atlas_nodes,
        "missing_kept": missing_kept,
        "missing_classification": missing_classes,
        "extras_vs_kept_sample": extras[:500],
        "physical_file_sample": sorted(physical_files)[:500],
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    discovery = report.get("discovery", {})
    lines = [
        "# Atlas Coverage Audit",
        "",
        f"- Project: `{report.get('project_root')}`",
        f"- Validation: **{report.get('validation')}**",
        f"- Meta mode: **{discovery.get('meta_mode', 'unknown')}**",
        f"- Atlas mode: **{discovery.get('atlas_mode', 'unknown')}**",
        f"- Package mode: **{discovery.get('package_mode', 'unknown')}**",
        f"- Project files: **{counts.get('project_files', 0)}**",
        f"- Package files: **{counts.get('package_files', 0)}**",
        f"- Important paths: **{counts.get('important_paths', 0)}**",
        f"- Missing important: **{counts.get('missing_important', 0)}**",
        f"- Kept paths from META: **{counts.get('kept_paths', 0)}**",
        f"- Missing kept paths: **{counts.get('missing_kept', 0)}**",
        f"- Atlas nodes: **{counts.get('atlas_nodes', 0)}**",
        f"- Missing atlas nodes: **{counts.get('missing_atlas_nodes', 0)}**",
        "",
        "## Sources",
        "",
    ]
    for src in report.get("sources", []):
        lines.append(f"- `{src.get('kind')}` `{src.get('path')}`: {src.get('status')}")
    if not report.get("sources"):
        lines.append("- No atlas/meta JSON sources were found; fallback important paths were inferred from project layout.")
    lines += ["", "## Discovery candidates", ""]
    for key in ("atlas_candidates", "meta_candidates", "package_candidates"):
        items = discovery.get(key) or []
        lines.append(f"### {key}")
        lines.append("")
        if items:
            lines.extend(f"- `{p}`" for p in items[:80])
        else:
            lines.append("- None.")
        lines.append("")
    lines += ["## Missing important files", ""]
    missing = report.get("missing_important") or []
    if missing:
        lines.extend(f"- `{p}`" for p in missing)
    else:
        lines.append("- None.")
    lines += ["", "## Missing META kept files", ""]
    missing_kept = report.get("missing_kept") or []
    if missing_kept:
        lines.extend(f"- `{p}`" for p in missing_kept[:300])
    else:
        lines.append("- None.")
    lines += ["", "## Missing classification", ""]
    for key, items in (report.get("missing_classification") or {}).items():
        lines.append(f"### {key}")
        lines.append("")
        if items:
            lines.extend(f"- `{p}`" for p in items[:200])
        else:
            lines.append("- None.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def save_audit(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "atlas_coverage_audit.json"
    md_path = output_dir / "atlas_coverage_audit.md"
    write_json(json_path, report)
    write_text(md_path, render_markdown(report))
    return json_path, md_path


def _parse_paths(values: list[str] | None) -> tuple[Path, ...]:
    return tuple(Path(v) for v in (values or []) if str(v).strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Code Atlas coverage audit.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--atlas", action="append", default=[])
    parser.add_argument("--meta", action="append", default=[])
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--out", default="reports/atlas_plus")
    args = parser.parse_args(argv)

    cfg = CoverageAuditConfig(
        project_root=Path(args.project_root),
        atlas_paths=_parse_paths(args.atlas),
        meta_paths=_parse_paths(args.meta),
        package_paths=_parse_paths(args.package),
        output_dir=Path(args.out),
    )
    report = run_audit(cfg)
    _, md = save_audit(report, Path(args.out))
    print(f"Atlas Coverage Audit: {report['validation']} -> {md}")
    return 0 if report["validation"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
