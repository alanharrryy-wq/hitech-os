from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

def hash_directory(root: str | Path) -> dict[str, str]:
    root_path = Path(root)
    if not root_path.exists():
        return {}
    payload: dict[str, str] = {}
    for file_path in sorted(path for path in root_path.rglob("*") if path.is_file()):
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        payload[file_path.relative_to(root_path).as_posix()] = digest
    return payload

def detect_drift(expected_snapshot: dict[str, str], current_root: str | Path) -> dict[str, Any]:
    current = hash_directory(current_root)
    expected_keys = set(expected_snapshot)
    current_keys = set(current)
    added = sorted(current_keys - expected_keys)
    removed = sorted(expected_keys - current_keys)
    changed = sorted(
        path for path in expected_keys & current_keys if expected_snapshot[path] != current[path]
    )
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "drift_detected": bool(added or removed or changed),
    }
