from __future__ import annotations

import json
from pathlib import Path

def _stringify_state(state: dict) -> dict:
    return {key: str(value) for key, value in state.items()}

def load_workspace_state(workspace_root: str | Path) -> dict:
    workspace = Path(workspace_root)
    state = {
        "workspace_root": workspace,
        "review_bundle": workspace / "review_bundle",
        "diff_manifest": workspace / "metadata" / "diff_manifest.json",
    }
    return _stringify_state(state)

def run_preflight(workspace_root: str | Path) -> dict:
    workspace = Path(workspace_root)
    review_dir = workspace / "review_bundle"
    diff_manifest = workspace / "metadata" / "diff_manifest.json"
    ok = review_dir.exists() and diff_manifest.exists()
    return {
        "status": "ready" if ok else "needs_attention",
        "review_bundle_present": review_dir.exists(),
        "diff_manifest_present": diff_manifest.exists(),
    }
