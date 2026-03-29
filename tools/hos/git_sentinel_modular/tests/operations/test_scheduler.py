from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.learning.engine import SQLiteLearningStore
from tools.hos.git_sentinel_modular.operations.scheduler import SentinelScheduler


class SentinelSchedulerTestCase(unittest.TestCase):
    def test_run_once(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name) / "repo"
        (repo / ".git").mkdir(parents=True, exist_ok=True)
        (repo / "src").mkdir()
        (repo / "src" / "config.env").write_text("SECRET=my-secret\n", encoding="utf-8")
        (repo / "dist").mkdir()
        (repo / "dist" / "app.js").write_text("console.log('x')\n", encoding="utf-8")

        db_path = Path(tmp.name) / "learning.sqlite3"
        scheduler = SentinelScheduler(learning_store=SQLiteLearningStore(db_path))
        tick = scheduler.run_once(str(repo))
        self.assertEqual(tick.report.scan_result.repo_root, str(repo.resolve()))
        self.assertFalse(tick.ci_gate.ok)


if __name__ == "__main__":
    unittest.main()
