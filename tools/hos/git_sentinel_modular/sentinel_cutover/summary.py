def evaluate_cutover_readiness(preflight_payload, smoke_payload, matrix_payload, policy):
    promotion_decision = preflight_payload["promotion_review"].get("decision", {})
    promotion_status = promotion_decision.get("status", "unknown")

    blockers = []
    attention_items = []

    if not preflight_payload["ok"]:
        blockers.extend(preflight_payload["issues"])

    blockers.extend(smoke_payload.get("failures", []))

    if promotion_status in policy.get("promotion_status_blockers", []):
        blockers.append(f"promotion_status:{promotion_status}")

    attention_items.extend(smoke_payload.get("warnings", []))

    if promotion_status in policy.get("promotion_status_attention", []):
        attention_items.append(f"promotion_status:{promotion_status}")

    if matrix_payload["overall_risk"] in ("high", "critical"):
        attention_items.append(f"overall_risk:{matrix_payload['overall_risk']}")

    if blockers:
        status = "blocked"
    elif attention_items:
        status = "needs_attention"
    else:
        status = "ready"

    reviewers = promotion_decision.get("reviewers", [])

    return {
        "run_id": preflight_payload["run_manifest"].get("run_id"),
        "status": status,
        "cutover_mode": policy.get("cutover_mode", "manual_only"),
        "overall_risk": matrix_payload["overall_risk"],
        "reviewers": reviewers,
        "blockers": sorted(set(blockers)),
        "attention_items": sorted(set(attention_items)),
        "counts": {
            "blockers": len(set(blockers)),
            "attention_items": len(set(attention_items)),
            "reviewers": len(reviewers),
            "touched_paths": preflight_payload["diff_manifest"].get("counts", {}).get("total_touched", 0),
        },
    }
