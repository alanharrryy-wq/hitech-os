from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.operations.execution_lock import ExecutionLock


class ExecutionLockTestCase(unittest.TestCase):
    def test_acquire_and_release(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        lock = ExecutionLock(Path(tmp.name) / "sentinel.lock")
        self.assertTrue(lock.acquire("test-owner"))
        self.assertFalse(lock.acquire("second-owner"))
        lock.release()
        self.assertTrue(lock.acquire("third-owner"))


if __name__ == "__main__":
    unittest.main()
