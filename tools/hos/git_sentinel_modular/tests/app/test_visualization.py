from __future__ import annotations

import unittest

from tools.hos.git_sentinel_modular.app.visualization import build_dashboard_state, build_kpi_cards, build_marker_summary, build_next_actions
from tools.hos.git_sentinel_modular.reporting.generator import SentinelReportGenerator
from tools.hos.git_sentinel_modular.shared.contracts import CleanupPlan, PredictionResult, RepairPlan, ScanResult, ScanStats, SecurityFinding


class VisualizationTestCase(unittest.TestCase):
    def _make_report(self):
        return SentinelReportGenerator().build_report(
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
                stats=ScanStats(scanned_files=3, scanned_directories=1, security_findings=1),
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

    def test_build_kpis_and_actions(self):
        report = self._make_report()
        self.assertEqual(len(build_kpi_cards(report)), 4)
        self.assertTrue(build_next_actions(report))

    def test_build_dashboard_state(self):
        state = build_dashboard_state(self._make_report())
        self.assertIn("kpis", state)
        self.assertIn("top_predictions", state)

    def test_marker_summary(self):
        summary = build_marker_summary(self._make_report())
        self.assertTrue(summary["has_next_best_actions"])
        self.assertTrue(summary["has_what_this_means"])


if __name__ == "__main__":
    unittest.main()
