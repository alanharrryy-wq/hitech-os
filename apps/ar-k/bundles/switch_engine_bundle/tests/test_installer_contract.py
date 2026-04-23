from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from contracts.shared_canon import (
    DEFAULT_INSTALL_REL,
    FINAL_STATUS,
    LAST_APPLY_REL,
    REQUIRED_SWITCH_ARTIFACTS,
    STATE_REL,
)


class InstallerContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle_root = Path(__file__).resolve().parents[1]
        self.installer = self.bundle_root / 'switch_engine_installer.py'

    def run_installer(self, *args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, str(self.installer), *args]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != expect:
            raise AssertionError(
                f'installer returned {result.returncode}, expected {expect}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'
            )
        return result

    def test_root_is_required(self) -> None:
        result = subprocess.run(
            [sys.executable, str(self.installer), '--dry-run'],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--root', result.stderr)

    def test_end_to_end_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir) / 'delivery-root'
            log_dir = Path(tempdir) / 'logs'
            root.mkdir(parents=True, exist_ok=True)

            dry = self.run_installer('--dry-run', '--root', str(root), '--log-dir', str(log_dir))
            dry_payload = json.loads(dry.stdout[dry.stdout.find('{'):])
            self.assertEqual(Path(dry_payload['install_root']), root / DEFAULT_INSTALL_REL)
            self.assertEqual(Path(dry_payload['state_root']), root / STATE_REL)
            self.assertEqual(Path(dry_payload['state_file']), root / LAST_APPLY_REL)

            apply = self.run_installer('--apply', '--root', str(root), '--log-dir', str(log_dir))
            apply_payload = json.loads(apply.stdout[apply.stdout.find('{'):])
            install_root = Path(apply_payload['install_root'])
            self.assertEqual(install_root, root / DEFAULT_INSTALL_REL)
            self.assertTrue((root / LAST_APPLY_REL).exists())

            verify = self.run_installer('--verify', '--root', str(root), '--log-dir', str(log_dir))
            verify_payload = json.loads(verify.stdout[verify.stdout.find('{'):])
            example_outputs = verify_payload['example_outputs']
            self.assertEqual(sorted(example_outputs), sorted(REQUIRED_SWITCH_ARTIFACTS))
            for name in REQUIRED_SWITCH_ARTIFACTS:
                self.assertTrue(Path(example_outputs[name]).exists())
                self.assertTrue(str(Path(example_outputs[name])).startswith(str(root / STATE_REL / 'verify_outputs')))

            rollback = self.run_installer('--rollback', '--root', str(root), '--log-dir', str(log_dir))
            rollback_payload = json.loads(rollback.stdout[rollback.stdout.find('{'):])
            self.assertTrue(rollback_payload['rolled_back'])
            self.assertFalse((install_root / 'switch_engine_installer.py').exists())

    def test_final_report_status(self) -> None:
        report = (self.bundle_root / 'FINAL_REPORT.md').read_text(encoding='utf-8')
        self.assertIn(FINAL_STATUS, report)


if __name__ == '__main__':
    unittest.main()
