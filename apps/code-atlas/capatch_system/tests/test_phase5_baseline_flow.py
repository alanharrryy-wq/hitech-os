from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from capatch_audit.baseline_registry import (
    compare_baseline,
    promote_checkpoint_to_baseline,
    promote_run_to_baseline,
    restore_baseline,
    write_baseline,
)
from capatch_audit.renderers import write_json


class Phase5BaselineFlowTests(unittest.TestCase):
    def test_write_and_compare_baseline(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_baseline_") as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "pkg" / "file.txt"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("alpha\n", encoding="utf-8")
            record = write_baseline(
                workspace,
                label="gold",
                target_files=["pkg/file.txt"],
                verification_snapshot=[{"verifier_id": "x", "ok": True}],
                notes="ok",
            )
            target.write_text("beta\n", encoding="utf-8")
            compare_payload = compare_baseline(workspace, record.baseline_id)
            self.assertTrue(compare_payload["drifted"])
            self.assertEqual(compare_payload["drift_count"], 1)

    def test_promote_run_requires_verified_system_status(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_baseline_") as tmp_dir:
            workspace = Path(tmp_dir)
            reports = workspace / "reports" / "patch_runs"
            reports.mkdir(parents=True, exist_ok=True)
            write_json(
                reports / "run_bad.json",
                {
                    "run_id": "run_bad",
                    "patch_status": "applied",
                    "system_status": "caution",
                    "target_files": ["a.txt"],
                    "verifier_results": [{"verifier_id": "x", "ok": False}],
                    "git_branch": "main",
                    "git_head": "deadbeef",
                    "rollback_target": None,
                },
            )
            with self.assertRaises(ValueError):
                promote_run_to_baseline(workspace, run_id="run_bad", label="bad")

    def test_promote_checkpoint_and_restore(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_baseline_") as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "pkg" / "file.txt"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("stable\n", encoding="utf-8")
            checkpoint_dir = workspace / "reports" / "checkpoints" / "cp_001"
            (checkpoint_dir / "pkg").mkdir(parents=True, exist_ok=True)
            (checkpoint_dir / "pkg" / "file.txt").write_text("stable\n", encoding="utf-8")
            write_json(
                workspace / "reports" / "checkpoints" / "cp_001.json",
                {
                    "checkpoint_id": "cp_001",
                    "checkpoint_path": str(checkpoint_dir),
                    "target_files": ["pkg/file.txt"],
                    "run_id": "run_ok",
                },
            )
            record = promote_checkpoint_to_baseline(
                workspace,
                checkpoint_id="cp_001",
                label="cp baseline",
                verification_snapshot=[{"verifier_id": "x", "ok": True}],
            )
            target.write_text("mutated\n", encoding="utf-8")
            restored = restore_baseline(workspace, record.baseline_id)
            self.assertEqual(restored["status"], "restored")
            self.assertEqual(target.read_text(encoding="utf-8"), "stable\n")
