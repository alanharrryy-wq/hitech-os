from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_observability.structured_logger import log_event

def test_log_event_appends_json_line(tmp_path):
    target = tmp_path / "events.jsonl"
    payload = log_event(target, "unit_test", value=3)
    assert payload["event"] == "unit_test"
    assert target.read_text(encoding="utf-8").count("\n") == 1
