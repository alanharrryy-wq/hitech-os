from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_shadow_apply.review_pack import build_review_pack

def test_review_pack_writes_summary(tmp_path):
    result = build_review_pack(
        tmp_path,
        {"counts": {"added": 1, "removed": 0, "changed": 0}},
        {"manifest": {"applied": 1, "rejected": 0}},
        {"status": "ready_for_manual_review"},
    )
    assert (tmp_path / "review_bundle" / "review_summary.json").exists()
    assert result["status"] == "ready_for_manual_review"
