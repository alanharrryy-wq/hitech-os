from pathlib import Path

from synapse_x.normalization import normalize_raw


def test_session_timestamp_and_tool_heuristics_from_text_log(tmp_path: Path) -> None:
    source = tmp_path / "rollout-2026-04-05_engine.log"
    text = """
10:36 Starting build with python -m pytest
10:37 ERROR pyside6 widget failed
Traceback (most recent call last):
  File \"main.py\", line 1, in <module>
RuntimeError: widget crash
""".strip()
    source.write_text(text, encoding="utf-8")

    raw = {"kind": "log", "payload": text}
    record = normalize_raw(raw, source)

    assert record.session_id == "rollout-2026-04-05"
    assert record.timestamp_utc == "2026-04-05T10:36:00Z"
    assert any(tool["tool_name"] == "pytest" for tool in record.tools)
    assert any(tool["tool_name"] == "pyside6" for tool in record.tools)
    assert any(error["error_type"] == "RuntimeError" for error in record.errors)
    assert record.metadata["heuristics"]["session_confidence"] in {"medium", "high"}


def test_structured_session_id_beats_generic_id(tmp_path: Path) -> None:
    source = tmp_path / "report.md"
    payload = {
        "id": "123",
        "session": {"session_id": "run-abc-42"},
        "timestamp": "2026-04-05 11:22",
        "command": "powershell ./repair.ps1",
        "error": "fatal PySide6 crash",
    }

    record = normalize_raw({"kind": "json", "payload": payload}, source)

    assert record.session_id == "run-abc-42"
    assert record.timestamp_utc == "2026-04-05T11:22:00Z"
    assert any(tool["tool_name"] == "powershell" for tool in record.tools)
    assert any(error["severity"] == "fatal" for error in record.errors)
