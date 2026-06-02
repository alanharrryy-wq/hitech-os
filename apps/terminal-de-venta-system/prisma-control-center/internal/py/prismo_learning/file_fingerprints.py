# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Operational file fingerprints."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .clock import from_timestamp, freshness_bucket
from .hashes import sha256_file
from .safety import is_metadata_only, is_forbidden_path, safe_to_read_text
from .sanitize import safe_source_label


def fingerprint_file(path: str | Path, root: str | Path | None = None) -> dict[str, Any]:
    p = Path(path)
    try:
        stat = p.stat()
    except Exception as exc:
        return {"path": str(path), "exists": False, "error": str(exc), "safe_to_read": False, "metadata_only": True}
    metadata_only = is_metadata_only(p)
    safe = safe_to_read_text(p)
    record: dict[str, Any] = {
        "exists": True,
        "name": p.name,
        "extension": p.suffix.lower(),
        "size_bytes": stat.st_size,
        "modified_at": from_timestamp(stat.st_mtime),
        "freshness": freshness_bucket(stat.st_mtime),
        "source_path": str(p),
        "safe_source_label": safe_source_label(str(p)),
        "safe_to_read": safe,
        "metadata_only": metadata_only,
        "forbidden": is_forbidden_path(p),
        "sha256": None,
        "warnings": [],
    }
    if root:
        try:
            record["relative_path"] = str(p.resolve().relative_to(Path(root).resolve())).replace("\\", "/")
        except Exception:
            record["relative_path"] = p.name
    else:
        record["relative_path"] = p.name
    if not metadata_only and stat.st_size <= 20 * 1024 * 1024:
        try:
            record["sha256"] = sha256_file(p)
        except Exception as exc:
            record["warnings"].append(f"hash_failed:{exc}")
    if metadata_only:
        record["warnings"].append("metadata_only")
    return record


def fingerprint_many(paths: list[str | Path], root: str | Path | None = None) -> list[dict[str, Any]]:
    return [fingerprint_file(p, root=root) for p in paths]
