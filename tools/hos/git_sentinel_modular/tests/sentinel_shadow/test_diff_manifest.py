from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_shadow.diff_manifest import build_diff, snapshot_tree

def test_build_diff_detects_added_changed_removed(tmp_path):
    before = tmp_path / "before"
    after = tmp_path / "after"
    before.mkdir()
    after.mkdir()
    (before / "same.txt").write_text("same", encoding="utf-8")
    (before / "change.txt").write_text("before", encoding="utf-8")
    (before / "remove.txt").write_text("gone", encoding="utf-8")

    (after / "same.txt").write_text("same", encoding="utf-8")
    (after / "change.txt").write_text("after", encoding="utf-8")
    (after / "add.txt").write_text("new", encoding="utf-8")

    diff = build_diff(snapshot_tree(before), snapshot_tree(after))
    assert diff["counts"] == {"added": 1, "removed": 1, "changed": 1, "total_touched": 3}
