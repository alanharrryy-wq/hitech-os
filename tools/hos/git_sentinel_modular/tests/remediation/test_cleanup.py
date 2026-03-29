from __future__ import annotations

import unittest

from tools.hos.git_sentinel_modular.remediation.cleanup import CleanupPlanner
from tools.hos.git_sentinel_modular.shared.contracts import ArtifactFinding, ScanResult, ScanStats


class CleanupPlannerTestCase(unittest.TestCase):
    def test_cleanup_blocks_outside_prefix(self):
        planner = CleanupPlanner()
        scan = ScanResult(
            repo_root="F:/repos/hitech-os",
            scan_id="scan-001",
            artifact_findings=[
                ArtifactFinding(
                    path="src/domain/service.py",
                    category="generated_code",
                    reason="bad classification for test",
                    confidence=0.75,
                )
            ],
            stats=ScanStats(scanned_files=1, artifact_findings=1),
        ).validate()
        plan = planner.plan_cleanup(scan)
        self.assertEqual(len(plan.actions), 0)
        self.assertEqual(len(plan.blocked_actions), 1)

    def test_cleanup_allows_local_reports(self):
        planner = CleanupPlanner()
        scan = ScanResult(
            repo_root="F:/repos/hitech-os",
            scan_id="scan-001",
            artifact_findings=[
                ArtifactFinding(
                    path="tools/_reports/report.json",
                    category="report",
                    reason="generated report",
                    confidence=0.95,
                )
            ],
            stats=ScanStats(scanned_files=1, artifact_findings=1),
        ).validate()
        plan = planner.plan_cleanup(scan)
        self.assertEqual(len(plan.actions), 1)


if __name__ == "__main__":
    unittest.main()
