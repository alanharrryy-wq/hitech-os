from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from capatch_diagnostics.session import DiagnosticBudget, DiagnosticSession, utc_now_iso
from capatch_plugins.active.fixer_safe_runtime_actions import run_fixers
from capatch_verify.registry import run_required_verifiers


class AutofixE2ETests(unittest.TestCase):
    def _session(self, root: Path, mode: str = 'apply-fixes') -> DiagnosticSession:
        return DiagnosticSession(
            session_id='diag_test',
            started_at=utc_now_iso(),
            root_dir=str(root),
            target_path=str(root),
            app_kind='python',
            execution_mode=mode,
            options={},
            budgets=DiagnosticBudget(),
        )

    def test_command_exit_zero_builtin_tracks_command_results(self) -> None:
        ok_rows = run_required_verifiers([], ['command-exit-zero'], {
            'command_results': [
                {'command': 'npm install --ignore-scripts', 'allowlisted': True, 'returncode': 0},
            ]
        })
        self.assertTrue(ok_rows[0]['ok'], ok_rows)

        bad_rows = run_required_verifiers([], ['command-exit-zero'], {
            'command_results': [
                {'command': 'npm install --ignore-scripts', 'allowlisted': True, 'returncode': 1},
            ]
        })
        self.assertFalse(bad_rows[0]['ok'], bad_rows)

    def test_apply_fixes_blocks_live_apply_when_sandbox_rolls_back(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_autofix_bad_') as tmp:
            root = Path(tmp)
            target = root / 'module.py'
            target.write_text('def meaning():\n    return 41\n', encoding='utf-8', newline='')
            session = self._session(root)
            proposal = {
                'proposal_id': 'autofix.bad-python',
                'title': 'Break python module',
                'rationale': 'Exercise sandbox gate',
                'family': 'general',
                'affected_paths': ['module.py'],
                'ops_payload': [
                    {
                        'type': 'EnsureReplaceExactOnce',
                        'label': 'break-module',
                        'file': 'module.py',
                        'old_text': '    return 41\n',
                        'new_text': '    return (\n',
                    }
                ],
                'verification_recipe': [
                    {'kind': 'builtin-verifier', 'verifier_id': 'python-parse', 'path': 'module.py', 'family': 'general'},
                ],
                'applicability_predicates': [
                    {'type': 'session_mode', 'modes': ['apply-fixes']},
                ],
                'metadata': {},
            }
            result = run_fixers(session, [proposal], [])
            bridge = session.options['autofix_bridge_results'][0]
            self.assertEqual('blocked-by-sandbox', bridge['execution_status'])
            self.assertEqual('failed', (bridge.get('sandbox') or {}).get('status'))
            self.assertFalse((bridge.get('sandbox') or {}).get('execution_ok', False))
            self.assertEqual('def meaning():\n    return 41\n', target.read_text(encoding='utf-8'))
            self.assertTrue(result['verification_results'])

    def test_apply_fixes_runs_sandbox_then_live_apply_for_safe_ops_payload(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_autofix_ok_') as tmp:
            root = Path(tmp)
            target = root / 'settings.json'
            target.write_text(json.dumps({'service': {'port': 3000}}, indent=2) + '\n', encoding='utf-8', newline='')
            session = self._session(root)
            proposal = {
                'proposal_id': 'autofix.port.bump',
                'title': 'Bump service port',
                'rationale': 'Exercise full Autofix Bridge',
                'family': 'port-conflict',
                'affected_paths': ['settings.json'],
                'ops_payload': [
                    {
                        'type': 'SetJsonValue',
                        'label': 'set-port',
                        'file': 'settings.json',
                        'json_pointer': '/service/port',
                        'value': 3001,
                    }
                ],
                'verification_recipe': [
                    {'kind': 'builtin-verifier', 'verifier_id': 'json-parse', 'path': 'settings.json', 'family': 'port-conflict'},
                ],
                'applicability_predicates': [
                    {'type': 'session_mode', 'modes': ['apply-fixes']},
                ],
                'metadata': {},
            }
            run_fixers(session, [proposal], [])
            bridge = session.options['autofix_bridge_results'][0]
            payload = json.loads(target.read_text(encoding='utf-8'))
            self.assertEqual(3001, payload['service']['port'])
            self.assertEqual('applied', bridge['execution_status'])
            self.assertTrue(bridge['execution_ok'])
            self.assertTrue((root / 'reports' / 'findings' / 'fix_execution.json').exists())
            self.assertTrue((root / 'reports' / 'verification' / 'before_after_verification.json').exists())


if __name__ == '__main__':
    unittest.main()
