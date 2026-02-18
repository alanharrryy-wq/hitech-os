from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import orchestrator, worktrees  # noqa: E402
from factory.tests.test_support import isolated_factory_env  # noqa: E402


class OperatorOrchestratorTests(unittest.TestCase):
    def test_prompt_generation_is_deterministic(self) -> None:
        with isolated_factory_env() as env:
            run_id = "operator_prompt_determinism_001"
            base_ref = "HEAD"
            workers = ["A_worker", "B_worker", "C_worker", "D_worker"]

            for worker in workers:
                (env["codex_dir"] / "worktrees" / run_id / worker).mkdir(parents=True, exist_ok=True)

            first = orchestrator.generate_phase_prompts(
                run_id=run_id,
                base_ref=base_ref,
                phase="phase1-extract",
                workers=workers,
                dry_run=True,
            )
            second = orchestrator.generate_phase_prompts(
                run_id=run_id,
                base_ref=base_ref,
                phase="phase1-extract",
                workers=workers,
                dry_run=True,
            )
            self.assertEqual(first, second)

    def test_worker_sorting_is_stable(self) -> None:
        workers = orchestrator.normalize_workers("D_worker,A_worker,C_worker,A_worker")
        self.assertEqual(["A_worker", "C_worker", "D_worker"], workers)

    def test_watch_handles_missing_status_files_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="operator_watch_") as temp_dir:
            runs_dir = Path(temp_dir).resolve()
            payload = orchestrator.watch_for_worker_statuses(
                run_id="operator_watch_missing_001",
                workers=["A_worker", "B_worker"],
                runs_dir=runs_dir,
                sleep_sec=1,
                timeout_min=0,
                dry_run=False,
            )
            self.assertEqual("BLOCKED", payload["status"])
            self.assertFalse(payload["ready"])
            self.assertEqual(["A_worker", "B_worker"], payload["missing"])

    def test_worktrees_open_builds_code_args_in_dry_run(self) -> None:
        with isolated_factory_env() as env:
            run_id = "operator_open_args_001"
            worktree_root = env["codex_dir"] / "worktrees" / run_id
            (worktree_root / "A_worker").mkdir(parents=True, exist_ok=True)
            (worktree_root / "B_worker").mkdir(parents=True, exist_ok=True)

            with patch("factory.worktrees.subprocess.run") as mocked_subprocess:
                payload = worktrees.open_worktrees(
                    run_id,
                    workers=["B_worker", "A_worker"],
                    dry_run=True,
                    new_window=True,
                    goto="PROMPT_WORKER.txt",
                )
                mocked_subprocess.assert_not_called()

            ordered_workers = [step["worker"] for step in payload["steps"]]
            self.assertEqual(["A_worker", "B_worker"], ordered_workers)

            first_cmd = payload["steps"][0]["actions"][0]["cmd"]
            expected_first_goto = (worktree_root / "A_worker" / "PROMPT_WORKER.txt").as_posix()
            self.assertEqual(["code", "-n", "--goto", expected_first_goto], first_cmd)


if __name__ == "__main__":
    unittest.main()
