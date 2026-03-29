from __future__ import annotations

from pathlib import Path
import json

def load_workspace_context(workspace_root: str | Path) -> dict:
    workspace = Path(workspace_root)
    diff_manifest = json.loads((workspace / "metadata" / "diff_manifest.json").read_text(encoding="utf-8"))
    return {
        "workspace_root": str(workspace),
        "candidate_root": str(workspace / "candidate"),
        "diff_manifest": diff_manifest,
    }
