from __future__ import annotations

from pathlib import Path


def normalize_relpath(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()
