from pathlib import Path

from synapse_x.normalization import normalize_raw


def test_normalizer_extracts_summary_tools_and_errors(tmp_path: Path) -> None:
    source = tmp_path / "report_2026-04-08.md"
    payload = "2026-04-08 09:30 python -m pytest\nERROR RuntimeError: render crash"
    source.write_text(payload, encoding="utf-8")
    record = normalize_raw({"kind": "report", "payload": payload}, source)
    assert record.session_id.startswith("derived-") or record.session_id.startswith("report")
    assert record.summary
    assert any(error["error_type"] for error in record.errors)
    assert any(tool["tool_name"] == "pytest" for tool in record.tools)
