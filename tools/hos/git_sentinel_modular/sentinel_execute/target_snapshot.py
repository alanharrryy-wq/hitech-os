from pathlib import Path
import hashlib

from .path_guard import resolve_target_path

def snapshot_target_paths(target_root, relative_paths):
    records = {}
    for relpath in sorted(set(relative_paths)):
        target = resolve_target_path(target_root, relpath)
        records[relpath] = _file_state(target)
    return records

def _file_state(path):
    path = Path(path)
    if not path.exists():
        return {
            "exists": False,
            "type": "missing",
            "size": 0,
            "sha256": None,
        }

    if path.is_dir():
        return {
            "exists": True,
            "type": "dir",
            "size": 0,
            "sha256": None,
        }

    return {
        "exists": True,
        "type": "file",
        "size": path.stat().st_size,
        "sha256": _sha256(path),
    }

def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
