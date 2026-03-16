from __future__ import annotations

import unittest

from tools.hos.git_sentinel_modular.operations.ci_gate import CIGateEvaluator
from tools.hos.git_sentinel_modular.reporting.generator import SentinelReportGenerator
from tools.hos.git_sentinel_modular.shared.contracts import CleanupPlan, RepairAction, RepairPlan, ScanResult, ScanStats, SecurityFinding


class CIGateEvaluatorTestCase(unittest.TestCase):
    def test_blocks_on_security_findings(self):
        report = SentinelReportGenerator().build_report(
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
                stats=ScanStats(scanned_files=1, security_findings=1),
            ).validate(),
            predictions=[],
            repair_plan=RepairPlan(dry_run=True).validate(),
            cleanup_plan=CleanupPlan(dry_run=True).validate(),
        )
        result = CIGateEvaluator().evaluate(report)
        self.assertFalse(result.ok)
        self.assertEqual(result.status, "blocked")

    def test_blocks_on_risky_repairs(self):
        report = SentinelReportGenerator().build_report(
            scan_result=ScanResult(
                repo_root="F:/repos/hitech-os",
                scan_id="scan-001",
                stats=ScanStats(scanned_files=1),
            ).validate(),
            predictions=[],
            repair_plan=RepairPlan(
                dry_run=True,
                risky_actions=[RepairAction(kind="notify", target_path="src/x.py", reason="manual review", safe=False).validate()],
            ).validate(),
            cleanup_plan=CleanupPlan(dry_run=True).validate(),
        )
        result = CIGateEvaluator().evaluate(report)
        self.assertFalse(result.ok)


if __name__ == "__main__":
    unittest.main()
