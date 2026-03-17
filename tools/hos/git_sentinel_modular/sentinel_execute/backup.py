from pathlib import Path
import shutil
import time

from .manifest_io import write_json
from .path_guard import resolve_target_path

def create_backup(target_root, backup_root, plan_payload):
    target_root = Path(target_root)
    backup_root = Path(backup_root)
    backup_root.mkdir(parents=True, exist_ok=True)

    copied = []
    missing = []

    for action in plan_payload.get("actions", []):
        relpath = action["path"]
        target = resolve_target_path(target_root, relpath)
        backup_target = backup_root / relpath

        if target.exists() and target.is_file():
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_target)
            copied.append(relpath)
        else:
            missing.append(relpath)

    payload = {
        "created_at_epoch": time.time(),
        "target_root": str(target_root),
        "backup_root": str(backup_root),
        "copied": copied,
        "missing": missing,
        "counts": {
            "copied": len(copied),
            "missing": len(missing),
        },
    }

    write_json(backup_root / "backup_manifest.json", payload)
    return payload
