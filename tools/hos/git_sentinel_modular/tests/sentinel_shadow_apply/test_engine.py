from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_shadow.runner import prepare_shadow_run
from tools.hos.git_sentinel_modular.sentinel_shadow_apply.engine import run_shadow_apply_engine

def test_engine_runs_end_to_end(sandbox_runtime):
    source_root = sandbox_runtime / "source"
    source_root.mkdir()
    (source_root / "base.txt").write_text("old\n", encoding="utf-8")

    prepared = prepare_shadow_run("demo", source_root=source_root)
    result = run_shadow_apply_engine(
        prepared["workspace_root"],
        [{"relpath": "base.txt", "content": "new\n"}],
    )

    assert result["apply_result"]["manifest"]["applied"] == 1
    assert result["diff_manifest"]["counts"]["changed"] == 1
    assert result["review_pack"]["status"] == "ready_for_manual_review"
