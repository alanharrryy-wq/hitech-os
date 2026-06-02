# PRISMO Learning Core V1.1 F2
# Generated package: prismo learn2 3005 1100 fix1
# Operation model: evidence-intake-real, local store writes only, read-only against repo/DB/secrets.
# This file intentionally uses only Python standard library modules.

"""Main evidence ingestion entry points.

F2 improves prioritization and records more deterministic metadata, but remains compatible
with F1 imports.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Iterable
from .constants import MAX_TEXT_BYTES
from .evidence_classifier import classify_record, classify_zip_inventory
from .evidence_registry import upsert_evidence, save_registry, load_registry
from .file_fingerprints import fingerprint_file
from .paths import allowed_roots
from .reports import write_ingestion_reports
from .safety import is_forbidden_path, is_metadata_only
from .text_extractors import extract_text
from .zip_inspector import inspect_zip


def iter_candidates(root: Path, max_files: int = 3000) -> Iterable[Path]:
    count = 0
    for path in root.rglob("*"):
        if count >= max_files:
            break
        if not path.is_file():
            continue
        if is_forbidden_path(path):
            continue
        count += 1
        yield path


def _merge_intake_flags(record: dict[str, Any], path: Path) -> dict[str, Any]:
    record = dict(record)
    record.setdefault("source_path", str(path))
    record.setdefault("safe_source_label", path.name)
    record.setdefault("read_only", True)
    record.setdefault("mutation_allowed", False)
    record.setdefault("store_write", "local_learning_store_only")
    warnings = list(record.get("warnings") or [])
    if record.get("secret_scan", {}).get("has_secret_like_pattern"):
        warnings.append("secret_like_pattern_redacted")
    record["warnings"] = sorted(set(warnings))
    return record


def ingest_zip(path: str | Path, base: str | Path | None = None) -> dict[str, Any]:
    p = Path(path)
    report = inspect_zip(p)
    record = classify_zip_inventory(report)
    record.update(fingerprint_file(p))
    record["zip_report"] = {
        "entry_count": report.get("entry_count"),
        "total_uncompressed_bytes": report.get("total_uncompressed_bytes"),
        "manifest_entries": report.get("manifest_entries", [])[:30],
        "report_entries": report.get("report_entries", [])[:30],
        "playwright_entries": report.get("playwright_entries", [])[:30],
        "forbidden_entries": report.get("forbidden_entries", [])[:30],
        "status": report.get("status"),
        "classes": report.get("classes", []),
        "warnings": report.get("warnings", []),
    }
    return upsert_evidence(_merge_intake_flags(record, p), base=base)


def ingest_path(path: str | Path, base: str | Path | None = None) -> dict[str, Any]:
    p = Path(path)
    if p.suffix.lower() == ".zip":
        return ingest_zip(p, base=base)
    fp = fingerprint_file(p)
    if not fp.get("metadata_only") and not is_metadata_only(p):
        extracted = extract_text(p, max_bytes=MAX_TEXT_BYTES)
        fp["preview"] = extracted.get("text", "")[:3000]
        fp["secret_scan"] = extracted.get("secret_scan")
        fp["text_signals"] = extracted.get("signals") or {}
    return upsert_evidence(_merge_intake_flags(classify_record(fp), p), base=base)


def ingest_all(repo_root: str | Path | None = None, base: str | Path | None = None, max_files_per_root: int = 1200) -> dict[str, Any]:
    roots = allowed_roots(repo_root)
    inserted: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for root in roots:
        for path in iter_candidates(root, max_files=max_files_per_root):
            try:
                inserted.append(ingest_path(path, base=base))
            except Exception as exc:
                errors.append({"path": str(path), "error": str(exc)})
    registry = load_registry(base)
    save_registry(registry, base)
    report = {"ok": True, "roots": [str(r) for r in roots], "inserted": len(inserted), "errors": errors[:100], "read_only": True, "mutation_allowed": False}
    write_ingestion_reports(report, base=base)
    return report
