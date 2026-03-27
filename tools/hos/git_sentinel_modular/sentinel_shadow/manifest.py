from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..shared.status_payloads import utc_now_iso

def read_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_manifest(path: str | Path, payload: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target

def build_run_manifest(workspace, run_id: str | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata_root = Path(workspace.metadata_root if hasattr(workspace, "metadata_root") else Path(workspace) / "metadata")
    workspace_root = Path(workspace.workspace_root if hasattr(workspace, "workspace_root") else workspace)
    payload = {
        "run_id": run_id or getattr(workspace, "run_id", workspace_root.name),
        "workspace_root": str(workspace_root),
        "created_at": utc_now_iso(),
    }
    if extra:
        payload.update(extra)
    write_manifest(metadata_root / "run_manifest.json", payload)
    return payload
