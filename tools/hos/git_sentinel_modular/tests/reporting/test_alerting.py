from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.reporting.alerting import AlertDispatcher
from tools.hos.git_sentinel_modular.reporting.generator import SentinelReportGenerator
from tools.hos.git_sentinel_modular.shared.contracts import CleanupPlan, PredictionResult, RepairAction, RepairPlan, ScanResult, ScanStats, SecurityFinding


class AlertDispatcherTestCase(unittest.TestCase):
    def _make_report(self, risky: bool = False):
        generator = SentinelReportGenerator()
        repair_plan = RepairPlan(
            dry_run=True,
            risky_actions=[
                RepairAction(kind="delete", target_path="dist/app.js", reason="risky delete", safe=False)
            ] if risky else [],
        ).validate()
        return generator.build_report(
            scan_result=ScanResult(
                repo_root="F:/repos/hitech-os",
                scan_id="scan-001",
                security_findings=[
                    SecurityFinding(
                        rule_id="SEC_SECRET",
                        path="src/config.env",
                        severity="critical",
                        message="Potential inline secret assignment",
                        secret_like=True,
                    )
                ],
                stats=ScanStats(scanned_files=2, scanned_directories=1, security_findings=1),
            ).validate(),
            predictions=[
                PredictionResult(
                    candidate_path="src/config.env",
                    risk_score=0.88,
                    confidence=0.91,
                    rationale=["security:SEC_SECRET:critical"],
                ).validate()
            ],
            repair_plan=repair_plan,
            cleanup_plan=CleanupPlan(dry_run=True).validate(),
        )

    def test_build_payload_sets_error_on_risky_repairs(self):
        payload = AlertDispatcher().build_payload(self._make_report(risky=True))
        self.assertEqual(payload.severity, "error")

    def test_dispatch_to_file(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "alert.txt"
        out = AlertDispatcher().dispatch_to_file(self._make_report(), path)
        self.assertTrue(out.exists())
        self.assertIn("severity", out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
