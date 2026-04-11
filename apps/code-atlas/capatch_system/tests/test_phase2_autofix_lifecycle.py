from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from capatch_engine.fixer_bridge import staged_apply


class Phase2AutofixLifecycleTests(unittest.TestCase):
    def test_staged_apply_reports_lifecycle_fields(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_phase2_autofix_') as tmp:
            root = Path(tmp)
            target = root / 'module.py'
            target.write_text('def meaning():\n    return 41\n', encoding='utf-8', newline='')
            proposal = {
                'proposal_id': 'autofix.phase2.ok',
                'title': 'Lift meaning',
                'rationale': 'Exercise lifecycle payload',
                'family': 'general',
                'affected_paths': ['module.py'],
                'ops_payload': [
                    {
                        'type': 'EnsureReplaceExactOnce',
                        'label': 'meaning-42',
                        'file': 'module.py',
                        'old_text': '    return 41\n',
                        'new_text': '    return 42\n',
                    }
                ],
                'verification_recipe': [
                    {'kind': 'builtin-verifier', 'verifier_id': 'python-parse', 'path': 'module.py', 'family': 'general'},
                    {'kind': 'builtin-verifier', 'verifier_id': 'python-compile-smoke', 'path': 'module.py', 'family': 'general'},
                    {'kind': 'builtin-verifier', 'verifier_id': 'python-import-smoke', 'path': 'module.py', 'family': 'general'},
                ],
                'metadata': {},
            }
            result = staged_apply(root, proposal, dry_run=False)
            self.assertIn('preconditions_satisfied', result)
            self.assertIn('verification_steps', result)
            self.assertIn('verification_outcome', result)
            self.assertIn('rollback_triggered', result)
            self.assertIn('rollback_outcome', result)
            self.assertIn('final_state', result)
            self.assertTrue(result['verification_steps'])


if __name__ == '__main__':
    unittest.main()
