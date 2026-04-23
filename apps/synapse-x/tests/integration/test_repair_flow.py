from pathlib import Path

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine
from synapse_x.ingestion.coordinator import IngestionCoordinator


def test_repair_flow_and_session_export(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    source.mkdir()
    (source / "sample.json").write_text(
        '{"session_id":"run-repair-1","timestamp":"2026-04-05T10:00:00Z","summary":"repair candidate","error":"RuntimeError: fail"}',
        encoding="utf-8",
    )

    settings = Settings(root=tmp_path, source_paths=(source,))
    engine = SynapseEngine(settings)
    coordinator = IngestionCoordinator(engine)
    coordinator.full_ingest()
    repaired = coordinator.repair()
    assert repaired["status"] in {"ok", "warning"}

    output = tmp_path / "exports" / "session_report.md"
    exported = engine.export_session_report("run-repair-1", output_path=output)
    assert exported["status"] == "ok"
    assert output.exists()
