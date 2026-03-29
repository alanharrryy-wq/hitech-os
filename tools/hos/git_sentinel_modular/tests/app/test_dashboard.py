from __future__ import annotations

import unittest

from tools.hos.git_sentinel_modular.app.dashboard import build_dashboard_payload, build_dashboard_snapshot
from tools.hos.git_sentinel_modular.reporting.generator import SentinelReportGenerator
from tools.hos.git_sentinel_modular.shared.contracts import CleanupPlan, PredictionResult, RepairPlan, ScanResult, ScanStats


class DashboardTestCase(unittest.TestCase):
    def _make_report(self):
        return SentinelReportGenerator().build_report(
            scan_result=ScanResult(
                repo_root="F:/repos/hitech-os",
                scan_id="scan-001",
                stats=ScanStats(scanned_files=3, scanned_directories=1),
            ).validate(),
            predictions=[
                PredictionResult(
                    candidate_path="src/config.env",
                    risk_score=0.88,
                    confidence=0.91,
                    rationale=["historical_churn:3"],
                ).validate()
            ],
            repair_plan=RepairPlan(dry_run=True).validate(),
            cleanup_plan=CleanupPlan(dry_run=True).validate(),
        )

    def test_payload_and_snapshot(self):
        report = self._make_report()
        payload = build_dashboard_payload(report)
        snapshot = build_dashboard_snapshot(report)
        self.assertIn("state", payload)
        self.assertEqual(snapshot["scan_id"], "scan-001")


if __name__ == "__main__":
    unittest.main()
