from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from capatch_fs.workspace_lock import (
    acquire_workspace_lock,
    collect_target_snapshot,
    diff_target_snapshot,
    force_release_workspace_lock,
    lock_path_for_root,
)


class Phase5WorkspaceLockTests(unittest.TestCase):
    def test_lock_acquire_release_cycle(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_lock_") as tmp_dir:
            workspace = Path(tmp_dir)
            lock = acquire_workspace_lock(workspace, owner_token="alpha", wait_timeout_seconds=0.2)
            self.assertTrue(Path(lock.lock_path).exists())
            lock.release()
            self.assertFalse(Path(lock.lock_path).exists())

    def test_lock_times_out_when_busy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_lock_") as tmp_dir:
            workspace = Path(tmp_dir)
            lock = acquire_workspace_lock(workspace, owner_token="alpha", wait_timeout_seconds=0.2)
            with self.assertRaises(TimeoutError):
                acquire_workspace_lock(workspace, owner_token="beta", wait_timeout_seconds=0.25, retry_interval_seconds=0.05)
            lock.release()

    def test_stale_lock_is_released(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_lock_") as tmp_dir:
            workspace = Path(tmp_dir)
            lock = acquire_workspace_lock(workspace, owner_token="alpha", wait_timeout_seconds=0.2)
            lock_path = Path(lock.lock_path)
            old = time.time() - 10
            os.utime(lock_path, (old, old))
            stale = acquire_workspace_lock(workspace, owner_token="beta", wait_timeout_seconds=0.2, stale_after_seconds=1)
            self.assertEqual(stale.owner_token, "beta")
            stale.release()

    def test_snapshot_diff_detects_hash_change(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_lock_") as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "demo.txt"
            target.write_text("one\n", encoding="utf-8")
            before = collect_target_snapshot(workspace, ["demo.txt"])
            target.write_text("two\n", encoding="utf-8")
            after = collect_target_snapshot(workspace, ["demo.txt"])
            diff = diff_target_snapshot(before, after)
            self.assertEqual(diff[0]["reason"], "hash_changed")

    def test_force_release_returns_previous_owner(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_lock_") as tmp_dir:
            workspace = Path(tmp_dir)
            acquire_workspace_lock(workspace, owner_token="alpha", wait_timeout_seconds=0.2)
            result = force_release_workspace_lock(workspace, reason="test")
            self.assertTrue(result["released"])
            self.assertEqual(result["previous_owner"]["owner_token"], "alpha")
            self.assertFalse(lock_path_for_root(workspace).exists())
