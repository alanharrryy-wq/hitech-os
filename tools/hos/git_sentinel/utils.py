#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path


def now_utc_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def to_posix(path: Path) -> str:
    return path.as_posix()


def rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def path_matches_glob(path_text: str, pattern: str) -> bool:
    normalized = path_text.replace("\\", "/").strip("/")
    normalized_pattern = pattern.replace("\\", "/").strip("/")
    return fnmatch.fnmatch(normalized, normalized_pattern)


def path_matches_any(path_text: str, patterns: list[str]) -> bool:
    return any(path_matches_glob(path_text=path_text, pattern=pattern) for pattern in patterns)


def is_within(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def is_binary_file(path: Path, read_bytes: int = 4096) -> bool:
    try:
        with path.open("rb") as handle:
            sample = handle.read(read_bytes)
    except OSError:
        return False
    if not sample:
        return False
    if b"\x00" in sample:
        return True
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
    return bool(sample.translate(None, text_chars))


def safe_unlink(path: Path) -> bool:
    try:
        path.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def safe_rmdir(path: Path) -> bool:
    try:
        path.rmdir()
        return True
    except OSError:
        return False


def ensure_dir(path: Path) -> None:
    os.makedirs(path, exist_ok=True)

