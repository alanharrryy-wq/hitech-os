from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.qa_testkit import ROOT, write_text


def _extract_last_json(stdout: str) -> dict[str, object]:
    for line in reversed(stdout.splitlines()):
        candidate = line.strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            return json.loads(candidate)
    raise AssertionError(f"No se encontro payload JSON en stdout:\n{stdout}")


class CliDryRunContractTests(unittest.TestCase):
    def _run_capatch(self, root_dir: Path, extra_args: list[str]) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CAPATCH_SKIP_CLEANER"] = "1"
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "capatch.py"),
                "--root-dir",
                str(root_dir),
                *extra_args,
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )

    def _write_python_canary_ops(self, root_dir: Path) -> Path:
        ops_path = root_dir / "ops.json"
        payload = [
            {
                "type": "EnsureReplaceExactOnce",
                "label": "meaning-42",
                "file": "pkg/service.py",
                "old_text": "    return 41\n",
                "new_text": "    return 42\n",
            }
        ]
        ops_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return ops_path

    def test_dry_run_success_returns_zero_and_does_not_write_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_cli_dry_contract_") as tmp_dir:
            root = Path(tmp_dir)
            target = root / "pkg" / "service.py"
            original = "def compute() -> int:\n    return 41\n"
            write_text(target, original)
            ops_path = self._write_python_canary_ops(root)

            result = self._run_capatch(root, ["--ops-file", str(ops_path), "--dry-run"])

            self.assertEqual(0, result.returncode, result.stdout + "\n" + result.stderr)
            self.assertEqual(original, target.read_text(encoding="utf-8"))
            self.assertIn("Preview listo. No se escribieron cambios.", result.stdout)
            self.assertNotIn("[ERROR]", result.stdout)

    def test_json_contract_for_patch_apply_and_dry_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_cli_json_contract_") as tmp_dir:
            root = Path(tmp_dir)
            target = root / "pkg" / "service.py"
            write_text(target, "def compute() -> int:\n    return 41\n")
            ops_path = self._write_python_canary_ops(root)

            dry_run = self._run_capatch(root, ["--ops-file", str(ops_path), "--dry-run", "--json-output"])
            self.assertEqual(0, dry_run.returncode, dry_run.stdout + "\n" + dry_run.stderr)
            dry_payload = _extract_last_json(dry_run.stdout)
            self.assertEqual("ok", dry_payload["status"])
            self.assertEqual("dry-run", dry_payload["outcome"])
            self.assertEqual(True, dry_payload["dry_run"])
            self.assertEqual(str(root.resolve()), dry_payload["root_dir"])
            self.assertIn("reason", dry_payload)
            self.assertIn("verification_outcome", dry_payload)

            apply_run = self._run_capatch(root, ["--ops-file", str(ops_path), "--json-output"])
            self.assertEqual(0, apply_run.returncode, apply_run.stdout + "\n" + apply_run.stderr)
            apply_payload = _extract_last_json(apply_run.stdout)
            self.assertEqual("ok", apply_payload["status"])
            self.assertIn(apply_payload["outcome"], {"verified", "applied-no-verifiers"})
            self.assertEqual(False, apply_payload["dry_run"])
            self.assertEqual(str(root.resolve()), apply_payload["root_dir"])
            self.assertIn("checkpoint_id", apply_payload)
            self.assertIn("verification_outcome", apply_payload)

    def test_json_contract_for_smoke_and_rollback_last_preview(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_cli_json_smoke_") as tmp_dir:
            root = Path(tmp_dir)

            smoke = self._run_capatch(root, ["--smoke-test", "--json-output"])
            self.assertEqual(0, smoke.returncode, smoke.stdout + "\n" + smoke.stderr)
            smoke_payload = _extract_last_json(smoke.stdout)
            self.assertEqual("ok", smoke_payload["status"])
            self.assertEqual("smoke-test", smoke_payload["outcome"])
            self.assertEqual(False, smoke_payload["dry_run"])
            self.assertEqual(str(root.resolve()), smoke_payload["root_dir"])
            self.assertIn("reason", smoke_payload)

            rollback_preview = self._run_capatch(root, ["--rollback-last", "--dry-run", "--json-output"])
            self.assertEqual(0, rollback_preview.returncode, rollback_preview.stdout + "\n" + rollback_preview.stderr)
            rollback_payload = _extract_last_json(rollback_preview.stdout)
            self.assertEqual("skipped", rollback_payload["status"])
            self.assertEqual("rollback-last", rollback_payload["outcome"])
            self.assertEqual("no_checkpoints", rollback_payload["reason"])
            self.assertEqual(True, rollback_payload["dry_run"])
            self.assertEqual(str(root.resolve()), rollback_payload["root_dir"])
            self.assertIn("checkpoint_id", rollback_payload)
            self.assertIn("verification_outcome", rollback_payload)
            self.assertIn("data", rollback_payload)


if __name__ == "__main__":
    unittest.main()
