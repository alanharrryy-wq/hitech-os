from sentinel_promotion.decision import evaluate_promotion_decision
from sentinel_promotion.policy_loader import default_policy

def test_decision_blocks_removed_legacy():
    policy = default_policy()

    diff_payload = {
        "added": [],
        "removed": ["legacy/adapters.py"],
        "changed": [],
        "counts": {"total_touched": 1},
    }
    gate_payload = {"allowed": True, "promotion_mode": "manual_only"}
    apply_payload = {"counts": {"rejected": 0}}

    result = evaluate_promotion_decision(diff_payload, gate_payload, apply_payload, policy)
    assert result["status"] == "blocked"
    assert any("removed_hard_block_path:legacy/adapters.py" == item for item in result["blocked_reasons"])

def test_decision_needs_review_on_threshold():
    policy = default_policy()

    diff_payload = {
        "added": ["a.py", "b.py", "c.py", "d.py", "e.py"],
        "removed": [],
        "changed": [],
        "counts": {"total_touched": 5},
    }
    gate_payload = {"allowed": True, "promotion_mode": "manual_only"}
    apply_payload = {"counts": {"rejected": 0}}

    result = evaluate_promotion_decision(diff_payload, gate_payload, apply_payload, policy)
    assert result["status"] == "needs_review"
