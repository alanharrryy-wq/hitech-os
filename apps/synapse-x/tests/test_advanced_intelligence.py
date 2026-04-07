from pathlib import Path

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine
from synapse_x.storage import connect


def test_related_sessions_sequences_and_root_causes(tmp_path: Path) -> None:
    source = tmp_path / 'inputs'
    source.mkdir()

    (source / 'session_a.json').write_text(
        '{"session_id":"run-alpha-1","timestamp":"2026-04-05T10:00:00Z","summary":"build step started with pytest and pyside6 widget smoke test","tool":"python -m pytest","events":[{"timestamp":"2026-04-05T10:00:00Z","message":"build completed"},{"timestamp":"2026-04-05T10:01:00Z","message":"pytest widget suite started"}],"error":"RuntimeError: widget render crash in PySide6 window"}',
        encoding='utf-8',
    )
    (source / 'session_a_repair.log').write_text(
        '10:02 ERROR RuntimeError: widget render crash in PySide6 window\n'
        '10:03 repair cache and rebuild index\n',
        encoding='utf-8',
    )
    (source / 'session_b.json').write_text(
        '{"session_id":"run-beta-2","timestamp":"2026-04-06T09:00:00Z","summary":"pytest pyside6 widget suite failed again","tool":"pytest","error":"RuntimeError: widget render crash in PySide6 dialog"}',
        encoding='utf-8',
    )

    engine = SynapseEngine(Settings(root=tmp_path, source_paths=(source,)))
    result = engine.ingest(full=True)
    assert result['files_processed'] == 3

    detail = engine.get_session_detail('run-alpha-1')
    assert detail['related_sessions']
    assert detail['related_sessions'][0]['session_id'] == 'run-beta-2'
    assert detail['session_insights']['sequence_patterns']
    assert any('failure' in item['pattern'] for item in detail['session_insights']['sequence_patterns'])
    assert detail['session_insights']['probable_root_causes']
    assert detail['session_insights']['probable_root_causes'][0]['category'] in {'ui_or_rendering', 'runtime_crash', 'test_assertion'}

    metrics = engine.get_metrics()
    assert 'sequence_patterns' in metrics
    assert metrics['sequence_patterns']


def test_source_count_stays_stable_on_full_reingest(tmp_path: Path) -> None:
    source = tmp_path / 'inputs'
    source.mkdir()
    sample = source / 'single.json'
    sample.write_text(
        '{"session_id":"run-gamma-1","timestamp":"2026-04-05T12:00:00Z","summary":"first pass ok"}',
        encoding='utf-8',
    )

    engine = SynapseEngine(Settings(root=tmp_path, source_paths=(source,)))
    engine.ingest(full=True)
    engine.ingest(full=True)

    conn = connect(tmp_path / 'data' / 'sqlite' / 'synapse_x.db')
    try:
        row = conn.execute("SELECT source_count FROM sessions WHERE session_id = ?", ('run-gamma-1',)).fetchone()
        assert row is not None
        assert row['source_count'] == 1
    finally:
        conn.close()
