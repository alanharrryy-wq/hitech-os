from __future__ import annotations

import hashlib
from pathlib import Path

def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _file_state(path: str | Path) -> dict:
    file_path = Path(path)
    return {"sha256": _sha256(file_path), "size": file_path.stat().st_size}

def snapshot_target_paths(target_root: str | Path) -> dict[str, dict]:
    root = Path(target_root)
    if not root.exists():
        return {}
    return {file_path.relative_to(root).as_posix(): _file_state(file_path) for file_path in root.rglob("*") if file_path.is_file()}
