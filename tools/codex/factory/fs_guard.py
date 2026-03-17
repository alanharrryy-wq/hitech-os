from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class WritePolicyError(PermissionError):
    pass


def _resolve(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


class WriteGuard:
    def __init__(self, allowed_root: Path):
        self._allowed_root = _resolve(allowed_root)

    @property
    def allowed_root(self) -> Path:
        return self._allowed_root

    def validate_path(self, target: Path) -> Path:
        resolved = _resolve(target)
        if resolved == self._allowed_root or self._allowed_root in resolved.parents:
            return resolved
        raise WritePolicyError(
            "Z no-write policy violation: "
            f"attempted write outside run root; target={resolved.as_posix()} "
            f"allowed_root={self._allowed_root.as_posix()}"
        )

    def ensure_parent(self, target: Path) -> Path:
        resolved = self.validate_path(target)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        return resolved

    def write_text(self, target: Path, text: str) -> Path:
        resolved = self.ensure_parent(target)
        resolved.write_text(text, encoding="utf-8", newline="\n")
        return resolved

    def write_json(self, target: Path, payload: Any) -> Path:
        rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        return self.write_text(target, rendered)

    def append_line(self, target: Path, line: str) -> Path:
        resolved = self.ensure_parent(target)
        with resolved.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(str(line) + "\n")
        return resolved

