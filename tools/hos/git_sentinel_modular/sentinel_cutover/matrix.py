from __future__ import annotations

from .policy_loader import default_policy
from ..sentinel_promotion.path_rules import classify_many

def _max_risk(values: list[str]) -> str:
    if "high" in values:
        return "high"
    if "medium" in values:
        return "medium"
    return "low"

def build_risk_matrix(diff_manifest: dict, policy: dict | None = None) -> dict:
    active_policy = policy or default_policy()
    paths = diff_manifest.get("added", []) + diff_manifest.get("changed", []) + diff_manifest.get("removed", [])
    grouped = classify_many(paths)
    overall_risk = _max_risk([bucket for bucket, values in grouped.items() if values] or ["low"])
    return {
        "grouped_paths": grouped,
        "overall_risk": overall_risk,
        "weights": active_policy["risk_weights"],
    }
