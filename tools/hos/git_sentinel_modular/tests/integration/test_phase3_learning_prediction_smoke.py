from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.analysis.prediction import RuleBasedPredictionEngine
from tools.hos.git_sentinel_modular.learning.engine import SQLiteLearningStore
from tools.hos.git_sentinel_modular.shared.contracts import ArtifactFinding, ScanResult, ScanStats, SecurityFinding


class Phase3LearningPredictionSmokeTestCase(unittest.TestCase):
    def test_learning_then_prediction_smoke(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)

        db_path = Path(tmp.name) / "learning.sqlite3"
        repo_root = str((Path(tmp.name) / "repo").resolve())
        store = SQLiteLearningStore(db_path)

        scan = ScanResult(
            repo_root=repo_root,
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
            stats=ScanStats(scanned_files=6, scanned_directories=2, artifact_findings=1, security_findings=1),
        ).validate()

        snapshot = store.update_from_scan(scan)
        predictions = RuleBasedPredictionEngine().predict(scan, snapshot)
        self.assertTrue(predictions)
        self.assertEqual(predictions[0].candidate_path, "src/config.env")


if __name__ == "__main__":
    unittest.main()
