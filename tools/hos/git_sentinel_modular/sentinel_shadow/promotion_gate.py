from __future__ import annotations

from typing import Any

DEFAULT_MAX_TOUCHED = 250

def evaluate_promotion_gate(
    diff_manifest: dict[str, Any],
    apply_result: dict[str, Any] | None = None,
    *,
    max_changed: int = DEFAULT_MAX_TOUCHED,
    allow_deletes: bool = False,
) -> dict[str, Any]:
    counts = diff_manifest.get("counts", {})
    reasons: list[str] = []
    if counts.get("total_touched", 0) > max_changed:
        reasons.append("too_many_changes")
    if not allow_deletes and counts.get("removed", 0) > 0:
        reasons.append("deletes_require_review")
    if apply_result:
        manifest = apply_result.get("manifest", apply_result)
        if manifest.get("rejected", 0) > 0:
            reasons.append("overlay_rejections_present")
    allowed = not reasons
    return {
        "allowed": allowed,
        "status": "ready_for_manual_review" if allowed else "blocked",
        "reasons": reasons,
    }

def assert_promotion_ready(gate: dict[str, Any]) -> None:
    if not gate.get("allowed"):
        raise RuntimeError(f"Promotion gate blocked: {gate.get('reasons', [])}")
