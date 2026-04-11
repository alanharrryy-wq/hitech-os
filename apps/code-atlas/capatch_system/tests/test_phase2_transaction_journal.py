from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.qa_testkit import build_ops, make_ctx, write_text
from capatch_engine.patch_pipeline import run_patch_pipeline


class Phase2TransactionJournalTests(unittest.TestCase):
    def test_transaction_journal_commits_clean_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_phase2_tx_') as tmp_dir:
            root = Path(tmp_dir)
            pkg = root / 'pkg'
            pkg.mkdir(parents=True, exist_ok=True)
            target = pkg / 'service.py'
            write_text(target, 'def compute() -> int:\n    return 41\n')
            ctx = make_ctx(root)
            ops = build_ops([
                {
                    'type': 'EnsureReplaceExactOnce',
                    'label': 'meaning-42',
                    'file': 'pkg/service.py',
                    'old_text': '    return 41\n',
                    'new_text': '    return 42\n',
                }
            ])
            result = run_patch_pipeline(ctx, ops)
            self.assertEqual('verified', result.outcome)
            tx = result.transaction_record
            self.assertIsNotNone(tx)
            journal_path = Path(tx.journal_path)
            self.assertTrue(journal_path.exists())
            payload = json.loads(journal_path.read_text(encoding='utf-8'))
            self.assertEqual('committed', payload['phase'])
            self.assertEqual('committed', payload['transaction_status'])
            phases = [item['phase'] for item in payload.get('phase_history', [])]
            self.assertIn('apply_started', phases)
            self.assertIn('verification_passed', phases)
            self.assertEqual('verified', payload.get('final_state'))

    def test_transaction_journal_marks_rollback_success(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_phase2_rb_') as tmp_dir:
            root = Path(tmp_dir)
            pkg = root / 'pkg'
            pkg.mkdir(parents=True, exist_ok=True)
            target = pkg / 'service.py'
            original = 'def compute() -> int:\n    return 41\n'
            write_text(target, original)
            ctx = make_ctx(root)
            ops = build_ops([
                {
                    'type': 'EnsureReplaceExactOnce',
                    'label': 'meaning-42',
                    'file': 'pkg/service.py',
                    'old_text': '    return 41\n',
                    'new_text': '    return 42\n',
                }
            ])
            with patch('capatch_engine.patch_pipeline.run_required_verifiers', return_value=[
                {
                    'verifier_id': 'python-parse',
                    'ok': False,
                    'title': 'forced failure',
                    'detail': 'test induced verifier failure',
                }
            ]):
                result = run_patch_pipeline(ctx, ops)
            self.assertEqual('rolled-back', result.outcome)
            payload = json.loads(Path(result.transaction_record.journal_path).read_text(encoding='utf-8'))
            self.assertEqual('rollback_succeeded', payload['phase'])
            self.assertEqual('rolled_back', payload['transaction_status'])
            self.assertEqual(original, target.read_text(encoding='utf-8'))

    def test_transaction_journal_persists_strategy_batch_profile(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_phase2_strategy_') as tmp_dir:
            root = Path(tmp_dir)
            pkg = root / 'pkg'
            pkg.mkdir(parents=True, exist_ok=True)
            write_text(pkg / 'service.py', 'def compute() -> int:\n    return 41\n')
            ctx = make_ctx(root)
            ops = build_ops([
                {
                    'type': 'EnsureReplaceExactOnce',
                    'label': 'meaning-42',
                    'file': 'pkg/service.py',
                    'old_text': '    return 41\n',
                    'new_text': '    return 42\n',
                }
            ])
            result = run_patch_pipeline(ctx, ops)
            payload = json.loads(Path(result.transaction_record.journal_path).read_text(encoding='utf-8'))
            metadata = dict(payload.get('metadata') or {})
            self.assertEqual('exact', metadata.get('strategy_decision', {}).get('selected_strategy'))
            self.assertEqual('exact', metadata.get('batch_profile', {}).get('selected_strategy'))
            self.assertEqual(1, metadata.get('batch_profile', {}).get('target_count'))
            self.assertEqual(['pkg/service.py'], metadata.get('batch_profile', {}).get('targets'))


if __name__ == '__main__':
    unittest.main()
