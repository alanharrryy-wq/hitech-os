from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "tools" / "scripts" / "run_factory_phase1_extract.ps1"


def _powershell_executable() -> str | None:
    for name in ("powershell", "pwsh"):
        found = shutil.which(name)
        if found:
            return found
    return None


class Phase1ScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ps = _powershell_executable()

    def setUp(self) -> None:
        if os.name != "nt" or not self.ps:
            self.skipTest("PowerShell script tests run only on Windows with powershell/pwsh available")

    def _make_fake_bin(self, scenario: str) -> Path:
        temp_dir = Path(tempfile.mkdtemp(prefix="factory_ps1_test_")).resolve()
        fake_py = temp_dir / "fake_python.py"
        fake_cmd = temp_dir / "python.cmd"
        fake_git = temp_dir / "git.cmd"

        fake_py.write_text(
            (
                "import json, os, sys\n"
                "scenario = os.getenv('FACTORY_TEST_SCENARIO', 'pass')\n"
                "args = sys.argv[1:]\n"
                "joined = ' '.join(args)\n"
                "if '-c' in args:\n"
                "    idx = args.index('-c')\n"
                "    expr = args[idx + 1] if idx + 1 < len(args) else ''\n"
                "    if 'import tools.codex.factory' in expr:\n"
                "        sys.exit(0)\n"
                "if 'doctor' in args:\n"
                "    print(json.dumps({'status': 'PASS', 'schema_version': 1}, sort_keys=True))\n"
                "    sys.exit(0)\n"
                "if 'operator' in args and 'phase1-extract' in args:\n"
                "    if scenario == 'huge_stderr_pass':\n"
                "        sys.stderr.write('E' * 300000 + '\\n')\n"
                "        print(json.dumps({'command': 'operator phase1-extract', 'run_id': 'RUN_TEST_001', 'status': 'PASS', 'stage_last_completed': 'watch worker statuses', 'resume_hint': 'none'}, sort_keys=True))\n"
                "        sys.exit(0)\n"
                "    if scenario == 'noisy_multi_json':\n"
                "        print('noise-before-json')\n"
                "        print(json.dumps({'foo': 1}, sort_keys=True))\n"
                "        print(json.dumps({'command': 'operator phase1-extract', 'run_id': 'RUN_OLD_001', 'status': 'BLOCKED', 'stage_failed': 'preflight', 'resume_hint': 'old hint'}, sort_keys=True))\n"
                "        print('noise-middle')\n"
                "        print(json.dumps({'command': 'operator phase1-extract', 'run_id': 'RUN_NEW_999', 'status': 'PASS', 'stage_last_completed': 'watch worker statuses', 'resume_hint': 'new hint'}, sort_keys=True))\n"
                "        sys.exit(0)\n"
                "    if scenario == 'nonzero_with_json':\n"
                "        sys.stderr.write('operator failed but emitted json\\n')\n"
                "        print(json.dumps({'command': 'operator phase1-extract', 'run_id': 'RUN_BLOCKED_777', 'status': 'BLOCKED', 'stage_failed': 'init-run', 'reason': 'simulated failure', 'resume_hint': 'rerun with fixes'}, sort_keys=True))\n"
                "        sys.exit(2)\n"
                "    print(json.dumps({'command': 'operator phase1-extract', 'run_id': 'RUN_DEFAULT_001', 'status': 'PASS', 'stage_last_completed': 'watch worker statuses', 'resume_hint': 'none'}, sort_keys=True))\n"
                "    sys.exit(0)\n"
                "print('unexpected args: ' + joined)\n"
                "sys.exit(0)\n"
            ),
            encoding="utf-8",
            newline="\n",
        )

        fake_cmd.write_text(
            f'@echo off\r\n"{sys.executable}" "{fake_py.as_posix()}" %*\r\n',
            encoding="utf-8",
            newline="\r\n",
        )
        fake_git.write_text(
            "@echo off\r\n"
            "if \"%1\"==\"status\" exit /b 0\r\n"
            "if \"%1\"==\"rev-parse\" (\r\n"
            "  echo deadbeefdeadbeefdeadbeefdeadbeefdeadbeef\r\n"
            "  exit /b 0\r\n"
            ")\r\n"
            "exit /b 0\r\n",
            encoding="utf-8",
            newline="\r\n",
        )
        return temp_dir

    def _run_script(self, *, scenario: str, extra_args: list[str] | None = None, timeout: int = 60) -> subprocess.CompletedProcess[str]:
        fake_bin = self._make_fake_bin(scenario)
        self.addCleanup(lambda: shutil.rmtree(fake_bin, ignore_errors=True))

        env = os.environ.copy()
        env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
        env["FACTORY_TEST_SCENARIO"] = scenario

        cmd = [
            self.ps,
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT_PATH),
            "-BaseRef",
            "HEAD",
            "-SkipDoctor",
            "-DryRun",
            "-NoOpenVscode",
            "-NoOpenRunboard",
            "-NoOpenFinalReport",
        ]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            env=env,
            timeout=timeout,
        )

    def test_deadlock_safe_capture_with_large_stderr(self) -> None:
        proc = self._run_script(scenario="huge_stderr_pass", extra_args=["-NoLogs", "-Quiet"], timeout=60)
        self.assertEqual(0, proc.returncode, msg=proc.stdout + "\n" + proc.stderr)
        self.assertIn("run_id=RUN_TEST_001", proc.stdout)
        self.assertIn("status=PASS", proc.stdout)

    def test_noisy_output_parser_picks_last_best_json(self) -> None:
        proc = self._run_script(scenario="noisy_multi_json", extra_args=["-NoLogs", "-Quiet"], timeout=60)
        self.assertEqual(0, proc.returncode, msg=proc.stdout + "\n" + proc.stderr)
        self.assertIn("run_id=RUN_NEW_999", proc.stdout)
        self.assertNotIn("run_id=RUN_OLD_001", proc.stdout)

    def test_nonzero_exit_still_uses_json_stage_fields(self) -> None:
        proc = self._run_script(scenario="nonzero_with_json", extra_args=["-NoLogs"], timeout=60)
        self.assertEqual(22, proc.returncode, msg=proc.stdout + "\n" + proc.stderr)
        self.assertIn("run_id: RUN_BLOCKED_777", proc.stdout)
        self.assertIn("stage_failed: init-run", proc.stdout)
        self.assertIn("reason: simulated failure", proc.stdout)
        self.assertIn("resume_hint: rerun with fixes", proc.stdout)

    def test_log_uses_utc_iso_timestamp(self) -> None:
        proc = self._run_script(scenario="noisy_multi_json", extra_args=[], timeout=60)
        self.assertEqual(0, proc.returncode, msg=proc.stdout + "\n" + proc.stderr)
        match = re.search(r"logs doctor=(.+?) phase=(.+)", proc.stdout)
        self.assertIsNotNone(match, msg=proc.stdout)
        phase_log = Path(match.group(2).strip())
        self.assertTrue(phase_log.exists(), msg=f"phase log missing: {phase_log}")
        content = phase_log.read_text(encoding="utf-8")
        self.assertRegex(content, r"time_utc:\s*\d{4}-\d{2}-\d{2}T[0-9:\.]+(?:\+00:00|Z)")


if __name__ == "__main__":
    unittest.main()
