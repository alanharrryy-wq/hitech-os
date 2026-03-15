from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.learning.engine import SQLiteLearningStore
from tools.hos.git_sentinel_modular.shared.contracts import ArtifactFinding, ScanResult, ScanStats, SecurityFinding


class SQLiteLearningStoreTestCase(unittest.TestCase):
    def _make_store(self) -> tuple[SQLiteLearningStore, str]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        db_path = Path(tmp.name) / "learning.sqlite3"
        store = SQLiteLearningStore(db_path)
        repo_root = str((Path(tmp.name) / "repo").resolve())
        return store, repo_root

    def test_load_default_snapshot(self):
        store, repo_root = self._make_store()
        payload = store.load_snapshot(repo_root)
        self.assertEqual(payload["repo_root"], repo_root)
        self.assertEqual(payload["total_scans"], 0)

    def test_update_from_scan_accumulates_counts(self):
        store, repo_root = self._make_store()
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
            stats=ScanStats(scanned_files=5, scanned_directories=2, artifact_findings=1, security_findings=1),
        ).validate()

        payload = store.update_from_scan(scan)
        self.assertEqual(payload["total_scans"], 1)
        self.assertEqual(payload["file_churn"]["dist/app.js"], 1)
        self.assertEqual(payload["security_rule_hits"]["SEC_SECRET"], 1)

        payload2 = store.update_from_scan(scan)
        self.assertEqual(payload2["total_scans"], 2)
        self.assertEqual(payload2["file_churn"]["dist/app.js"], 2)


if __name__ == "__main__":
    unittest.main()
