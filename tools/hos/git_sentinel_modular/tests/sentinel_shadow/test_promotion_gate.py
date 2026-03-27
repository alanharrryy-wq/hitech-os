from __future__ import annotations

import pytest

from tools.hos.git_sentinel_modular.sentinel_shadow.promotion_gate import assert_promotion_ready, evaluate_promotion_gate

def test_promotion_gate_blocks_deletes_without_permission():
    diff_manifest = {"counts": {"total_touched": 1, "removed": 1}}
    gate = evaluate_promotion_gate(diff_manifest)
    assert gate["allowed"] is False
    with pytest.raises(RuntimeError):
        assert_promotion_ready(gate)
