from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.learning.engine import SQLiteLearningStore
from tools.hos.git_sentinel_modular.operations.execution_lock import ExecutionLock
from tools.hos.git_sentinel_modular.operations.scheduler import SentinelScheduler


class Phase5RemediationOperationsSmokeTestCase(unittest.TestCase):
    def test_scheduler_with_lock_smoke(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name) / "repo"
        (repo / ".git").mkdir(parents=True, exist_ok=True)
        (repo / "src").mkdir()
        (repo / "src" / "config.env").write_text("SECRET=my-secret\n", encoding="utf-8")
        (repo / "tools" / "_reports").mkdir(parents=True, exist_ok=True)
        (repo / "tools" / "_reports" / "audit_report.json").write_text("{}", encoding="utf-8")

        lock = ExecutionLock(Path(tmp.name) / "scheduler.lock")
        self.assertTrue(lock.acquire("phase5-smoke"))
        db_path = Path(tmp.name) / "learning.sqlite3"
        tick = SentinelScheduler(learning_store=SQLiteLearningStore(db_path)).run_once(str(repo))
        self.assertTrue(tick.report.predictions)
        lock.release()


if __name__ == "__main__":
    unittest.main()
