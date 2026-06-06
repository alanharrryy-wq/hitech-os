from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from capatch_cli.commands_audit import handle
from capatch_engine.patch_pipeline import run_patch_pipeline
from tests.qa_testkit import build_ops, make_ctx, write_text


def _args(root_dir: Path, **overrides: object) -> SimpleNamespace:
    payload: dict[str, object] = {
        'root_dir': str(root_dir),
        'json_output': True,
        'dry_run': False,
        'list_checkpoints': False,
        'rollback_run': None,
        'rollback_checkpoint': None,
        'rollback_last': False,
        'show_run': None,
        'show_rollback_command': None,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _invoke(args: SimpleNamespace) -> dict[str, object]:
    capture = io.StringIO()
    with redirect_stdout(capture):
        result = handle(args)
    assert result == 0
    output = capture.getvalue().strip()
    assert output
    return json.loads(output)


class AuditCommandFlowTests(unittest.TestCase):
    def test_audit_list_load_preview_apply_and_rollback_last_contracts(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_audit_cmd_') as tmp_dir:
            root = Path(tmp_dir)
            target = root / 'pkg' / 'service.py'
            original = 'def compute() -> int:\n    return 41\n'
            write_text(target, original)

            ctx = make_ctx(root)
            ops = build_ops(
                [
                    {
                        'type': 'EnsureReplaceExactOnce',
                        'label': 'meaning-42',
                        'file': 'pkg/service.py',
                        'old_text': '    return 41\n',
                        'new_text': '    return 42\n',
                    }
                ]
            )
            pipeline = run_patch_pipeline(ctx, ops)
            self.assertEqual('verified', pipeline.outcome)
            self.assertIsNotNone(pipeline.run_record)
            run_id = str(pipeline.run_record.run_id)
            checkpoint_id = Path(str(pipeline.run_record.rollback_target or '')).name
            self.assertTrue(checkpoint_id)

            list_payload = _invoke(_args(root, list_checkpoints=True))
            self.assertEqual('list-checkpoints', list_payload['outcome'])
            self.assertEqual('ok', list_payload['status'])
            checkpoints = list_payload['data']
            self.assertTrue(isinstance(checkpoints, list) and checkpoints)

            show_payload = _invoke(_args(root, show_run=run_id))
            self.assertEqual('show-run', show_payload['outcome'])
            self.assertEqual(run_id, show_payload['data']['run_id'])

            rollback_cmd_payload = _invoke(_args(root, show_rollback_command=run_id))
            self.assertEqual('show-rollback-command', rollback_cmd_payload['outcome'])
            self.assertIn('--rollback-checkpoint', rollback_cmd_payload['data']['rollback_apply_command'])

            preview_payload = _invoke(_args(root, rollback_checkpoint=checkpoint_id, dry_run=True))
            self.assertEqual('rollback-checkpoint', preview_payload['outcome'])
            self.assertEqual('ok', preview_payload['status'])
            self.assertTrue(preview_payload['data']['restore_ok'])

            apply_payload = _invoke(_args(root, rollback_checkpoint=checkpoint_id, dry_run=False))
            self.assertEqual('rollback-checkpoint', apply_payload['outcome'])
            self.assertEqual('ok', apply_payload['status'])
            self.assertIn(apply_payload['data']['status'], {'restored', 'restored_with_warnings'})
            self.assertEqual(original, target.read_text(encoding='utf-8'))

            rollback_last_payload = _invoke(_args(root, rollback_last=True, dry_run=True))
            self.assertEqual('rollback-last', rollback_last_payload['outcome'])
            self.assertIn(rollback_last_payload['status'], {'ok', 'skipped'})


if __name__ == '__main__':
    unittest.main()
