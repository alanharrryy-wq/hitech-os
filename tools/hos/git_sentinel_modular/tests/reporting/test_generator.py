from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.reporting.generator import SentinelReportGenerator
from tools.hos.git_sentinel_modular.shared.contracts import (
    ArtifactFinding,
    CleanupPlan,
    PredictionResult,
    RepairPlan,
    ScanResult,
    ScanStats,
    SecurityFinding,
)


class SentinelReportGeneratorTestCase(unittest.TestCase):
    def _make_scan(self) -> ScanResult:
        return ScanResult(
            repo_root="F:/repos/hitech-os",
            scan_id="scan-001",
            artifact_findings=[
                ArtifactFinding(
                    path="dist/app.js",
                    category="generated_code",
                    reason="generated dir",
                    confidence=0.80,
                )
            ],
            security_findings=[
                SecurityFinding(
                    rule_id="SEC_SECRET",
                    path="src/config.env",
                    severity="critical",
                    message="Potential inline secret assignment",
                    secret_like=True,
                )
            ],
            stats=ScanStats(scanned_files=10, scanned_directories=3, artifact_findings=1, security_findings=1),
        ).validate()

    def test_build_report_and_bundle(self):
        generator = SentinelReportGenerator()
        report = generator.build_report(
            scan_result=self._make_scan(),
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
        self.assertEqual(report.summary["prediction_count"], 1)
        bundle = generator.to_bundle(report)
        self.assertIn("Top predictions", bundle.markdown_text)

    def test_write_bundle(self):
        generator = SentinelReportGenerator()
        report = generator.build_report(
            scan_result=self._make_scan(),
            predictions=[],
            repair_plan=RepairPlan(dry_run=True).validate(),
            cleanup_plan=CleanupPlan(dry_run=True).validate(),
        )
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        json_path = Path(tmp.name) / "report.json"
        md_path = Path(tmp.name) / "report.md"
        generator.write_bundle(report, json_path, md_path)
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())


if __name__ == "__main__":
    unittest.main()
