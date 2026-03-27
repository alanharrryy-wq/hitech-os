from __future__ import annotations

def evaluate_cutover_readiness(preflight: dict, risk_matrix: dict, smoke: dict | None = None) -> dict:
    smoke = smoke or {"status": "skipped"}
    status = "ready"
    if preflight.get("status") != "ready":
        status = "needs_attention"
    elif risk_matrix.get("overall_risk") == "high":
        status = "needs_attention"
    return {
        "status": status,
        "overall_risk": risk_matrix.get("overall_risk", "low"),
        "smoke_status": smoke.get("status", "skipped"),
    }
