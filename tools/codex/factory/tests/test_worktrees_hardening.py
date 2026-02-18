from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import common, worktrees  # noqa: E402
from factory.tests.test_support import isolated_factory_env  # noqa: E402


class WorktreeHardeningTests(unittest.TestCase):
    def test_worktree_path_under_codex_worktrees(self) -> None:
        with isolated_factory_env() as env:
            run_id = "worktree_hard_20260218_000001"
            path = worktrees.worktree_path(run_id, "A_worker")
            expected = env["codex_dir"] / "worktrees" / run_id / "A_worker"
            self.assertEqual(expected, path)

    def test_create_worktrees_writes_state_file(self) -> None:
        with isolated_factory_env() as env:
            run_id = "worktree_hard_20260218_000002"
            payload = worktrees.create_worktrees(run_id, workers=list(common.WORKERS), base_ref="HEAD", dry_run=True)
            self.assertEqual("PASS", payload["status"])
            state_file = env["runs_dir"] / run_id / "WORKTREE_STATE.json"
            self.assertTrue(state_file.exists())

    def test_create_worktrees_blocked_when_run_lock_exists(self) -> None:
        with isolated_factory_env() as env:
            run_id = "worktree_hard_20260218_000003"
            lock_file = env["runs_dir"] / run_id / "locks" / "run.lock"
            lock_file.parent.mkdir(parents=True, exist_ok=True)
            lock_file.write_text("held\n", encoding="utf-8")

            payload = worktrees.create_worktrees(run_id, workers=list(common.WORKERS), base_ref="HEAD", dry_run=True)
            self.assertEqual("BLOCKED", payload["status"])
            self.assertIn("lock_error", payload)


if __name__ == "__main__":
    unittest.main()

