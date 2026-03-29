from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.shared.contracts import CleanupPlan, PredictionResult, RepairPlan, ScanResult, ScanStats, SentinelReport
from tools.hos.git_sentinel_modular.shared.foundation import SentinelPaths
from tools.hos.git_sentinel_modular.shared.runtime_checks import ProviderRegistry, run_startup_doctor


class RepoScanner:
    def scan_repository(self, repo_root: str) -> ScanResult:
        return ScanResult(repo_root=repo_root, scan_id="scan-smoke", stats=ScanStats(scanned_files=2)).validate()


class SecurityScanner:
    def scan_security(self, repo_root: str):
        return []


class LearningStore:
    def load_snapshot(self, repo_root: str):
        return {"history": []}

    def save_snapshot(self, repo_root: str, payload):
        return None


class PredictionEngine:
    def predict(self, scan_result: ScanResult, learning_snapshot):
        return [
            PredictionResult(
                candidate_path="tools/hos/git_sentinel/dashboard_app.py",
                risk_score=0.35,
                confidence=0.60,
                rationale=["high churn surface"],
            ).validate()
        ]


class ReportGenerator:
    def build_report(self, scan_result, predictions, repair_plan, cleanup_plan):
        return SentinelReport(
            report_id="smoke-report",
            repo_root=scan_result.repo_root,
            scan_result=scan_result,
            predictions=predictions,
            repair_plan=repair_plan,
            cleanup_plan=cleanup_plan,
        ).validate()


class WiringSmokeTestCase(unittest.TestCase):
    def test_phase1_wiring_smoke(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)

        repo_root = Path(tmp.name) / "repo"
        scaffold_root = repo_root / "tools" / "hos" / "git_sentinel_modular"
        (repo_root / ".git").mkdir(parents=True, exist_ok=True)
        (repo_root / "tools" / "hos").mkdir(parents=True, exist_ok=True)
        (scaffold_root / "docs" / "phases" / "phase_01").mkdir(parents=True, exist_ok=True)

        paths = SentinelPaths.from_scaffold_root(repo_root, scaffold_root)
        registry = ProviderRegistry()
        registry.register("repository_scanner", RepoScanner())
        registry.register("security_scanner", SecurityScanner())
        registry.register("learning_store", LearningStore())
        registry.register("prediction_engine", PredictionEngine())
        registry.register("report_generator", ReportGenerator())

        result = run_startup_doctor(paths, registry)
        self.assertTrue(result.ok, result.findings)
        self.assertEqual(result.checked_contract_version, "1.0.0")


if __name__ == "__main__":
    unittest.main()
