
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


BUNDLE_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = BUNDLE_ROOT / 'ai_annotator_installer.py'


class InstallerContractTests(unittest.TestCase):
    def test_parser_surface_is_exact(self) -> None:
        import ai_annotator_installer as installer

        parser = installer.build_parser()
        options = sorted(action.option_strings[0] for action in parser._actions if action.option_strings)
        self.assertEqual(options, sorted(['--dry-run', '--apply', '--verify', '--rollback', '--root', '--log-dir', '--install-rel']))

    def test_root_is_required_and_has_no_implicit_default(self) -> None:
        import ai_annotator_installer as installer

        parser = installer.build_parser()
        root_action = next(action for action in parser._actions if '--root' in action.option_strings)
        self.assertTrue(root_action.required)
        self.assertIsNone(root_action.default)

    def test_missing_root_is_rejected(self) -> None:
        env = dict(os.environ)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        proc = subprocess.run([sys.executable, str(INSTALLER), '--dry-run'], capture_output=True, text=True, env=env)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('--root', proc.stderr)

    def test_full_flow(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'root'
            log_dir = Path(td) / 'logs'
            root.mkdir(parents=True)
            log_dir.mkdir(parents=True)
            env = dict(os.environ)
            env['PYTHONDONTWRITEBYTECODE'] = '1'
            commands = [
                [sys.executable, str(INSTALLER), '--dry-run', '--root', str(root), '--log-dir', str(log_dir)],
                [sys.executable, str(INSTALLER), '--apply', '--root', str(root), '--log-dir', str(log_dir)],
                [sys.executable, str(INSTALLER), '--verify', '--root', str(root), '--log-dir', str(log_dir)],
                [sys.executable, str(INSTALLER), '--rollback', '--root', str(root), '--log-dir', str(log_dir)],
            ]
            last_output = None
            outputs = []
            for command in commands:
                proc = subprocess.run(command, check=True, capture_output=True, text=True, env=env)
                payload = json.loads(proc.stdout)
                outputs.append(payload)
                last_output = payload
            self.assertIsNotNone(last_output)
            self.assertIn('mode', last_output)
            verify_output = next(item for item in outputs if item['mode'] == 'verify')
            self.assertEqual(verify_output['missing_files'], [])
            self.assertEqual(verify_output['hash_mismatches'], [])
            self.assertTrue(any(log_dir.iterdir()))


if __name__ == '__main__':
    unittest.main()
