from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_shadow_apply.dry_apply import apply_overlay_to_candidate

def test_dry_apply_does_not_write_files(tmp_path):
    candidate_root = tmp_path / "candidate"
    payload = apply_overlay_to_candidate(
        candidate_root,
        [{"relpath": "example.txt", "content": "value"}],
        dry_run=True,
    )
    assert payload["manifest"]["applied"] == 1
    assert not (candidate_root / "example.txt").exists()
