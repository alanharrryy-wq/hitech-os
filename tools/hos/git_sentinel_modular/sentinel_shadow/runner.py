from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .diff_manifest import snapshot_tree, write_diff_manifest
from .manifest import build_run_manifest, write_manifest
from .workspace import create_shadow_workspace
from ..sentinel_shadow_apply.safe_paths import assert_safe_relative_path

def prepare_shadow_run(run_id: str, source_root: str | Path | None = None) -> dict[str, Any]:
    workspace = create_shadow_workspace(run_id=run_id, source_root=source_root)
    baseline_snapshot = snapshot_tree(workspace.baseline_root)
    write_manifest(workspace.metadata_root / "baseline_snapshot.json", baseline_snapshot)
    manifest = build_run_manifest(workspace)
    return {**workspace.to_dict(), "manifest": manifest}

def stage_candidate_overlay(workspace_root: str | Path, overlay_plan: list[dict[str, Any]]) -> dict[str, Any]:
    workspace = Path(workspace_root)
    candidate_root = workspace / "candidate"
    overlay_root = workspace / "overlay"
    applied = 0
    for item in overlay_plan:
        relpath = assert_safe_relative_path(item["relpath"])
        action = item.get("action", "upsert")
        target = candidate_root / relpath
        mirror = overlay_root / relpath
        if action == "delete":
            if target.exists():
                target.unlink()
            applied += 1
            continue
        content = item.get("content", "")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_text(content, encoding="utf-8")
        applied += 1
    payload = {"applied_items": applied, "overlay_items": len(overlay_plan)}
    (workspace / "metadata" / "overlay_stage.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

def finalize_shadow_run(workspace_root: str | Path) -> dict[str, Any]:
    workspace = Path(workspace_root)
    return write_diff_manifest(workspace, workspace / "baseline", workspace / "candidate")
