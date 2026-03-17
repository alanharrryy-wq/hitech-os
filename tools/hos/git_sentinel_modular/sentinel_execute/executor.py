from pathlib import Path
import shutil
import time

from .backup import create_backup
from .manifest_io import write_json
from .path_guard import resolve_target_path

def execute_plan(plan_payload, target_root, execution_dir, policy, *, do_execute=False, confirm_token=None):
    target_root = Path(target_root)
    execution_dir = Path(execution_dir)
    execution_dir.mkdir(parents=True, exist_ok=True)

    if plan_payload.get("blocked"):
        return {
            "ok": False,
            "mode": "blocked_before_execution",
            "blocked": plan_payload["blocked"],
            "applied": [],
            "skipped": [],
            "counts": {
                "applied": 0,
                "skipped": 0,
                "blocked": len(plan_payload["blocked"]),
            },
        }, None

    if not do_execute:
        return {
            "ok": True,
            "mode": "dry_run",
            "blocked": [],
            "applied": [],
            "skipped": plan_payload.get("actions", []),
            "counts": {
                "applied": 0,
                "skipped": len(plan_payload.get("actions", [])),
                "blocked": 0,
            },
        }, None

    if policy.get("require_confirm_token", True):
        expected = policy.get("confirm_token")
        if confirm_token != expected:
            raise RuntimeError(
                f"Execution requires confirm token: expected {expected!r}"
            )

    backup_manifest = None
    if policy.get("backup_enabled", True):
        backup_root = execution_dir / policy.get("backup_dir_name", "backups")
        backup_manifest = create_backup(target_root, backup_root, plan_payload)

    applied = []
    skipped = []

    for action in plan_payload.get("actions", []):
        relpath = action["path"]
        op = action["action"]
        source_path = Path(action["source_path"]) if action.get("source_path") else None
        target = resolve_target_path(target_root, relpath)

        if op in ("add", "update"):
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target)
            applied.append({
                "path": relpath,
                "action": op,
                "bytes": source_path.stat().st_size,
            })
        elif op == "delete":
            if target.exists():
                target.unlink()
                applied.append({
                    "path": relpath,
                    "action": op,
                    "bytes": 0,
                })
            else:
                skipped.append({
                    "path": relpath,
                    "action": op,
                    "reason": "target_missing_at_delete_time",
                })

    payload = {
        "ok": True,
        "mode": "execute",
        "executed_at_epoch": time.time(),
        "blocked": [],
        "applied": applied,
        "skipped": skipped,
        "counts": {
            "applied": len(applied),
            "skipped": len(skipped),
            "blocked": 0,
        },
    }

    write_json(execution_dir / "execution_result.raw.json", payload)
    return payload, backup_manifest
