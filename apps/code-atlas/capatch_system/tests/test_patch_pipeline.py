from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.qa_testkit import build_ops, make_ctx, write_text

from capatch_engine.patch_pipeline import run_patch_pipeline


class PatchPipelineTests(unittest.TestCase):
    def test_patch_pipeline_verifies_successful_python_patch(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_pipeline_success_') as tmp_dir:
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
            self.assertIsNotNone(result.transaction_record)
            self.assertEqual('committed', result.transaction_record.phase)
            self.assertIsNotNone(result.run_record)
            self.assertEqual('applied', result.run_record.patch_status)
            self.assertEqual('verified', result.run_record.system_status)
            self.assertEqual('def compute() -> int:\n    return 42\n', target.read_text(encoding='utf-8'))

    def test_patch_pipeline_auto_rolls_back_when_required_verifier_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_pipeline_rollback_') as tmp_dir:
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
            self.assertIsNotNone(result.transaction_record)
            self.assertEqual('rollback_succeeded', result.transaction_record.phase)
            self.assertTrue(result.rollback_decision.get('should_rollback'))
            self.assertIsNotNone(result.rollback_event)
            self.assertEqual(original, target.read_text(encoding='utf-8'))
            self.assertIsNotNone(result.run_record)
            self.assertEqual('rolled_back', result.run_record.patch_status)
            self.assertEqual('rolled_back', result.run_record.system_status)

    def test_patch_pipeline_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_pipeline_dry_run_') as tmp_dir:
            root = Path(tmp_dir)
            pkg = root / 'pkg'
            pkg.mkdir(parents=True, exist_ok=True)
            target = pkg / 'service.py'
            original = 'def compute() -> int:\n    return 41\n'
            write_text(target, original)

            ctx = make_ctx(root, dry_run=True)
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

            self.assertEqual('dry-run', result.outcome)
            self.assertEqual(original, target.read_text(encoding='utf-8'))
            self.assertEqual(['python-parse', 'python-compile-smoke', 'python-import-smoke'], result.required_verifiers)

    def test_patch_pipeline_records_strategy_decision_and_transaction_metadata(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_pipeline_strategy_') as tmp_dir:
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

            self.assertEqual('exact', result.strategy_decision.get('selected_strategy'))
            self.assertFalse(result.strategy_decision.get('advisory_only'))
            self.assertIn('anchor-review', result.strategy_decision.get('recommended_guardrails', []))
            self.assertEqual('exact', result.risk_summary.get('selected_strategy'))
            metadata = dict(result.transaction_record.metadata or {})
            self.assertEqual('exact', metadata.get('strategy_decision', {}).get('selected_strategy'))
            self.assertEqual(1, metadata.get('batch_profile', {}).get('target_count'))

    def test_patch_pipeline_blocks_probe_only_strategy_without_dry_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_pipeline_probe_only_') as tmp_dir:
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
            forced_strategy = {
                'selected_strategy': 'probe-only',
                'selected_score': 0.22,
                'candidate_ranking': [{'strategy': 'probe-only', 'score': 0.22}],
                'operation_families': {'exact-text': 1},
                'planner_stub': {'enabled': True, 'hint': 'probe-only', 'source': 'test'},
                'anchor_confidence': 0.41,
                'syntax_confidence': 0.51,
                'semantic_confidence': 0.40,
                'batch_risk': 0.30,
                'rollback_readiness': 0.82,
                'overall_confidence': 0.41,
                'recommended_guardrails': ['dry-run-required'],
                'requires_future_executor': False,
                'executor_capabilities': {'advisory_only': False, 'families': ['read-only']},
                'advisory_only': False,
                'reasons': ['forced by test'],
            }
            with patch('capatch_engine.patch_pipeline.select_patch_strategy', return_value=forced_strategy):
                result = run_patch_pipeline(ctx, ops)

            self.assertEqual('blocked', result.outcome)
            self.assertEqual('probe-only', result.strategy_decision.get('selected_strategy'))
            self.assertIn('--dry-run', result.error or '')
            self.assertEqual(original, target.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
