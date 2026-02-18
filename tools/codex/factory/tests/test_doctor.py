from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.doctor import run_doctor  # noqa: E402
from factory.tests.test_support import isolated_factory_env  # noqa: E402


class DoctorTests(unittest.TestCase):
    def test_doctor_passes_in_isolated_env(self) -> None:
        with isolated_factory_env():
            payload = run_doctor()
            self.assertIn(payload["status"], {"PASS", "BLOCKED"})
            self.assertIn("checks", payload)
            self.assertGreater(len(payload["checks"]), 5)

    def test_doctor_reports_missing_required_path(self) -> None:
        with isolated_factory_env() as env:
            required = env["repo_root"] / "tools" / "codex" / "run.py"
            required.unlink()
            payload = run_doctor()
            self.assertEqual("BLOCKED", payload["status"])


if __name__ == "__main__":
    unittest.main()

