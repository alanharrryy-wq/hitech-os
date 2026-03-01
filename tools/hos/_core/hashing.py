#!/usr/bin/env python3
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Iterable

from .stable_json import dump_json

DEFAULT_IGNORE_DIRS: tuple[str, ...] = (
    ".git",
    ".next",
    ".turbo",
    "node_modules",
    "__pycache__",
)


def sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path, chunk_size: int = 1024 * 64) -> str:
    hasher = sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _iter_files(root: Path, ignore_dirs: Iterable[str]) -> list[Path]:
    ignored = set(ignore_dirs)
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in ignored for part in path.parts):
            continue
        files.append(path)
    files.sort(key=lambda item: item.relative_to(root).as_posix())
    return files


def hash_directory(root: Path, ignore_dirs: Iterable[str] = DEFAULT_IGNORE_DIRS) -> str:
    root = root.resolve()
    hasher = sha256()
    for file_path in _iter_files(root, ignore_dirs=ignore_dirs):
        rel = file_path.relative_to(root).as_posix().encode("utf-8")
        hasher.update(rel)
        hasher.update(b"\n")
        hasher.update(sha256_file(file_path).encode("ascii"))
        hasher.update(b"\n")
    return hasher.hexdigest()


def hash_json_stable(data: object) -> str:
    return sha256_text(dump_json(data, indent=2, sort_keys=True))

