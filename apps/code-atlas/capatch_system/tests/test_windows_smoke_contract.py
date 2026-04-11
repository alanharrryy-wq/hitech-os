from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.qa_testkit import ROOT

from tooling.run_windows_smoke import (
    DEFAULT_REQUIRED_PLUGINS,
    build_windows_steps,
    determine_smoke_status,
    parse_required_plugins,
    run_windows_smoke,
)


class WindowsSmokeContractTests(unittest.TestCase):
    def test_non_windows_returns_skipped_report(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_windows_skip_") as tmp_dir:
            report = run_windows_smoke(ROOT, Path(tmp_dir))
            self.assertIn(report["status"], {"skipped", "passed", "degraded"})
            self.assertIn("generated_at_utc", report)
            if report["status"] == "skipped":
                self.assertIn("Windows", report["reason"])

    def test_windows_step_builder_contains_expected_commands(self) -> None:
        steps = build_windows_steps(ROOT, Path("C:/temp/work space"), Path("C:/temp/ops smoke.json"))
        names = [step["name"] for step in steps]
        self.assertEqual(
            ["smoke-test", "plugin-health", "apply", "list-checkpoints", "rollback-last"],
            names,
        )
        apply_step = next(step for step in steps if step["name"] == "apply")
        argv_text = " ".join(apply_step["argv"])
        self.assertIn("capatch.py", argv_text)
        self.assertIn("--ops-file", argv_text)
        self.assertIn("--root-dir", argv_text)
        self.assertIn("work space", argv_text)

    def test_required_plugin_parser_handles_commas_and_semicolons(self) -> None:
        self.assertEqual(["a", "b", "c"], parse_required_plugins("a,b;c"))
        self.assertEqual(DEFAULT_REQUIRED_PLUGINS, parse_required_plugins(None))

    def test_status_can_fail_when_plugin_health_rejects_required_plugin(self) -> None:
        steps = [
            {"name": "smoke-test", "returncode": 0, "stdout": "ok", "stderr": ""},
            {
                "name": "plugin-health",
                "returncode": 0,
                "stdout": "verifier_post_fix_verifier rejected by runtime\n",
                "stderr": "",
            },
            {"name": "apply", "returncode": 0, "stdout": "ok", "stderr": ""},
            {"name": "list-checkpoints", "returncode": 0, "stdout": "ok", "stderr": ""},
            {"name": "rollback-last", "returncode": 0, "stdout": "ok", "stderr": ""},
        ]
        status, reason, detail = determine_smoke_status(steps, required_plugins=["verifier_post_fix_verifier"])
        self.assertEqual("failed", status)
        self.assertIn("rejected", reason)
        self.assertEqual(["verifier_post_fix_verifier"], detail["rejected"])

    def test_windows_mode_can_be_simulated_without_real_subprocesses(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_windows_fake_") as tmp_dir:
            output_dir = Path(tmp_dir)

            class _Completed:
                def __init__(self, returncode: int = 0, stdout: str = "ok", stderr: str = "") -> None:
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            fake_rows = [
                _Completed(0, "smoke ok"),
                _Completed(0, "plugin verifier_post_fix_verifier active\nfixer.safe-runtime-actions active\nrecommender.safe-fix-plan active"),
                _Completed(0, "apply ok"),
                _Completed(0, "checkpoint ok"),
                _Completed(0, "rollback ok"),
            ]

            with patch("tooling.run_windows_smoke.platform.system", return_value="Windows"):
                with patch("tooling.run_windows_smoke.subprocess.run", side_effect=fake_rows):
                    report = run_windows_smoke(ROOT, output_dir, required_plugins=["verifier_post_fix_verifier", "fixer.safe-runtime-actions", "recommender.safe-fix-plan"])
            self.assertEqual("passed", report["status"])
            self.assertEqual(5, len(report["steps"]))
            self.assertTrue((output_dir / "windows_smoke.json").exists())
            self.assertIn("environment_fingerprint", report)


if __name__ == "__main__":
    unittest.main()
