# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Streaming and stable hashes for files, texts and normalized records."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def normalize_for_hash(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): normalize_for_hash(v) for k, v in sorted(obj.items(), key=lambda item: str(item[0]))}
    if isinstance(obj, (list, tuple, set)):
        return [normalize_for_hash(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    return obj


def stable_json_hash(obj: Any) -> str:
    normalized = normalize_for_hash(obj)
    raw = json.dumps(normalized, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return sha256_text(raw)


def short_hash(value: str, size: int = 12) -> str:
    return sha256_text(value)[:max(6, min(32, size))]
