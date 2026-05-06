from pathlib import Path

from synapse_x.ingestion.scanner import scan_sources


def test_scan_sources_only_returns_supported_extensions(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    source.mkdir()
    (source / "a.json").write_text('{"ok": true}', encoding="utf-8")
    (source / "b.log").write_text("hello", encoding="utf-8")
    (source / "c.png").write_text("binary-ish", encoding="utf-8")

    rows = scan_sources([source])
    names = {item.name for item in rows}
    assert "a.json" in names
    assert "b.log" in names
    assert "c.png" not in names
