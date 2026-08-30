from __future__ import annotations

from pathlib import Path

_ALLOWED_SUFFIXES = {".db", ".sqlite", ".sqlite3"}


def owned_sqlite_path(path: Path, data_root: Path, label: str) -> Path:
    root = data_root.resolve()
    candidate = path.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"BLOCKED_DB_PATH_ESCAPE:{label}:{candidate}") from exc
    if candidate.suffix.lower() not in _ALLOWED_SUFFIXES:
        raise RuntimeError(f"BLOCKED_NON_SQLITE_DB:{label}:{candidate.name}")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate


def sqlite_url(path: Path, data_root: Path, label: str) -> str:
    safe = owned_sqlite_path(path, data_root, label)
    return "file:" + safe.as_posix()


def validate_database_url(url: str, data_root: Path, label: str) -> Path:
    if not url.startswith("file:"):
        raise RuntimeError(f"BLOCKED_NON_FILE_DATABASE_URL:{label}")
    raw = url[len("file:"):]
    if not raw:
        raise RuntimeError(f"BLOCKED_EMPTY_DATABASE_URL:{label}")
    return owned_sqlite_path(Path(raw), data_root, label)
