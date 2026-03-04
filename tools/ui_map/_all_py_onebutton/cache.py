from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .io_utils import load_json, write_json


class SimpleCache:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, Any] = {}
        if path.exists():
            raw = load_json(path)
            if isinstance(raw, dict):
                self.data = raw

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def save(self) -> None:
        write_json(self.path, self.data)


def fingerprint_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix().lower()):
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()
