from __future__ import annotations

import sys
import tempfile
import io
from contextlib import redirect_stdout
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import cli, locks  # noqa: E402
from factory.tests.test_support import isolated_factory_env  # noqa: E402


class LockTests(unittest.TestCase):
    def test_file_lock_acquire_and_release(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lock_basic_") as temp_dir:
            lock_path = Path(temp_dir) / "basic.lock"
            lock = locks.FileLock(path=lock_path, owner="test", metadata={})
            lock.acquire()
            self.assertTrue(lock_path.exists())
            lock.release()
            self.assertFalse(lock_path.exists())

    def test_second_lock_acquire_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lock_collision_") as temp_dir:
            lock_path = Path(temp_dir) / "collision.lock"
            first = locks.FileLock(path=lock_path, owner="first", metadata={}).acquire()
            try:
                with self.assertRaises(locks.LockAcquisitionError):
                    locks.FileLock(path=lock_path, owner="second", metadata={}).acquire()
            finally:
                first.release()

    def test_run_lock_helpers(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lock_helpers_") as temp_dir:
            runs_dir = Path(temp_dir) / "runs"
            runs_dir.mkdir(parents=True, exist_ok=True)
            with patch.object(locks, "RUNS_DIR", runs_dir):
                acquired = locks.acquire_run_lock("run1", owner="owner")
                self.assertTrue((runs_dir / "run1" / "locks" / "run.lock").exists())
                acquired.release()
                self.assertFalse((runs_dir / "run1" / "locks" / "run.lock").exists())

    def test_worker_lock_helpers(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lock_worker_") as temp_dir:
            runs_dir = Path(temp_dir) / "runs"
            runs_dir.mkdir(parents=True, exist_ok=True)
            with patch.object(locks, "RUNS_DIR", runs_dir):
                acquired = locks.acquire_worker_lock("run2", "A_worker", owner="owner")
                self.assertTrue((runs_dir / "run2" / "locks" / "A_worker.lock").exists())
                acquired.release()
                self.assertFalse((runs_dir / "run2" / "locks" / "A_worker.lock").exists())

    def test_second_launch_is_blocked_when_run_lock_exists(self) -> None:
        with isolated_factory_env() as env:
            run_id = "lock_launch_20260218_000001"
            lock_dir = env["runs_dir"] / run_id / "locks"
            lock_dir.mkdir(parents=True, exist_ok=True)
            (lock_dir / "run.lock").write_text("held\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                rc = cli.main(["launch", "--run-id", run_id, "--base-ref", "HEAD", "--dry-run"])
            self.assertNotEqual(0, rc)


if __name__ == "__main__":
    unittest.main()
