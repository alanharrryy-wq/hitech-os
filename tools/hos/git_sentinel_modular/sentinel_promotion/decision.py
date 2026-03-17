from .path_rules import classify_many
from .reviewers import reviewers_for_paths

def evaluate_promotion_decision(diff_payload, gate_payload, apply_payload, policy):
    touched_paths = []
    touched_paths.extend(diff_payload.get("added", []))
    touched_paths.extend(diff_payload.get("removed", []))
    touched_paths.extend(diff_payload.get("changed", []))

    path_report = classify_many(touched_paths, policy)
    blocked = []
    warnings = []

    if not gate_payload.get("allowed", False):
        blocked.append("upstream_promotion_gate_blocked")

    removed_paths = set(diff_payload.get("removed", []))
    for item in path_report:
        if item["is_blocked"]:
            blocked.extend(item["blocked_reasons"])

        if item["path"] in removed_paths and item["hard_block_remove_hits"]:
            blocked.append(f"removed_hard_block_path:{item['path']}")

        if item["is_high_risk"]:
            warnings.append(f"high_risk_path:{item['path']}")

        if item["needs_manual_review"]:
            warnings.append(f"manual_review_path:{item['path']}")

    counts = diff_payload.get("counts", {})
    total_touched = counts.get("total_touched", 0)

    thresholds = policy.get("review_thresholds", {})
    needs_review_total_touched = thresholds.get("needs_review_total_touched", 5)
    high_risk_total_touched = thresholds.get("high_risk_total_touched", 15)

    if total_touched >= needs_review_total_touched:
        warnings.append(f"touched_threshold:{total_touched}")

    if total_touched >= high_risk_total_touched:
        warnings.append(f"high_risk_threshold:{total_touched}")

    if apply_payload.get("counts", {}).get("rejected", 0) > 0:
        warnings.append("rejected_apply_actions_present")

    if blocked:
        status = "blocked"
    elif warnings:
        status = "needs_review"
    else:
        status = "ready_for_manual_review"

    reviewers = reviewers_for_paths(touched_paths, policy)

    return {
        "status": status,
        "promotion_mode": policy.get("promotion_mode", "manual_only"),
        "blocked_reasons": sorted(set(blocked)),
        "warnings": sorted(set(warnings)),
        "reviewers": reviewers,
        "path_report": path_report,
        "touched_paths": sorted(set(touched_paths)),
        "counts": {
            "total_touched": total_touched,
            "reviewers": len(reviewers),
            "blocked_reasons": len(set(blocked)),
            "warnings": len(set(warnings)),
        },
    }
