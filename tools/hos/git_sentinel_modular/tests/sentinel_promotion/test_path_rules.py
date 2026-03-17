from sentinel_promotion.path_rules import classify_path

def test_classify_path_marks_blocked_and_manual_review():
    policy = {
        "blocked_path_parts": ["_local"],
        "blocked_suffixes": [".tmp"],
        "manual_review_prefixes": ["legacy/"],
        "high_risk_prefixes": ["shared/provider.py"],
        "hard_block_removed_prefixes": ["legacy/"],
    }

    item = classify_path("legacy/example.tmp", policy)
    assert item["is_blocked"] is True
    assert item["needs_manual_review"] is True
    assert item["is_high_risk"] is False
