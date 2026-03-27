from __future__ import annotations

from pathlib import Path
import shutil

from .path_guard import resolve_target_path

def execute_plan(plan: dict, target_root: str | Path, *, do_execute: bool = False) -> dict:
    target = Path(target_root)
    target.mkdir(parents=True, exist_ok=True)
    applied = 0
    for action in plan.get("actions", []):
        destination = resolve_target_path(target, action["relpath"])
        if not do_execute:
            continue
        if action["action"] == "delete":
            destination.unlink(missing_ok=True)
        else:
            source = Path(action["source"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        applied += 1
    return {
        "status": "executed" if do_execute else "planned_only",
        "applied": applied,
        "planned_actions": len(plan.get("actions", [])),
    }
