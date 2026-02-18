from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]


class CliEntrypointTests(unittest.TestCase):
    def test_package_module_help_prints(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "tools.codex.factory", "--help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode)
        self.assertIn("usage:", proc.stdout.lower())
        self.assertIn("doctor", proc.stdout)

    def test_module_help_prints(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "tools.codex.factory.cli", "--help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode)
        self.assertIn("usage:", proc.stdout.lower())
        self.assertIn("oneshot", proc.stdout)
        self.assertNotIn("RuntimeWarning", proc.stderr)

    def test_module_version_prints(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "tools.codex.factory", "--version"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode)
        self.assertIn("2.0.0-block-b", proc.stdout.strip())

    def test_file_execution_help_prints(self) -> None:
        proc = subprocess.run(
            [sys.executable, "tools/codex/factory/cli.py", "--help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode)
        self.assertIn("usage:", proc.stdout.lower())
        self.assertIn("bundle-validate", proc.stdout)


if __name__ == "__main__":
    unittest.main()
