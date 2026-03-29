from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

def _sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def snapshot_tree(root: str | Path) -> dict[str, dict[str, Any]]:
    root_path = Path(root)
    if not root_path.exists():
        return {}
    snapshot: dict[str, dict[str, Any]] = {}
    for file_path in sorted(path for path in root_path.rglob("*") if path.is_file()):
        relpath = file_path.relative_to(root_path).as_posix()
        snapshot[relpath] = {
            "sha256": _sha256(file_path),
            "size": file_path.stat().st_size,
        }
    return snapshot

def build_diff(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> dict[str, Any]:
    before_keys = set(before)
    after_keys = set(after)
    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    changed = sorted(path for path in before_keys & after_keys if before[path] != after[path])
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "counts": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "total_touched": len(added) + len(removed) + len(changed),
        },
    }

def write_diff_manifest(workspace_root: str | Path, before_root: str | Path, after_root: str | Path) -> dict[str, Any]:
    workspace_path = Path(workspace_root)
    payload = build_diff(snapshot_tree(before_root), snapshot_tree(after_root))
    output = workspace_path / "metadata" / "diff_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload
