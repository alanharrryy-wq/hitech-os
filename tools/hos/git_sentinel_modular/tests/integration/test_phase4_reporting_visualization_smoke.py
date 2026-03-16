from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.app.visualization import build_dashboard_state
from tools.hos.git_sentinel_modular.reporting.alerting import AlertDispatcher
from tools.hos.git_sentinel_modular.reporting.generator import SentinelReportGenerator
from tools.hos.git_sentinel_modular.shared.contracts import CleanupPlan, PredictionResult, RepairPlan, ScanResult, ScanStats, SecurityFinding


class Phase4ReportingVisualizationSmokeTestCase(unittest.TestCase):
    def test_report_to_visualization_and_alert_smoke(self):
        generator = SentinelReportGenerator()
        report = generator.build_report(
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
                stats=ScanStats(scanned_files=4, scanned_directories=2, security_findings=1),
            ).validate(),
            predictions=[
                PredictionResult(
                    candidate_path="src/config.env",
                    risk_score=0.88,
                    confidence=0.91,
                    rationale=["security:SEC_SECRET:critical"],
                ).validate()
            ],
            repair_plan=RepairPlan(dry_run=True).validate(),
            cleanup_plan=CleanupPlan(dry_run=True).validate(),
        )

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        json_path = Path(tmp.name) / "report.json"
        md_path = Path(tmp.name) / "report.md"
        alert_path = Path(tmp.name) / "alert.txt"

        generator.write_bundle(report, json_path, md_path)
        AlertDispatcher().dispatch_to_file(report, alert_path)
        state = build_dashboard_state(report)

        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        self.assertTrue(alert_path.exists())
        self.assertEqual(state["top_predictions"][0]["path"], "src/config.env")


if __name__ == "__main__":
    unittest.main()
