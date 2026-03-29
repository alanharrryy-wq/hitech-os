from sentinel_cutover.rollback import build_rollback_manifest

def test_rollback_manifest_has_expected_action_counts():
    preflight_payload = {
        "diff_manifest": {
            "added": ["a.py"],
            "removed": ["b.py"],
            "changed": ["c.py"],
            "counts": {"total_touched": 3},
        }
    }

    result = build_rollback_manifest(preflight_payload)
    assert result["counts"]["actions"] == 3
