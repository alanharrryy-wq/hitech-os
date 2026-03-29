from __future__ import annotations

from pathlib import Path
import json

def build_rollback_manifest(workspace_root: str | Path) -> dict:
    workspace = Path(workspace_root)
    payload = {
        "workspace_root": str(workspace),
        "rollback_dir": str(workspace / "rollback_bundle"),
        "steps": [
            "restore backup before cutover",
            "rebuild execution bundle after rollback",
        ],
    }
    target = workspace / "rollback_bundle" / "rollback_manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload
