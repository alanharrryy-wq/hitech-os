from __future__ import annotations

from pathlib import Path
from typing import Any

from ..sentinel_shadow.promotion_gate import evaluate_promotion_gate
from ..sentinel_shadow.runner import finalize_shadow_run, stage_candidate_overlay
from .dry_apply import apply_overlay_to_candidate
from .policies import ApplyPolicy, default_policy
from .review_pack import build_review_pack

def run_shadow_apply_engine(
    workspace_root: str | Path,
    overlay_plan: list[dict[str, Any]] | None = None,
    policy: ApplyPolicy | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    workspace = Path(workspace_root)
    active_policy = policy or default_policy()
    staged = stage_candidate_overlay(workspace, overlay_plan or [])
    apply_result = apply_overlay_to_candidate(workspace / "candidate", overlay_plan or [], active_policy, dry_run=dry_run)
    diff_manifest = finalize_shadow_run(workspace)
    gate = evaluate_promotion_gate(diff_manifest, apply_result, allow_deletes=active_policy.allow_delete)
    review_pack = build_review_pack(workspace, diff_manifest, apply_result, gate)
    return {
        "staged": staged,
        "apply_result": apply_result,
        "diff_manifest": diff_manifest,
        "gate": gate,
        "review_pack": review_pack,
    }
