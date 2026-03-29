from __future__ import annotations

def build_rollback_instructions(backup_dir: str, target_root: str) -> dict:
    return {
        "backup_dir": backup_dir,
        "target_root": target_root,
        "steps": [
            "delete changed files from target if needed",
            "restore backup snapshot into target root",
        ],
    }
