from __future__ import annotations

import unittest

from tools.hos.git_sentinel_modular.remediation.repair import RepairPlanner
from tools.hos.git_sentinel_modular.shared.contracts import PredictionResult, ScanResult, ScanStats, SecurityFinding


class RepairPlannerTestCase(unittest.TestCase):
    def test_repair_marks_security_and_high_risk_predictions(self):
        planner = RepairPlanner()
        scan = ScanResult(
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
            stats=ScanStats(scanned_files=1, security_findings=1),
        ).validate()

        plan = planner.plan_repairs(
            scan,
            [
                PredictionResult(
                    candidate_path="src/config.env",
                    risk_score=0.91,
                    confidence=0.90,
                    rationale=["security:SEC_SECRET:critical"],
                ).validate()
            ],
        )
        self.assertTrue(plan.has_risky_actions)
        self.assertGreaterEqual(len(plan.risky_actions), 2)


if __name__ == "__main__":
    unittest.main()
