from pathlib import Path

def build_risk_matrix(preflight_payload, smoke_payload, policy):
    diff = preflight_payload["diff_manifest"]
    promotion_review = preflight_payload["promotion_review"]
    decision = promotion_review.get("decision", {})

    touched = diff.get("added", []) + diff.get("changed", []) + diff.get("removed", [])
    touched = sorted(set(touched))
    total_touched = diff.get("counts", {}).get("total_touched", 0)

    critical_prefixes = [str(x).replace("\\", "/") for x in policy.get("critical_prefixes", [])]

    critical_hits = []
    for relpath in touched:
        rel = str(relpath).replace("\\", "/")
        for prefix in critical_prefixes:
            if rel == prefix or rel.startswith(prefix):
                critical_hits.append(rel)
                break

    promotion_status = decision.get("status", "unknown")

    scope_risk = "low"
    if total_touched > policy.get("max_total_touched_before_attention", 15):
        scope_risk = "high"
    elif total_touched > policy.get("max_total_touched_for_easy_cutover", 5):
        scope_risk = "medium"

    smoke_risk = "low"
    if smoke_payload["failures"]:
        smoke_risk = "high"
    elif smoke_payload["warnings"]:
        smoke_risk = "medium"

    decision_risk = "low"
    if promotion_status in policy.get("promotion_status_blockers", []):
        decision_risk = "critical"
    elif promotion_status in policy.get("promotion_status_attention", []):
        decision_risk = "medium"

    critical_path_risk = "high" if critical_hits else "low"

    overall = _max_risk([scope_risk, smoke_risk, decision_risk, critical_path_risk])

    return {
        "overall_risk": overall,
        "dimensions": {
            "scope": scope_risk,
            "smoke": smoke_risk,
            "promotion_decision": decision_risk,
            "critical_paths": critical_path_risk,
        },
        "critical_hits": sorted(set(critical_hits)),
        "counts": {
            "total_touched": total_touched,
            "critical_hits": len(set(critical_hits)),
            "smoke_failures": len(smoke_payload["failures"]),
            "smoke_warnings": len(smoke_payload["warnings"]),
        },
    }

def _max_risk(levels):
    order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    reverse = {v: k for k, v in order.items()}
    return reverse[max(order[x] for x in levels)]
