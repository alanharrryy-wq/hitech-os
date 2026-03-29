from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.shared.foundation import SentinelPaths
from tools.hos.git_sentinel_modular.shared.interfaces import (
    CleanupEnginePort,
    LearningStorePort,
    PredictionEnginePort,
    RepairEnginePort,
    ReportGeneratorPort,
    RepositoryScannerPort,
    SecurityScannerPort,
)
from tools.hos.git_sentinel_modular.shared.runtime_checks import ProviderRegistry, run_startup_doctor
from tools.hos.git_sentinel_modular.shared.contracts import (
    CleanupPlan,
    PredictionResult,
    RepairPlan,
    ScanResult,
    ScanStats,
    SecurityFinding,
    SentinelReport,
)


class DummyRepositoryScanner:
    def scan_repository(self, repo_root: str) -> ScanResult:
        return ScanResult(repo_root=repo_root, scan_id="scan-001", stats=ScanStats(scanned_files=1)).validate()


class DummySecurityScanner:
    def scan_security(self, repo_root: str) -> list[SecurityFinding]:
        return []


class DummyLearningStore:
    def load_snapshot(self, repo_root: str):
        return {}

    def save_snapshot(self, repo_root: str, payload):
        return None


class DummyPredictionEngine:
    def predict(self, scan_result: ScanResult, learning_snapshot):
        return []


class DummyRepairEngine:
    def plan_repairs(self, scan_result: ScanResult, predictions: list[PredictionResult]) -> RepairPlan:
        return RepairPlan(dry_run=True).validate()


class DummyCleanupEngine:
    def plan_cleanup(self, scan_result: ScanResult) -> CleanupPlan:
        return CleanupPlan(dry_run=True).validate()


class DummyReportGenerator:
    def build_report(
        self,
        scan_result: ScanResult,
        predictions: list[PredictionResult],
        repair_plan: RepairPlan,
        cleanup_plan: CleanupPlan,
    ) -> SentinelReport:
        return SentinelReport(
            report_id="report-001",
            repo_root=scan_result.repo_root,
            scan_result=scan_result,
            predictions=predictions,
            repair_plan=repair_plan,
            cleanup_plan=cleanup_plan,
        ).validate()


class RuntimeChecksTestCase(unittest.TestCase):
    def _make_paths(self) -> SentinelPaths:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo_root = Path(tmp.name) / "repo"
        scaffold_root = repo_root / "tools" / "hos" / "git_sentinel_modular"
        (repo_root / ".git").mkdir(parents=True, exist_ok=True)
        (repo_root / "tools" / "hos").mkdir(parents=True, exist_ok=True)
        (scaffold_root / "docs" / "phases" / "phase_01").mkdir(parents=True, exist_ok=True)
        return SentinelPaths.from_scaffold_root(repo_root, scaffold_root)

    def test_doctor_reports_missing_required_providers(self):
        paths = self._make_paths()
        registry = ProviderRegistry()
        result = run_startup_doctor(paths, registry)
        self.assertFalse(result.ok)
        self.assertTrue(any(f.code == "REQUIRED_PROVIDER_MISSING" for f in result.findings))

    def test_doctor_passes_when_required_providers_exist(self):
        paths = self._make_paths()
        registry = ProviderRegistry()
        registry.register("repository_scanner", DummyRepositoryScanner())
        registry.register("security_scanner", DummySecurityScanner())
        registry.register("learning_store", DummyLearningStore())
        registry.register("prediction_engine", DummyPredictionEngine())
        registry.register("report_generator", DummyReportGenerator())
        result = run_startup_doctor(paths, registry)
        self.assertTrue(result.ok, result.findings)

    def test_optional_providers_can_be_missing(self):
        paths = self._make_paths()
        registry = ProviderRegistry()
        registry.register("repository_scanner", DummyRepositoryScanner())
        registry.register("security_scanner", DummySecurityScanner())
        registry.register("learning_store", DummyLearningStore())
        registry.register("prediction_engine", DummyPredictionEngine())
        registry.register("report_generator", DummyReportGenerator())
        result = run_startup_doctor(paths, registry)
        warn_codes = {f.code for f in result.findings if f.level == "WARN"}
        self.assertIn("OPTIONAL_PROVIDER_MISSING", warn_codes)


if __name__ == "__main__":
    unittest.main()
