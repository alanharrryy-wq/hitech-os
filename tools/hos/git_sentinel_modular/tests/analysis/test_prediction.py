from __future__ import annotations

import unittest

from tools.hos.git_sentinel_modular.analysis.prediction import RuleBasedPredictionEngine
from tools.hos.git_sentinel_modular.shared.contracts import ArtifactFinding, ScanResult, ScanStats, SecurityFinding


class RuleBasedPredictionEngineTestCase(unittest.TestCase):
    def test_predict_combines_current_findings_and_history(self):
        engine = RuleBasedPredictionEngine()
        scan = ScanResult(
            repo_root="F:/repos/hitech-os",
            scan_id="scan-001",
            artifact_findings=[
                ArtifactFinding(
                    path="dist/app.js",
                    category="generated_code",
                    reason="generated dir",
                    confidence=0.90,
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
            stats=ScanStats(scanned_files=10, scanned_directories=4, artifact_findings=1, security_findings=1),
        ).validate()

        snapshot = {
            "file_churn": {
                "src/config.env": 3,
                "src/hotspot.py": 2,
            }
        }

        predictions = engine.predict(scan, snapshot)
        self.assertGreaterEqual(len(predictions), 2)
        self.assertEqual(predictions[0].candidate_path, "src/config.env")
        self.assertTrue(any("historical_churn:3" in reason for reason in predictions[0].rationale))

    def test_predictions_are_capped_and_sorted(self):
        engine = RuleBasedPredictionEngine()
        scan = ScanResult(
            repo_root="F:/repos/hitech-os",
            scan_id="scan-001",
            security_findings=[
                SecurityFinding(
                    rule_id="SEC_PRIVATE_KEY",
                    path="src/private.pem",
                    severity="critical",
                    message="Potential private key material",
                    secret_like=True,
                )
            ],
            stats=ScanStats(scanned_files=2, scanned_directories=1, security_findings=1),
        ).validate()

        snapshot = {"file_churn": {"src/private.pem": 10}}
        predictions = engine.predict(scan, snapshot)
        self.assertLessEqual(predictions[0].risk_score, 0.99)
        self.assertGreater(predictions[0].confidence, 0.55)


if __name__ == "__main__":
    unittest.main()
