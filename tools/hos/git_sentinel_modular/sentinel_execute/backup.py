from __future__ import annotations

from pathlib import Path
import shutil

def create_backup(target_root: str | Path, execution_dir: str | Path) -> Path:
    target = Path(target_root)
    backup_dir = Path(execution_dir) / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    if target.exists():
        for item in target.rglob("*"):
            relative = item.relative_to(target)
            destination = backup_dir / relative
            if item.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, destination)
    return backup_dir
