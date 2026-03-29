from __future__ import annotations

from tools.hos.git_sentinel_modular.app.modular_cli import run_rollout_pipeline_plan_only

def test_rollout_pipeline_plan_only_returns_expected_shape(sandbox_runtime):
    source_root = sandbox_runtime / "source"
    target_root = sandbox_runtime / "target"
    source_root.mkdir()
    target_root.mkdir()
    (source_root / "settings.ini").write_text("before=true\n", encoding="utf-8")

    result = run_rollout_pipeline_plan_only(
        run_id="demo_flow",
        source_root=source_root,
        target_root=target_root,
        overlay_mutations={
            "settings.ini": "before=false\n",
            "new_file.txt": "hello\n",
        },
    )

    assert result["gate_allowed"] is True
    assert result["promotion_status"] in {"ready_for_manual_review", "needs_review"}
    assert result["cutover_status"] in {"ready", "needs_attention"}
    assert result["execute_dry_run_summary"]["status"] == "planned_only"
    assert result["execution_counts"]["actions"] == 2
