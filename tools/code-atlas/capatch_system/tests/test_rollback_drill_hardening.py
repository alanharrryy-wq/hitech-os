from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.qa_testkit import ROOT

from tooling.run_rollback_drill import run_rollback_drill


class RollbackDrillHardeningTests(unittest.TestCase):
    def test_rollback_drill_detects_conflict_and_restores_multi_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_rollback_harden_") as tmp_dir:
            payload = run_rollback_drill(ROOT, Path(tmp_dir))
            self.assertEqual("passed", payload["status"])
            self.assertTrue(payload["conflict_preview_detected"])
            self.assertTrue(payload["multi_run_restore_ok"])
            self.assertTrue((Path(tmp_dir) / "rollback_drill.json").exists())
            self.assertTrue((Path(tmp_dir) / "rollback_drill.md").exists())


if __name__ == "__main__":
    unittest.main()
