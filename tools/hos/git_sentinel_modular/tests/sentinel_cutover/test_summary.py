from sentinel_cutover.summary import evaluate_cutover_readiness

def test_summary_blocked_when_smoke_fails():
    preflight_payload = {
        "ok": True,
        "run_manifest": {"run_id": "r1"},
        "diff_manifest": {"counts": {"total_touched": 1}},
        "promotion_review": {"decision": {"status": "ready_for_manual_review", "reviewers": ["repo-owner"]}},
    }
    smoke_payload = {"failures": ["python_parse_failed:x.py"], "warnings": []}
    matrix_payload = {"overall_risk": "high"}
    policy = {
        "promotion_status_blockers": ["blocked"],
        "promotion_status_attention": ["needs_review"],
        "cutover_mode": "manual_only",
    }

    result = evaluate_cutover_readiness(preflight_payload, smoke_payload, matrix_payload, policy)
    assert result["status"] == "blocked"
