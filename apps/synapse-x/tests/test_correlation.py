
from pathlib import Path

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine


def test_ambiguous_files_adopt_explicit_anchor_session(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    source.mkdir()

    (source / "anchor.json").write_text(
        '{"session_id":"run-abc-42","timestamp":"2026-04-05T10:00:00Z","summary":"pyside6 widget crash","tool":"pytest","error":"RuntimeError: widget crash"}',
        encoding="utf-8",
    )
    (source / "worker_2026-04-05.log").write_text(
        "10:05 ERROR pyside6 widget crash while running python -m pytest\nRuntimeError: widget crash\n",
        encoding="utf-8",
    )
    (source / "report_2026-04-05.md").write_text(
        "2026-04-05 10:06 failure after pytest in pyside6\nRuntimeError widget crash\n",
        encoding="utf-8",
    )

    engine = SynapseEngine(Settings(root=tmp_path, source_paths=(source,)))
    result = engine.ingest()
    assert result["files_processed"] == 3

    detail = engine.get_session_detail("run-abc-42")
    assert detail["session"]["source_count"] == 3
    assert len(detail["records"]) == 3


def test_existing_anchor_can_adopt_new_ambiguous_file_on_later_ingest(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    source.mkdir()

    (source / "anchor.json").write_text(
        '{"session_id":"rollout-2026-04-05","timestamp":"2026-04-05T10:00:00Z","summary":"sqlite lock","tool":"sqlite3","error":"database lock"}',
        encoding="utf-8",
    )

    engine = SynapseEngine(Settings(root=tmp_path, source_paths=(source,)))
    first = engine.ingest()
    assert first["files_processed"] == 1

    (source / "later_2026-04-05.log").write_text(
        "10:20 ERROR database lock while running sqlite3 migration\n",
        encoding="utf-8",
    )

    second = engine.ingest()
    assert second["files_processed"] == 1

    detail = engine.get_session_detail("rollout-2026-04-05")
    assert detail["session"]["source_count"] == 2


def test_ambiguous_records_cluster_together_without_explicit_session(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    source.mkdir()

    (source / "alpha_2026-04-06.log").write_text(
        "08:00 ERROR database lock while running sqlite3 migration\n",
        encoding="utf-8",
    )
    (source / "beta_2026-04-06.report").write_text(
        "2026-04-06 08:15 failure database lock during sqlite migration\n",
        encoding="utf-8",
    )

    engine = SynapseEngine(Settings(root=tmp_path, source_paths=(source,)))
    result = engine.ingest()
    assert result["files_processed"] == 2

    rows = engine.search("database lock")
    session_ids = {row["session_id"] for row in rows}
    assert len(session_ids) == 1
    only_session = next(iter(session_ids))
    assert only_session.startswith("cluster-")
