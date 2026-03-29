from __future__ import annotations

from pathlib import Path

from tools.hos.git_sentinel_modular.sentinel_shadow.workspace import create_shadow_workspace

def test_create_shadow_workspace_copies_source_tree(sandbox_runtime):
    source_root = sandbox_runtime / "source"
    (source_root / "pkg").mkdir(parents=True)
    (source_root / "pkg" / "example.py").write_text("value = 1\n", encoding="utf-8")

    workspace = create_shadow_workspace("demo", source_root=source_root)

    assert workspace.workspace_root.exists()
    assert (workspace.baseline_root / "pkg" / "example.py").exists()
    assert (workspace.candidate_root / "pkg" / "example.py").exists()
