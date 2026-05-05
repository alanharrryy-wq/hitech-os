from pathlib import Path

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine
from synapse_x.ingestion.coordinator import IngestionCoordinator
from synapse_x.ingestion.watcher import watch_loop


def test_ingest_pipeline_with_coordinator_and_watch_loop(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    source.mkdir()
    (source / "one.json").write_text(
        '{"session_id":"run-ingest-1","timestamp":"2026-04-05T10:00:00Z","summary":"first run"}',
        encoding="utf-8",
    )

    settings = Settings(root=tmp_path, source_paths=(source,))
    engine = SynapseEngine(settings)
    coordinator = IngestionCoordinator(engine)

    first = coordinator.ingest_now()
    assert first["files_processed"] == 1

    (source / "two.log").write_text("10:01 RuntimeError: watch catch", encoding="utf-8")
    watch_result = watch_loop(coordinator, interval_seconds=0, max_cycles=1)
    assert watch_result["status"] == "ok"
    assert watch_result["cycles"] == 1

    status = engine.get_status()
    assert status["counts"]["records"] >= 2
