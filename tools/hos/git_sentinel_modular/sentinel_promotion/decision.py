from __future__ import annotations

from typing import Any

from .policy_loader import default_policy
from .reviewers import reviewers_for_paths

def evaluate_promotion_decision(
    diff_manifest: dict[str, Any],
    apply_result: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_policy = policy or default_policy()
    counts = diff_manifest.get("counts", {})
    changed_paths = (
        diff_manifest.get("added", []) +
        diff_manifest.get("changed", []) +
        diff_manifest.get("removed", [])
    )
    reviewers = reviewers_for_paths(changed_paths)
    status = "ready_for_manual_review"
    if counts.get("total_touched", 0) > active_policy["max_total_touched"]:
        status = "needs_attention"
    if counts.get("removed", 0) and not active_policy["allow_deletes"]:
        status = "needs_review"
    if apply_result and apply_result.get("manifest", {}).get("rejected", 0) > 0:
        status = "needs_attention"
    return {
        "status": status,
        "reviewers": reviewers,
        "review_dir_name": "review_bundle",
    }
