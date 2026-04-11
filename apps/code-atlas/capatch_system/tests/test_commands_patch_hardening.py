from __future__ import annotations

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from capatch_cli.commands_patch import handle
from capatch_cli.exit_codes import EXIT_BLOCKED, EXIT_OK, EXIT_VERIFICATION_ROLLED_BACK


def _args(**overrides: object) -> SimpleNamespace:
    payload: dict[str, object] = {
        'self_test': False,
        'smoke_test': False,
        'ops_file': 'ops.json',
        'ops_stdin': False,
        'root_dir': '.',
        'dry_run': False,
        'no_auto_support': False,
        'checkpoint_label': 'session',
        'json_output': False,
        'strategy': 'auto',
        'probe_only': False,
        'allow_advisory_strategy': False,
        'force_dry_run_on_high_risk': True,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _rolled_back_pipeline() -> SimpleNamespace:
    return SimpleNamespace(
        preflight_report=SimpleNamespace(path_violations=[], conflicts=[], schema_violations=[]),
        preview_payload={'diff_summary': []},
        operation_results=[],
        required_verifiers=[],
        verifier_results=[],
        rollback_decision={'should_rollback': True, 'rollback_reason': 'forced-test'},
        rollback_event={'status': 'restored', 'checkpoint_id': 'session_test'},
        run_record=SimpleNamespace(
            run_id='patch_0001',
            patch_status='rolled_back',
            system_status='rolled_back',
            verification_outcome='failed',
        ),
        outcome='rolled-back',
        strategy_decision={'selected_strategy': 'guarded', 'advisory_only': False, 'selected_score': 0.61, 'reasons': ['forced-test']},
        error=None,
    )


def _verified_pipeline() -> SimpleNamespace:
    return SimpleNamespace(
        preflight_report=SimpleNamespace(path_violations=[], conflicts=[], schema_violations=[]),
        preview_payload={'diff_summary': ['pkg/service.py']},
        operation_results=[],
        required_verifiers=['python-parse'],
        verifier_results=[{'verifier_id': 'python-parse', 'ok': True, 'title': 'ok', 'detail': 'ok'}],
        rollback_decision={'should_rollback': False},
        rollback_event=None,
        run_record=SimpleNamespace(
            run_id='patch_0002',
            patch_status='applied',
            system_status='verified',
            verification_outcome='passed',
            rollback_target='checkpoint_001',
        ),
        outcome='verified',
        strategy_decision={'selected_strategy': 'exact', 'advisory_only': False, 'selected_score': 0.68, 'reasons': ['forced-test']},
        error=None,
    )


def _probe_only_pipeline() -> SimpleNamespace:
    return SimpleNamespace(
        preflight_report=SimpleNamespace(path_violations=[], conflicts=[], schema_violations=[]),
        preview_payload={'diff_summary': []},
        operation_results=[],
        required_verifiers=['python-parse'],
        verifier_results=[],
        rollback_decision={'should_rollback': False},
        rollback_event=None,
        run_record=None,
        outcome='blocked',
        strategy_decision={'selected_strategy': 'probe-only', 'advisory_only': False, 'selected_score': 0.22, 'reasons': ['forced-test']},
        error='probe-only strategy selected; rerun with --dry-run or --strategy exact/guarded',
    )


def test_rollback_warning_emission_cannot_mask_pipeline_outcome() -> None:
    args = _args()
    with tempfile.TemporaryDirectory(prefix='capatch_external_export_') as tmp_dir:
        export_dir = Path(tmp_dir) / 'exports'
        with patch.dict(os.environ, {'CAPATCH_AUDIT_EXPORT_DIR': str(export_dir)}):
            with patch('capatch_cli.commands_patch.load_operations_from_file', return_value=[]):
                with patch('capatch_cli.commands_patch.run_patch_pipeline', return_value=_rolled_back_pipeline()):
                    with patch('capatch_cli.patch_compat.print', side_effect=OSError('broken pipe')):
                        assert handle(args, parser=None) == EXIT_VERIFICATION_ROLLED_BACK


def test_json_summary_exposes_selected_strategy() -> None:
    args = _args(json_output=True)
    with patch('capatch_cli.commands_patch.load_operations_from_file', return_value=[]):
        with patch('capatch_cli.commands_patch.run_patch_pipeline', return_value=_verified_pipeline()):
            with patch('capatch_cli.commands_patch._export_attempt_artifacts', return_value={'log_path': 'F:/descargasf/log.txt', 'sources_path': 'F:/descargasf/sources.txt'}):
                with patch('capatch_cli.commands_patch._emit_json_summary') as emit_json:
                    assert handle(args, parser=None) == EXIT_OK
    payload = emit_json.call_args.args[0]
    assert payload['selected_strategy'] == 'exact'
    assert payload['status'] == 'ok'
    assert payload['external_audit_refs']['log_path'].endswith('log.txt')


def test_probe_only_block_emits_warning_and_exit_blocked() -> None:
    args = _args()
    with patch('capatch_cli.commands_patch.load_operations_from_file', return_value=[]):
        with patch('capatch_cli.commands_patch.run_patch_pipeline', return_value=_probe_only_pipeline()):
            with patch('capatch_cli.commands_patch._export_attempt_artifacts', return_value={'log_path': 'F:/descargasf/log.txt', 'sources_path': 'F:/descargasf/sources.txt'}):
                with patch('capatch_cli.commands_patch.emit_warn') as emit_warn:
                    assert handle(args, parser=None) == EXIT_BLOCKED
    emit_warn.assert_called()
