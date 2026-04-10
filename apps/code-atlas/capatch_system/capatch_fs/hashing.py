from __future__ import annotations

import hashlib
from pathlib import Path


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def hash_file(path_value: Path) -> str | None:
    try:
        return hashlib.sha256(path_value.read_bytes()).hexdigest()
    except Exception:
        return None
