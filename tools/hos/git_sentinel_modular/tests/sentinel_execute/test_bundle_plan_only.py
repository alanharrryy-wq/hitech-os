import json
from pathlib import Path

from sentinel_execute.bundle import build_execution_bundle

def _make_workspace(tmp_path):
    (tmp_path / "manifests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "review_bundle").mkdir(parents=True, exist_ok=True)
    (tmp_path / "cutover_bundle").mkdir(parents=True, exist_ok=True)
    (tmp_path / "candidate" / "tools").mkdir(parents=True, exist_ok=True)
    (tmp_path / "baseline" / "tools").mkdir(parents=True, exist_ok=True)
    (tmp_path / "candidate" / "tools" / "x.py").write_text("x=1\n", encoding="utf-8")

    (tmp_path / "manifests" / "run_manifest.json").write_text(json.dumps({"run_id": "r1"}), encoding="utf-8")
    (tmp_path / "manifests" / "apply_manifest.json").write_text(json.dumps({"run_id": "r1"}), encoding="utf-8")
    (tmp_path / "manifests" / "diff_manifest.json").write_text(json.dumps({
        "added": ["tools/x.py"],
        "removed": [],
        "changed": [],
        "counts": {"total_touched": 1}
    }), encoding="utf-8")
    (tmp_path / "manifests" / "promotion_gate.json").write_text(json.dumps({"allowed": True}), encoding="utf-8")
    (tmp_path / "review_bundle" / "promotion_review.json").write_text(json.dumps({"decision": {"reviewers": ["repo-owner"]}}), encoding="utf-8")
    (tmp_path / "cutover_bundle" / "release_candidate_summary.json").write_text(json.dumps({"status": "ready"}), encoding="utf-8")

def test_build_execution_bundle_writes_plan(tmp_path):
    _make_workspace(tmp_path)
    target_root = tmp_path / "target"
    target_root.mkdir(parents=True, exist_ok=True)

    result = build_execution_bundle(tmp_path, target_root)
    assert result["execution_dir"].exists()
    assert (result["execution_dir"] / "execution_plan.json").exists()
