from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest

THIS_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = THIS_DIR.parent


class InstallerCliTests(unittest.TestCase):
    def test_root_is_required(self) -> None:
        result = subprocess.run(
            [sys.executable, str(BUNDLE_ROOT / 'registry_builder_installer.py'), '--dry-run'],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--root', result.stderr)

    def test_help_surface_is_limited_to_canonical_flags(self) -> None:
        result = subprocess.run(
            [sys.executable, str(BUNDLE_ROOT / 'registry_builder_installer.py'), '--help'],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        help_text = result.stdout
        for flag in ['--dry-run', '--apply', '--verify', '--rollback', '--root', '--log-dir', '--install-rel']:
            self.assertIn(flag, help_text)
        for forbidden in ['--payload', '--bundle']:
            self.assertNotIn(forbidden, help_text)


if __name__ == '__main__':
    unittest.main()
