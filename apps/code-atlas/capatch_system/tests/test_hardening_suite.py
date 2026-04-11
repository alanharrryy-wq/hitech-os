from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.qa_testkit import ROOT

from tooling.run_hardening_suite import run_hardening_suite


class HardeningSuiteTests(unittest.TestCase):
    def test_hardening_suite_aggregates_child_checks(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_hardening_suite_") as tmp_dir:
            with patch("tooling.run_hardening_suite.run_suite", return_value={"metrics": {"fix_success_rate": 0.75}}):
                with patch(
                    "tooling.run_hardening_suite.run_rollback_drill",
                    return_value={"status": "passed", "conflict_preview_detected": True, "multi_run_restore_ok": True},
                ):
                    with patch("tooling.run_hardening_suite.run_windows_smoke", return_value={"status": "skipped", "reason": "not windows"}):
                        payload = run_hardening_suite(ROOT, Path(tmp_dir), quick=True)
            self.assertEqual("passed", payload["status"])
            self.assertTrue((Path(tmp_dir) / "hardening_suite.json").exists())
            self.assertTrue((Path(tmp_dir) / "hardening_suite.md").exists())


if __name__ == "__main__":
    unittest.main()
