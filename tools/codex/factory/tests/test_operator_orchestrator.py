from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import cli, orchestrator, worktrees  # noqa: E402
from factory.tests.test_support import isolated_factory_env  # noqa: E402


class OperatorOrchestratorTests(unittest.TestCase):
    def test_auto_run_id_selects_001_when_none_exist(self) -> None:
        with isolated_factory_env() as env:
            run_id, source = orchestrator.select_run_id_for_phase(
                phase="phase1-extract",
                explicit_run_id=None,
                strict=False,
                runs_dir=env["runs_dir"],
                prompts_dir=env["codex_dir"] / "prompts",
                worktrees_dir=env["codex_dir"] / "worktrees",
            )
            self.assertEqual("RUN_PHASE1_EXTRACT_001", run_id)
            self.assertEqual("auto", source)

    def test_auto_run_id_selects_002_when_001_is_occupied(self) -> None:
        with isolated_factory_env() as env:
            occupied = "RUN_PHASE1_EXTRACT_001"
            (env["runs_dir"] / occupied).mkdir(parents=True, exist_ok=True)
            run_id, source = orchestrator.select_run_id_for_phase(
                phase="phase1-extract",
                explicit_run_id=None,
                strict=False,
                runs_dir=env["runs_dir"],
                prompts_dir=env["codex_dir"] / "prompts",
                worktrees_dir=env["codex_dir"] / "worktrees",
            )
            self.assertEqual("RUN_PHASE1_EXTRACT_002", run_id)
            self.assertEqual("auto", source)

    def test_list_existing_run_ids_is_sorted_and_deterministic(self) -> None:
        with isolated_factory_env() as env:
            runs_dir = env["runs_dir"]
            prompts_dir = env["codex_dir"] / "prompts"
            worktrees_dir = env["codex_dir"] / "worktrees"
            for run_id in [
                "RUN_PHASE1_EXTRACT_010",
                "RUN_PHASE1_EXTRACT_002",
                "RUN_PHASE1_EXTRACT_001",
                "RUN_PHASE1_EXTRACT_ABC",
                "RUN_OTHER_PHASE_001",
            ]:
                (runs_dir / run_id).mkdir(parents=True, exist_ok=True)
            (prompts_dir / "RUN_PHASE1_EXTRACT_002").mkdir(parents=True, exist_ok=True)
            (worktrees_dir / "RUN_PHASE1_EXTRACT_001").mkdir(parents=True, exist_ok=True)

            first = orchestrator.list_existing_run_ids(
                runs_dir=runs_dir,
                prompts_dir=prompts_dir,
                worktrees_dir=worktrees_dir,
                prefix="RUN_PHASE1_EXTRACT",
            )
            second = orchestrator.list_existing_run_ids(
                runs_dir=runs_dir,
                prompts_dir=prompts_dir,
                worktrees_dir=worktrees_dir,
                prefix="RUN_PHASE1_EXTRACT",
            )

            self.assertEqual(first, second)
            self.assertEqual(
                [
                    "RUN_PHASE1_EXTRACT_001",
                    "RUN_PHASE1_EXTRACT_002",
                    "RUN_PHASE1_EXTRACT_010",
                ],
                first,
            )

    def test_operator_bootstrap_retries_next_run_id_on_first_collision(self) -> None:
        with isolated_factory_env():
            attempts: list[str] = []
            real_generate = cli.generate_phase_prompts

            def _collision_then_pass(*, run_id: str, base_ref: str, phase: str, workers: list[str], dry_run: bool) -> dict[str, object]:
                attempts.append(run_id)
                if len(attempts) == 1:
                    raise orchestrator.OperatorCollisionError("simulated prompt collision")
                return real_generate(run_id=run_id, base_ref=base_ref, phase=phase, workers=workers, dry_run=dry_run)

            with patch("factory.cli.generate_phase_prompts", side_effect=_collision_then_pass):
                payload = cli._operator_bootstrap_payload(
                    run_id=None,
                    strict_run_id=False,
                    base_ref="HEAD",
                    workers_raw="A_worker,B_worker,C_worker,D_worker",
                    phase="phase1-extract",
                    open_vscode=False,
                    goto_prompt=True,
                    open_runboard=False,
                    dry_run=True,
                    config_path=None,
                )

            self.assertEqual("PASS", payload["status"])
            self.assertEqual("RUN_PHASE1_EXTRACT_002", payload["run_id"])
            self.assertEqual(["RUN_PHASE1_EXTRACT_001", "RUN_PHASE1_EXTRACT_002"], attempts)

    def test_operator_bootstrap_strict_run_id_blocks_on_collision(self) -> None:
        with isolated_factory_env() as env:
            run_id = "RUN_PHASE1_EXTRACT_001"
            (env["runs_dir"] / run_id).mkdir(parents=True, exist_ok=True)

            payload = cli._operator_bootstrap_payload(
                run_id=run_id,
                strict_run_id=True,
                base_ref="HEAD",
                workers_raw="A_worker,B_worker,C_worker,D_worker",
                phase="phase1-extract",
                open_vscode=False,
                goto_prompt=True,
                open_runboard=False,
                dry_run=True,
                config_path=None,
            )

            self.assertEqual("BLOCKED", payload["status"])
            self.assertEqual("init-run", payload["stage_failed"])
            self.assertEqual("Use --run-id auto or choose a new run-id.", payload["resume_hint"])
            self.assertEqual(run_id, payload["run_id"])

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

    def test_worker_prompt_header_prefix_is_byte_identical(self) -> None:
        run_id = "RUN_PHASE1_EXTRACT_777"
        base_ref = "HEAD"
        phase = "phase1-extract"
        spec = orchestrator.get_phase_spec(phase)
        worker_spec = spec["workers"]["A_worker"]
        rendered = orchestrator.render_worker_prompt(
            run_id=run_id,
            base_ref=base_ref,
            phase=phase,
            worker="A_worker",
            worker_spec=worker_spec,
        )

        expected_header = (
            "# HITECH-OS Worker Prompt\n"
            "RUN_ID: RUN_PHASE1_EXTRACT_777\n"
            "PHASE: phase1-extract\n"
            "WORKER_ID: A_worker\n"
            "BASE_REF: HEAD\n"
            "\n"
            "## Mission Scope\n"
            "- Scaffold packages/render-core, packages/module-registry, packages/desktop-bridge.\n"
            "\n"
            "## Repo Write Scope\n"
            "- packages/desktop-bridge/**\n"
            "- packages/module-registry/**\n"
            "- packages/render-core/**\n"
            "\n"
            "## Artifact Write Root (Required)\n"
            "- tools/codex/runs/RUN_PHASE1_EXTRACT_777/A_worker/\n"
            "\n"
            "Only write standard bundle artifacts under this root:\n"
            "- STATUS.json\n"
            "- SUMMARY.md\n"
            "- FILES_CHANGED.json\n"
            "- DIFF.patch\n"
            "- SUGGESTIONS.md\n"
            "- SCOPE_LOCK.json\n"
            "- HANDOFF_NOTE.json\n"
            "- LOGS/INDEX.json\n"
            "\n"
            "## Hard Constraints\n"
            "- Determinism only: stable ordering, no random IDs, no UUIDs.\n"
            "- Do not modify protected paths: .git/**, .env*, .github/workflows/**.\n"
            "- Abort immediately on out-of-scope writes or path collisions.\n"
            "- Abort immediately if another worker owns a path you plan to change.\n"
            "\n"
            "## Worker-Specific Constraints\n"
            "- No runtime business logic.\n"
            "- Scaffold only.\n"
            "\n"
            "## Completion Signal\n"
            "- Write STATUS.json to tools/codex/runs/RUN_PHASE1_EXTRACT_777/A_worker/STATUS.json\n"
            "\n"
            "## Abort Conditions\n"
            "- Collision detected in prompt artifacts or worker outputs.\n"
            "- Requested change is outside declared scope.\n"
            "- Required path ownership is ambiguous.\n"
        )

        self.assertTrue(rendered.startswith(expected_header))
        self.assertIn("## === ENRICHED PLAYBOOK ===", rendered)

    def test_enriched_playbook_differs_per_worker(self) -> None:
        run_id = "RUN_PHASE1_EXTRACT_778"
        base_ref = "HEAD"
        phase = "phase1-extract"
        spec = orchestrator.get_phase_spec(phase)

        prompt_a = orchestrator.render_worker_prompt(
            run_id=run_id,
            base_ref=base_ref,
            phase=phase,
            worker="A_worker",
            worker_spec=spec["workers"]["A_worker"],
        )
        prompt_b = orchestrator.render_worker_prompt(
            run_id=run_id,
            base_ref=base_ref,
            phase=phase,
            worker="B_worker",
            worker_spec=spec["workers"]["B_worker"],
        )

        marker = "## === ENRICHED PLAYBOOK ==="
        enriched_a = marker + prompt_a.split(marker, 1)[1]
        enriched_b = marker + prompt_b.split(marker, 1)[1]
        self.assertNotEqual(enriched_a, enriched_b)
        self.assertIn("render, registry, and desktop bridge modules", enriched_a)
        self.assertIn("deterministic tooling primitives", enriched_b)

    def test_enriched_playbook_has_no_new_scope_globs(self) -> None:
        run_id = "RUN_PHASE1_EXTRACT_779"
        base_ref = "HEAD"
        phase = "phase1-extract"
        spec = orchestrator.get_phase_spec(phase)
        marker = "## === ENRICHED PLAYBOOK ==="

        for worker in sorted(spec["workers"]):
            prompt = orchestrator.render_worker_prompt(
                run_id=run_id,
                base_ref=base_ref,
                phase=phase,
                worker=worker,
                worker_spec=spec["workers"][worker],
            )
            enriched = marker + prompt.split(marker, 1)[1]
            self.assertNotIn("/**", enriched)

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
            self.assertTrue(str(first_cmd[0]).lower().endswith(("code", "code.cmd", "code.exe")))
            self.assertEqual(["-n", "--goto", expected_first_goto], first_cmd[1:])

    def test_worktrees_open_resolves_code_executable_on_windows(self) -> None:
        with isolated_factory_env() as env:
            run_id = "operator_open_exec_001"
            worktree_root = env["codex_dir"] / "worktrees" / run_id
            (worktree_root / "A_worker").mkdir(parents=True, exist_ok=True)

            with patch("factory.worktrees.shutil.which", return_value="C:/VSCode/bin/code.CMD"):
                with patch("factory.worktrees.subprocess.run") as mocked_subprocess:
                    mocked_subprocess.return_value.returncode = 0
                    mocked_subprocess.return_value.stdout = ""
                    mocked_subprocess.return_value.stderr = ""
                    payload = worktrees.open_worktrees(
                        run_id,
                        workers=["A_worker"],
                        dry_run=False,
                        new_window=True,
                        goto="PROMPT_WORKER.txt",
                    )

            self.assertEqual("PASS", payload["status"])
            called_args = mocked_subprocess.call_args[0][0]
            self.assertEqual("C:/VSCode/bin/code.CMD", called_args[0])

    def test_run_external_command_resolves_executable(self) -> None:
        with patch("factory.orchestrator.shutil.which", return_value="C:/VSCode/bin/code.CMD"):
            with patch("factory.orchestrator.subprocess.run") as mocked_subprocess:
                mocked_subprocess.return_value.returncode = 0
                mocked_subprocess.return_value.stdout = "ok"
                mocked_subprocess.return_value.stderr = ""
                result = orchestrator.run_external_command(["code", "--version"], dry_run=False)

        self.assertEqual(0, result["rc"])
        self.assertEqual("C:/VSCode/bin/code.CMD", result["cmd"][0])


if __name__ == "__main__":
    unittest.main()
