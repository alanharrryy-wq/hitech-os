import json
from pathlib import Path

from sentinel_execute.plan import build_execution_plan
from sentinel_execute.policy_loader import default_policy

def _make_workspace(tmp_path):
    (tmp_path / "manifests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "review_bundle").mkdir(parents=True, exist_ok=True)
    (tmp_path / "cutover_bundle").mkdir(parents=True, exist_ok=True)
    (tmp_path / "candidate" / "legacy").mkdir(parents=True, exist_ok=True)
    (tmp_path / "baseline" / "legacy").mkdir(parents=True, exist_ok=True)

    (tmp_path / "candidate" / "legacy" / "adapters.py").write_text("x=1\n", encoding="utf-8")
    (tmp_path / "baseline" / "legacy" / "adapters.py").write_text("x=0\n", encoding="utf-8")

    (tmp_path / "manifests" / "run_manifest.json").write_text(json.dumps({"run_id": "r1"}), encoding="utf-8")
    (tmp_path / "manifests" / "apply_manifest.json").write_text(json.dumps({"run_id": "r1"}), encoding="utf-8")
    (tmp_path / "manifests" / "diff_manifest.json").write_text(json.dumps({
        "added": [],
        "removed": [],
        "changed": ["legacy/adapters.py"],
        "counts": {"total_touched": 1}
    }), encoding="utf-8")
    (tmp_path / "manifests" / "promotion_gate.json").write_text(json.dumps({"allowed": True}), encoding="utf-8")
    (tmp_path / "review_bundle" / "promotion_review.json").write_text(json.dumps({"decision": {"reviewers": ["repo-owner"]}}), encoding="utf-8")
    (tmp_path / "cutover_bundle" / "release_candidate_summary.json").write_text(json.dumps({"status": "ready"}), encoding="utf-8")

def test_plan_blocks_protected_prefix(tmp_path):
    _make_workspace(tmp_path)
    policy = default_policy()
    result = build_execution_plan(tmp_path, tmp_path / "target", policy)
    assert result["counts"]["blocked"] == 1
