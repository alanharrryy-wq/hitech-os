from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_shadow_apply.overlay_plan import build_overlay_plan

def test_overlay_plan_normalizes_mapping_input():
    plan = build_overlay_plan({"a\\b.txt": "hello"})
    assert plan == [{"relpath": "a/b.txt", "content": "hello", "action": "upsert"}]
