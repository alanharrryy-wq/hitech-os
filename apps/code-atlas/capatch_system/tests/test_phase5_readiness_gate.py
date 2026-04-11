from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from capatch_runtime.readiness_gate import run_readiness_gate


class Phase5ReadinessGateTests(unittest.TestCase):
    def test_readiness_gate_promotable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_gate_") as tmp_dir:
            workspace = Path(tmp_dir)
            with patch("capatch_runtime.readiness_gate.capture_environment_guard", return_value={"base_dir": str(workspace), "target_exists": True}), \
                 patch("capatch_runtime.readiness_gate.evaluate_environment_guard", return_value={"status": "healthy", "reasons": [], "warnings": []}), \
                 patch("capatch_runtime.readiness_gate.run_windows_smoke", return_value={"status": "skipped", "reason": "not-windows"}), \
                 patch("capatch_runtime.readiness_gate.run_contract_smoke", return_value={"status": "passed", "issues": []}), \
                 patch("capatch_runtime.readiness_gate.run_rollback_drill", return_value={"status": "passed"}), \
                 patch("capatch_runtime.readiness_gate.list_baselines", return_value=[{"baseline_id": "b1"}]):
                payload = run_readiness_gate(workspace, None)
            self.assertEqual(payload["status"], "promotable")

    def test_readiness_gate_blocks_on_failed_checks(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_gate_") as tmp_dir:
            workspace = Path(tmp_dir)
            with patch("capatch_runtime.readiness_gate.capture_environment_guard", return_value={"base_dir": str(workspace), "target_exists": True}), \
                 patch("capatch_runtime.readiness_gate.evaluate_environment_guard", return_value={"status": "blocked", "reasons": ["bad"], "warnings": []}), \
                 patch("capatch_runtime.readiness_gate.run_windows_smoke", return_value={"status": "failed", "reason": "bad"}), \
                 patch("capatch_runtime.readiness_gate.run_contract_smoke", return_value={"status": "failed", "issues": ["bad"]}), \
                 patch("capatch_runtime.readiness_gate.run_rollback_drill", return_value={"status": "failed"}), \
                 patch("capatch_runtime.readiness_gate.list_baselines", return_value=[]):
                payload = run_readiness_gate(workspace, None)
            self.assertEqual(payload["status"], "blocked")
