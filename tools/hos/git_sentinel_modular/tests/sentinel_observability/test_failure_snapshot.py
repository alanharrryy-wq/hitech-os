from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_observability.failure_snapshot import capture_failure

def test_failure_snapshot_writes_json(tmp_path):
    try:
        raise ValueError("boom")
    except ValueError as exc:
        path = capture_failure(tmp_path, exc, context={"phase": "unit"})
    assert path.exists()
    assert "boom" in path.read_text(encoding="utf-8")
