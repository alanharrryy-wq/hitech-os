from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_shadow.runner import finalize_shadow_run, prepare_shadow_run
from tools.hos.git_sentinel_modular.sentinel_shadow_apply.overlay_plan import build_overlay_plan
from tools.hos.git_sentinel_modular.sentinel_shadow.runner import stage_candidate_overlay

def test_runner_produces_diff_after_overlay(sandbox_runtime):
    source_root = sandbox_runtime / "source"
    source_root.mkdir()
    (source_root / "config.txt").write_text("old\n", encoding="utf-8")

    prepared = prepare_shadow_run("demo", source_root=source_root)
    workspace_root = prepared["workspace_root"]

    plan = build_overlay_plan({"config.txt": "new\n", "extra.txt": "hello\n"})
    stage_candidate_overlay(workspace_root, plan)
    diff_manifest = finalize_shadow_run(workspace_root)

    assert diff_manifest["counts"]["changed"] == 1
    assert diff_manifest["counts"]["added"] == 1
