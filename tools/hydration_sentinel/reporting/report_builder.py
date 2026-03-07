from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..analysis.advanced_pipeline import AdvancedAnalysisPipeline
from ..engine.runner import ScanRunner
from ..history.snapshot_store import SnapshotStore
from ..risk.regression_detector import RegressionDetector
from ..risk.risk_scoring_engine import RiskScoringEngine
from ..rules_engine.executor import RulesExecutor
from .diagnostics_formatter import DiagnosticsFormatter
from .graph_report import GraphReport
from .json_report import JsonReport
from .markdown_report import MarkdownReport
from .metrics_report import MetricsReport


@dataclass(slots=True)
class BuiltReport:
    findings_payload: dict
    summary_payload: dict
    recommendations_payload: dict
    metrics_payload: dict
    markdown_text: str
    graph_payload: dict
    history_snapshot_payload: dict
    trend_payload: dict


class ReportBuilder:
    def __init__(
        self,
        repo_root: str | Path,
        *,
        config_path: str | Path | None = None,
        baseline_path: str | Path | None = None,
        report_root: str | Path | None = None,
        diff_only: bool = False,
        diff_base_ref: str | None = None,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.config_path = config_path
        self.baseline_path = baseline_path
        self.report_root = Path(report_root).resolve() if report_root else self.repo_root / '_reports' / 'hydration_sentinel'
        self.diff_only = diff_only
        self.diff_base_ref = diff_base_ref

    def build(self) -> BuiltReport:
        runner = ScanRunner(
            self.repo_root,
            config_path=self.config_path,
            baseline_path=self.baseline_path,
            force_diff_enabled=True if self.diff_only else None,
            force_diff_base_ref=self.diff_base_ref,
        )
        output = runner.run()
        output = RulesExecutor(self.repo_root, baseline_path=self.baseline_path).execute(output).scan_output
        advanced = AdvancedAnalysisPipeline(self.repo_root, self.report_root).execute(output)
        output = advanced.scan_output
        risk_summary = RiskScoringEngine().compute(output)
        regression_summary = RegressionDetector().compare_with_previous(output, self.report_root)
        formatter = DiagnosticsFormatter()
        recommendations = formatter.recommendations(output, risk_summary, advanced.graph_summary, advanced.trend_summary)
        top_findings = formatter.top_findings_lines(output)
        json_report = JsonReport()
        metrics_payload = MetricsReport().build(output, risk_summary, regression_summary, advanced.graph_summary, advanced.trend_summary)
        findings_payload = json_report.findings_payload(output, risk_summary, regression_summary, advanced.graph_summary, advanced.history_snapshot, advanced.trend_summary)
        summary_payload = json_report.summary_payload(output, risk_summary, regression_summary, recommendations, advanced.graph_summary, advanced.history_snapshot, advanced.trend_summary)
        markdown_text = MarkdownReport().render(output, risk_summary, regression_summary, recommendations, top_findings, advanced.graph_summary, advanced.trend_summary)
        recommendations_payload = {'recommendations': recommendations}
        return BuiltReport(
            findings_payload=findings_payload,
            summary_payload=summary_payload,
            recommendations_payload=recommendations_payload,
            metrics_payload=metrics_payload,
            markdown_text=markdown_text,
            graph_payload=GraphReport().payload(advanced.graph_summary, advanced.trend_summary),
            history_snapshot_payload=advanced.history_snapshot,
            trend_payload=advanced.trend_summary,
        )

    def write_latest(self, built: BuiltReport) -> dict[str, Path]:
        latest = self.report_root / 'latest'
        latest.mkdir(parents=True, exist_ok=True)
        paths = {
            'findings': latest / 'findings.json',
            'summary': latest / 'summary.json',
            'recommendations': latest / 'recommendations.json',
            'metrics': latest / 'metrics.json',
            'report': latest / 'report.md',
            'graph_summary': latest / 'graph_summary.json',
            'history_snapshot': latest / 'history_snapshot.json',
            'trend_summary': latest / 'trend_summary.json',
        }
        paths['findings'].write_text(json.dumps(built.findings_payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        paths['summary'].write_text(json.dumps(built.summary_payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        paths['recommendations'].write_text(json.dumps(built.recommendations_payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        paths['metrics'].write_text(json.dumps(built.metrics_payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        paths['graph_summary'].write_text(json.dumps(built.graph_payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        paths['trend_summary'].write_text(json.dumps(built.trend_payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        paths['report'].write_text(built.markdown_text, encoding='utf-8')
        snapshot_paths = SnapshotStore(self.report_root).write(built.history_snapshot_payload)
        paths['history_snapshot'] = snapshot_paths['latest']
        return paths
