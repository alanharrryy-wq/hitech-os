from pathlib import Path

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine


def test_engine_ingest_search_metrics(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    source.mkdir()
    (source / "sample.json").write_text(
        '{"session_id":"rollout-2026-04-05","timestamp":"2026-04-05T10:36:00Z","summary":"pyside6 failure","tool":"pyside6","error":"fatal widget crash"}',
        encoding="utf-8",
    )

    settings = Settings(root=tmp_path, source_paths=(source,))
    engine = SynapseEngine(settings)
    result = engine.ingest()
    assert result["files_processed"] == 1

    rows = engine.search("pyside6")
    assert rows

    metrics = engine.get_metrics()
    assert metrics["totals"]["records"] >= 1

    detail = engine.get_session_detail("rollout-2026-04-05")
    assert detail["session"]["session_id"] == "rollout-2026-04-05"
