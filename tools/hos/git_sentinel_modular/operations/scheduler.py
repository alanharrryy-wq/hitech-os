from __future__ import annotations

from dataclasses import dataclass

from ..analysis.prediction import RuleBasedPredictionEngine
from ..learning.engine import SQLiteLearningStore
from ..operations.ci_gate import CIGateEvaluator, CIGateResult
from ..remediation.cleanup import CleanupPlanner
from ..remediation.repair import RepairPlanner
from ..reporting.generator import SentinelReportGenerator
from ..scanning.artifacts import ArtifactClassifier
from ..scanning.repository import RepositoryScanner
from ..security.scanner import SecurityScanner
from ..shared.contracts import SentinelReport


@dataclass(slots=True)
class SchedulerTick:
    repo_root: str
    report: SentinelReport
    ci_gate: CIGateResult


class SentinelScheduler:
    def __init__(
        self,
        learning_store: SQLiteLearningStore,
        repository_scanner: RepositoryScanner | None = None,
        artifact_classifier: ArtifactClassifier | None = None,
        security_scanner: SecurityScanner | None = None,
        prediction_engine: RuleBasedPredictionEngine | None = None,
        repair_planner: RepairPlanner | None = None,
        cleanup_planner: CleanupPlanner | None = None,
        report_generator: SentinelReportGenerator | None = None,
        ci_gate_evaluator: CIGateEvaluator | None = None,
    ):
        self.learning_store = learning_store
        self.repository_scanner = repository_scanner or RepositoryScanner()
        self.artifact_classifier = artifact_classifier or ArtifactClassifier()
        self.security_scanner = security_scanner or SecurityScanner()
        self.prediction_engine = prediction_engine or RuleBasedPredictionEngine()
        self.repair_planner = repair_planner or RepairPlanner()
        self.cleanup_planner = cleanup_planner or CleanupPlanner()
        self.report_generator = report_generator or SentinelReportGenerator()
        self.ci_gate_evaluator = ci_gate_evaluator or CIGateEvaluator()

    def run_once(self, repo_root: str) -> SchedulerTick:
        scan_result = self.repository_scanner.scan_repository(repo_root)
        snapshot = self.repository_scanner.scan_paths(self.repository_scanner.build_request(repo_root))

        artifact_findings = self.artifact_classifier.classify_many(snapshot.discovered_files)
        security_findings = self.security_scanner.scan_security(repo_root)

        scan_result.artifact_findings = artifact_findings
        scan_result.security_findings = security_findings
        scan_result.stats.artifact_findings = len(artifact_findings)
        scan_result.stats.security_findings = len(security_findings)
        scan_result.validate()

        learning_snapshot = self.learning_store.update_from_scan(scan_result)
        predictions = self.prediction_engine.predict(scan_result, learning_snapshot)
        repair_plan = self.repair_planner.plan_repairs(scan_result, predictions)
        cleanup_plan = self.cleanup_planner.plan_cleanup(scan_result)
        report = self.report_generator.build_report(scan_result, predictions, repair_plan, cleanup_plan)
        gate = self.ci_gate_evaluator.evaluate(report)

        return SchedulerTick(
            repo_root=repo_root,
            report=report,
            ci_gate=gate,
        )
