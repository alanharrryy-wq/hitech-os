from __future__ import annotations

from pathlib import Path
from typing import Iterable

from synapse_x.models import FileFingerprint
from synapse_x.storage import get_file_state
from synapse_x.utils import file_mtime_iso, sha256_file


def fingerprint_path(path: Path) -> FileFingerprint:
    stat = path.stat()
    return FileFingerprint(
        path=str(path),
        size_bytes=stat.st_size,
        mtime_utc=file_mtime_iso(path),
        content_hash=sha256_file(path),
    )


def has_changed(conn, path: Path, *, full: bool = False) -> bool:
    if full:
        return True
    state = get_file_state(conn, str(path))
    if state is None:
        return True
    fingerprint = fingerprint_path(path)
    return any(
        (
            state["size_bytes"] != fingerprint.size_bytes,
            state["mtime_utc"] != fingerprint.mtime_utc,
            state["content_hash"] != fingerprint.content_hash,
            state["ingest_status"] != "ok",
        )
    )


def collect_changed_files(conn, candidates: Iterable[Path], *, full: bool = False) -> list[Path]:
    changed: list[Path] = []
    for path in candidates:
        if has_changed(conn, path, full=full):
            changed.append(path)
    return sorted(changed)
