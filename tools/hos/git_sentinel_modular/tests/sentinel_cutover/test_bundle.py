import json
from pathlib import Path
from sentinel_cutover.bundle import build_cutover_readiness_bundle

def test_bundle_writes_outputs(tmp_path):
    (tmp_path / "manifests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "review_bundle").mkdir(parents=True, exist_ok=True)
    (tmp_path / "candidate").mkdir(parents=True, exist_ok=True)
    (tmp_path / "baseline").mkdir(parents=True, exist_ok=True)

    (tmp_path / "candidate" / "tools").mkdir(parents=True, exist_ok=True)
    (tmp_path / "candidate" / "tools" / "x.py").write_text("x = 1\n", encoding="utf-8")

    (tmp_path / "manifests" / "run_manifest.json").write_text(json.dumps({"run_id": "r1"}), encoding="utf-8")
    (tmp_path / "manifests" / "apply_manifest.json").write_text(json.dumps({"run_id": "r1", "counts": {"applied": 1}}), encoding="utf-8")
    (tmp_path / "manifests" / "diff_manifest.json").write_text(json.dumps({
        "added": ["tools/x.py"],
        "removed": [],
        "changed": [],
        "counts": {"added": 1, "removed": 0, "changed": 0, "total_touched": 1}
    }), encoding="utf-8")
    (tmp_path / "manifests" / "promotion_gate.json").write_text(json.dumps({"allowed": True, "promotion_mode": "manual_only"}), encoding="utf-8")
    (tmp_path / "review_bundle" / "promotion_review.json").write_text(json.dumps({
        "decision": {"status": "ready_for_manual_review", "reviewers": ["repo-owner"]},
        "source_counts": {"diff": {"total_touched": 1}}
    }), encoding="utf-8")

    result = build_cutover_readiness_bundle(tmp_path)

    assert result["summary_path"].exists()
    assert result["summary_md_path"].exists()
    assert result["checklist_path"].exists()
