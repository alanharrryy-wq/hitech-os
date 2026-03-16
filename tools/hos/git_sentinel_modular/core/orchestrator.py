from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..analysis.prediction import RuleBasedPredictionEngine
from ..learning.engine import SQLiteLearningStore
from ..operations.ci_gate import CIGateEvaluator
from ..operations.scheduler import SentinelScheduler
from ..remediation.cleanup import CleanupPlanner
from ..remediation.repair import RepairPlanner
from ..reporting.alerting import AlertDispatcher
from ..reporting.generator import SentinelReportGenerator
from ..scanning.artifacts import ArtifactClassifier
from ..scanning.repository import RepositoryScanner
from ..security.scanner import SecurityScanner
from ..shared.contracts import SentinelReport


@dataclass(slots=True)
class OrchestratorConfig:
    repo_root: str
    learning_db_path: str
    report_json_path: str = ""
    report_md_path: str = ""
    alert_output_path: str = ""
    run_alerting: bool = True

    def validate(self) -> "OrchestratorConfig":
        self.repo_root = str(Path(self.repo_root).resolve())
        self.learning_db_path = str(Path(self.learning_db_path).resolve())
        if self.report_json_path:
            self.report_json_path = str(Path(self.report_json_path).resolve())
        if self.report_md_path:
            self.report_md_path = str(Path(self.report_md_path).resolve())
        if self.alert_output_path:
            self.alert_output_path = str(Path(self.alert_output_path).resolve())
        return self


class SentinelOrchestrator:
    def __init__(
        self,
        config: OrchestratorConfig,
        scheduler: SentinelScheduler | None = None,
        report_generator: SentinelReportGenerator | None = None,
        alert_dispatcher: AlertDispatcher | None = None,
    ):
        self.config = config.validate()
        self.report_generator = report_generator or SentinelReportGenerator()
        self.alert_dispatcher = alert_dispatcher or AlertDispatcher()

        if scheduler is None:
            learning_store = SQLiteLearningStore(self.config.learning_db_path)
            scheduler = SentinelScheduler(
                learning_store=learning_store,
                repository_scanner=RepositoryScanner(),
                artifact_classifier=ArtifactClassifier(),
                security_scanner=SecurityScanner(),
                prediction_engine=RuleBasedPredictionEngine(),
                repair_planner=RepairPlanner(),
                cleanup_planner=CleanupPlanner(),
                report_generator=self.report_generator,
                ci_gate_evaluator=CIGateEvaluator(),
            )
        self.scheduler = scheduler

    def run_once(self) -> dict[str, Any]:
        tick = self.scheduler.run_once(self.config.repo_root)
        report = tick.report.validate()

        if self.config.report_json_path and self.config.report_md_path:
            self.report_generator.write_bundle(report, self.config.report_json_path, self.config.report_md_path)

        alert_path = ""
        if self.config.run_alerting and self.config.alert_output_path:
            alert_path = str(self.alert_dispatcher.dispatch_to_file(report, self.config.alert_output_path))

        return {
            "repo_root": self.config.repo_root,
            "report": report.to_dict(),
            "ci_gate": {
                "ok": tick.ci_gate.ok,
                "status": tick.ci_gate.status,
                "reasons": list(tick.ci_gate.reasons),
            },
            "alert_output_path": alert_path,
        }
