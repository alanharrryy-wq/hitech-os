from __future__ import annotations

import json
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

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

    def test_open_worktrees_blocked_when_code_missing_captures_stderr(self) -> None:
        with isolated_factory_env():
            run_id = "worktree_hard_20260218_000004"
            for worker in common.WORKERS:
                target = worktrees.worktree_path(run_id, worker)
                target.mkdir(parents=True, exist_ok=True)

            with patch.object(worktrees, "_resolve_code_cli", return_value=None):
                payload = worktrees.open_worktrees(run_id, workers=list(common.WORKERS), dry_run=False)

            self.assertEqual("BLOCKED", payload["status"])
            self.assertEqual(len(common.WORKERS), payload["blocked"])
            for step in payload["steps"]:
                self.assertEqual("BLOCKED", step["status"])
                self.assertIn("code CLI command not found", step["actions"][0]["stderr"])

    def test_cleanup_vscode_sessions_stale_pid_writes_report(self) -> None:
        with isolated_factory_env() as env:
            run_id = "worktree_hard_20260218_000005"
            old_run_id = "worktree_hard_20260218_000001"
            session_path = env["runs_dir"] / old_run_id / "_debug" / "VSCODE_SESSION.json"
            session_path.parent.mkdir(parents=True, exist_ok=True)
            session_path.write_text(
                json.dumps(
                    {
                        "run_id": old_run_id,
                        "sessions": [
                            {
                                "run_id": old_run_id,
                                "worker": "A_core",
                                "opened_folder_path": "F:/fake/worktree/A_core",
                                "pid": 999999,
                                "window_handle": None,
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )

            with patch.dict(os.environ, {"HITECH_FACTORY_VSCODE_CLEAN": "1", "HITECH_FACTORY_VSCODE_NUKE": "0"}, clear=False):
                with patch.object(worktrees, "_probe_pid_ownership", return_value={"exists": False, "is_code": False}):
                    report = worktrees._cleanup_vscode_sessions(run_id)

            self.assertTrue(report["clean_enabled"])
            self.assertEqual(1, report["sessions_found"])
            cleanup_report = env["runs_dir"] / run_id / "_debug" / "VSCODE_CLEANUP_REPORT.txt"
            self.assertTrue(cleanup_report.exists())
            text = cleanup_report.read_text(encoding="utf-8")
            self.assertIn("worktree_hard_20260218_000001|A_core|999999|F:/fake/worktree/A_core", text)
            self.assertIn("already_gone", text)

    def test_open_worktrees_writes_session_registry(self) -> None:
        with isolated_factory_env() as env:
            run_id = "worktree_hard_20260218_000006"
            for worker in common.WORKERS:
                target = worktrees.worktree_path(run_id, worker)
                target.mkdir(parents=True, exist_ok=True)

            def _fake_open(args: list[str], cwd: Path | None = None, dry_run: bool = False, timeout_seconds: float = 30.0) -> dict[str, object]:
                return {
                    "cmd": args,
                    "cwd": str(cwd or worktrees.REPO_ROOT),
                    "rc": 0,
                    "stdout": "",
                    "stderr": "",
                    "dry_run": dry_run,
                    "wrapper_pid": 3100,
                }

            with patch.object(worktrees, "_resolve_code_cli", return_value="code.cmd"):
                with patch.object(worktrees, "_run_with_wrapper_pid", side_effect=_fake_open):
                    with patch.object(worktrees, "_resolve_code_pid_from_wrapper", return_value=4200):
                        with patch.object(worktrees, "_cleanup_vscode_sessions", return_value={"clean_enabled": True, "nuke_enabled": False, "sessions_found": 0, "actions": [], "report": ""}):
                            with patch.object(worktrees, "_list_code_pids", return_value=[]):
                                payload = worktrees.open_worktrees(run_id, workers=list(common.WORKERS), dry_run=False)

            self.assertEqual("PASS", payload["status"])
            session_registry = env["runs_dir"] / run_id / "_debug" / "VSCODE_SESSION.json"
            self.assertTrue(session_registry.exists())
            data = json.loads(session_registry.read_text(encoding="utf-8"))
            self.assertEqual(run_id, data["run_id"])
            self.assertEqual(len(common.WORKERS), len(data["sessions"]))
            for row in data["sessions"]:
                self.assertEqual(4200, row["pid"])

    def test_cleanup_skips_non_code_pid(self) -> None:
        with isolated_factory_env() as env:
            run_id = "worktree_hard_20260218_000007"
            old_run_id = "worktree_hard_20260218_000001"
            session_path = env["runs_dir"] / old_run_id / "_debug" / "VSCODE_SESSION.json"
            session_path.parent.mkdir(parents=True, exist_ok=True)
            session_path.write_text(
                json.dumps(
                    {
                        "run_id": old_run_id,
                        "sessions": [
                            {
                                "run_id": old_run_id,
                                "worker": "A_core",
                                "opened_folder_path": "F:/fake/worktree/A_core",
                                "pid": 1111,
                                "window_handle": None,
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )

            with patch.dict(os.environ, {"HITECH_FACTORY_VSCODE_CLEAN": "1", "HITECH_FACTORY_VSCODE_NUKE": "0"}, clear=False):
                with patch.object(worktrees, "_probe_pid_ownership", return_value={"exists": True, "is_code": False}):
                    with patch.object(worktrees, "_list_code_pids", return_value=[]):
                        report = worktrees._cleanup_vscode_sessions(run_id)

            self.assertEqual(1, report["sessions_found"])
            self.assertEqual("ownership_mismatch", report["actions"][0]["action"])


if __name__ == "__main__":
    unittest.main()
