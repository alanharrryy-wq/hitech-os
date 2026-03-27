from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_observability.drift_detector import detect_drift, hash_directory

def test_detect_drift_finds_changed_file(tmp_path):
    expected_root = tmp_path / "expected"
    current_root = tmp_path / "current"
    expected_root.mkdir()
    current_root.mkdir()
    (expected_root / "a.txt").write_text("old", encoding="utf-8")
    (current_root / "a.txt").write_text("new", encoding="utf-8")
    expected = hash_directory(expected_root)
    result = detect_drift(expected, current_root)
    assert result["drift_detected"] is True
    assert result["changed"] == ["a.txt"]
