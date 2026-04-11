from pathlib import Path

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine


def test_session_detail_exposes_confidence_error_groups_and_timeline(tmp_path: Path) -> None:
    source = tmp_path / 'inputs'
    source.mkdir()

    (source / 'anchor.json').write_text(
        '{"session_id":"run-abc-42","timestamp":"2026-04-05T10:00:00Z","summary":"build failed in pytest with RuntimeError","tool":"python -m pytest","error":"RuntimeError: widget crash at C:/tmp/a.py:12"}',
        encoding='utf-8',
    )
    (source / 'worker_2026-04-05.log').write_text(
        '10:03 ERROR RuntimeError: widget crash at C:/tmp/b.py:98 while python -m pytest\n'
        'Traceback (most recent call last):\n'
        '  File "main.py", line 12, in <module>\n'
        'RuntimeError: widget crash\n',
        encoding='utf-8',
    )

    engine = SynapseEngine(Settings(root=tmp_path, source_paths=(source,)))
    result = engine.ingest()
    assert result['files_processed'] == 2

    detail = engine.get_session_detail('run-abc-42')
    assert detail['session']['confidence']['label'] in {'high', 'medium'}
    assert detail['session_insights']['error_groups']
    assert detail['session_insights']['error_groups'][0]['count'] >= 2
    assert any(item['kind'] == 'error' for item in detail['timeline'])
    assert any(item['phase'] in {'failure', 'test', 'build'} for item in detail['timeline'])


def test_metrics_expose_session_confidence_and_top_error_groups(tmp_path: Path) -> None:
    source = tmp_path / 'inputs'
    source.mkdir()

    (source / 'sample.json').write_text(
        '{"session_id":"rollout-2026-04-05","timestamp":"2026-04-05T10:36:00Z","summary":"pyside6 failure","tool":"pyside6","error":"fatal widget crash"}',
        encoding='utf-8',
    )

    engine = SynapseEngine(Settings(root=tmp_path, source_paths=(source,)))
    engine.ingest()
    metrics = engine.get_metrics()
    assert 'session_confidence' in metrics
    assert 'distribution' in metrics['session_confidence']
    assert 'top_error_groups' in metrics
