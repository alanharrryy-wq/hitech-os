from __future__ import annotations

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from capatch_cli.commands_patch import _export_attempt_artifacts, handle


def _args(root_dir: Path, **overrides: object) -> SimpleNamespace:
    payload: dict[str, object] = {
        'self_test': False,
        'smoke_test': False,
        'ops_file': 'ops.json',
        'ops_stdin': False,
        'root_dir': str(root_dir),
        'dry_run': False,
        'no_auto_support': False,
        'checkpoint_label': 'session',
        'json_output': True,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _pipeline(root: Path) -> SimpleNamespace:
    return SimpleNamespace(
        preflight_report=SimpleNamespace(
            path_violations=[],
            conflicts=[],
            schema_violations=[],
            target_files=['pkg/alpha.txt', 'pkg/missing.txt'],
        ),
        preview_payload={
            'diff_summary': ['pkg/alpha.txt (+1 -1)'],
            'preview_content_by_target': {(root / 'pkg' / 'alpha.txt'): 'preview'},
        },
        operation_results=[
            SimpleNamespace(
                operation_label='op-alpha',
                patch_status='applied',
                target_path=str(root / 'pkg' / 'alpha.txt'),
                message='ok',
            ),
            {
                'operation_label': 'op-bin',
                'patch_status': 'applied',
                'target_path': str(root / 'pkg' / 'binary.bin'),
                'message': 'ok',
            },
        ],
        required_verifiers=['python-parse'],
        verifier_results=[{'verifier_id': 'python-parse', 'ok': True, 'title': 'parse', 'detail': ''}],
        rollback_decision={'should_rollback': False},
        rollback_event=None,
        run_record=SimpleNamespace(
            run_id='patch_123',
            patch_status='applied',
            system_status='verified',
            verification_outcome='passed',
            target_files=['pkg/alpha.txt'],
        ),
        outcome='verified',
        error=None,
    )


def test_export_attempt_artifacts_writes_log_and_sources_with_missing_and_binary_notes() -> None:
    with tempfile.TemporaryDirectory(prefix='capatch_export_attempt_') as tmp_dir:
        root = Path(tmp_dir)
        (root / 'pkg').mkdir(parents=True, exist_ok=True)
        (root / 'pkg' / 'alpha.txt').write_text('alpha\nbeta\n', encoding='utf-8', newline='')
        (root / 'pkg' / 'binary.bin').write_bytes(b'\x00\x01\x02binary\x03')

        args = _args(root)
        operations = [
            SimpleNamespace(file='pkg/alpha.txt', payload={}),
            SimpleNamespace(file='pkg/beta.txt', payload={}),
        ]
        export_dir = root / 'external_exports'
        with patch.dict(os.environ, {'CAPATCH_AUDIT_EXPORT_DIR': str(export_dir)}):
            refs = _export_attempt_artifacts(args, _pipeline(root), operations, reason_override='forced-test')

        assert refs.get('export_error') in {None, ''}
        log_path = Path(str(refs['log_path']))
        sources_path = Path(str(refs['sources_path']))
        assert log_path.exists()
        assert sources_path.exists()

        log_text = log_path.read_text(encoding='utf-8')
        assert 'outcome=verified' in log_text
        assert 'run_id=patch_123' in log_text
        assert 'rollback_decision=' in log_text
        assert 'pkg/missing.txt' in log_text

        sources_text = sources_path.read_text(encoding='utf-8')
        assert '===== FILE: pkg/alpha.txt =====' in sources_text
        assert 'alpha\nbeta\n' in sources_text
        assert '===== FILE: pkg/missing.txt =====' in sources_text
        assert 'file does not exist at export time' in sources_text
        assert '===== FILE: pkg/binary.bin =====' in sources_text
        assert 'binary-looking content detected' in sources_text


def test_json_output_includes_external_audit_refs() -> None:
    with tempfile.TemporaryDirectory(prefix='capatch_export_json_') as tmp_dir:
        root = Path(tmp_dir)
        args = _args(root)
        export_dir = root / 'exports'
        with patch.dict(os.environ, {'CAPATCH_AUDIT_EXPORT_DIR': str(export_dir)}):
            with patch('capatch_cli.commands_patch.load_operations_from_file', return_value=[]):
                with patch('capatch_cli.commands_patch.run_patch_pipeline', return_value=_pipeline(root)):
                    output_lines: list[str] = []
                    with patch('capatch_cli.commands_patch.print', side_effect=lambda *a, **k: output_lines.append(' '.join(str(x) for x in a))):
                        code = handle(args, parser=None)
        assert code == 0
        json_rows = [line for line in output_lines if line.strip().startswith('{') and line.strip().endswith('}')]
        assert json_rows
        payload = json_rows[-1]
        assert '"external_audit_refs"' in payload
