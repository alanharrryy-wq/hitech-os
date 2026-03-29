from __future__ import annotations

from tools.hos.git_sentinel_modular.operations.status import build_combined_status

def test_build_combined_status_returns_summary(sandbox_runtime):
    summary = build_combined_status().to_dict()
    assert summary["overall_status"] in {"ready", "attention"}
    assert "runtime" in summary
    assert "supervisor" in summary
