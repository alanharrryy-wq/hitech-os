from pathlib import Path
from sentinel_promotion.bundle import build_promotion_bundle

def test_bundle_writes_outputs(tmp_path):
    manifests = tmp_path / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)

    (manifests / "run_manifest.json").write_text('{"run_id":"r1"}', encoding="utf-8")
    (manifests / "apply_manifest.json").write_text('{"counts":{"applied":1,"skipped":0,"rejected":0}}', encoding="utf-8")
    (manifests / "diff_manifest.json").write_text('{"added":["tools/x.py"],"removed":[],"changed":[],"counts":{"added":1,"removed":0,"changed":0,"total_touched":1}}', encoding="utf-8")
    (manifests / "promotion_gate.json").write_text('{"allowed":true,"promotion_mode":"manual_only","notes":["manual review only"]}', encoding="utf-8")

    result = build_promotion_bundle(tmp_path)

    assert result["promotion_review_json"].exists()
    assert result["promotion_review_md"].exists()
    assert result["reviewer_assignment_json"].exists()
    assert result["reviewer_assignment_md"].exists()
    assert result["evidence_index_json"].exists()
