from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..engine.client_index import ClientIndexBuilder
from ..engine.context import Finding, ScanOutput
from ..history.snapshot_store import SnapshotStore
from ..history.trend_analyzer import TrendAnalyzer
from ..react_graph.boundary_analyzer import GraphBoundaryAnalyzer
from ..react_graph.graph_builder import ReactGraphBuilder
from ..react_graph.models import GraphSummary


@dataclass(slots=True)
class AdvancedAnalysisResult:
    scan_output: ScanOutput
    graph_summary: GraphSummary
    history_snapshot: dict
    trend_summary: dict


class AdvancedAnalysisPipeline:
    def __init__(self, repo_root: str | Path, report_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.report_root = Path(report_root).resolve()
        self.graph_builder = ReactGraphBuilder()
        self.analyzer = GraphBoundaryAnalyzer()
        self.snapshot_store = SnapshotStore(self.report_root)
        self.trend_analyzer = TrendAnalyzer()

    def execute(self, output: ScanOutput) -> AdvancedAnalysisResult:
        client_index = ClientIndexBuilder(str(self.repo_root)).build(output.inventory)
        graph = self.graph_builder.build(output, client_index)
        graph_findings, graph_summary = self.analyzer.analyze(graph)
        output.findings = self._dedupe([*output.findings, *graph_findings])
        output.stats.findings_total = len(output.findings)
        output.stats.findings_active = sum(1 for item in output.findings if not item.ignored)
        output.stats.baseline_ignored = sum(1 for item in output.findings if item.ignored)
        output.meta['react_graph'] = graph_summary.to_dict()
        output.meta['react_graph']['entrypoints'] = list(graph.entrypoints)
        history_snapshot = self.snapshot_store.build_snapshot(output, graph_summary)
        previous_snapshot = self.snapshot_store.read_latest_snapshot()
        trend_summary = self.trend_analyzer.compare(previous_snapshot, history_snapshot)
        history_snapshot['trend'] = trend_summary
        return AdvancedAnalysisResult(
            scan_output=output,
            graph_summary=graph_summary,
            history_snapshot=history_snapshot,
            trend_summary=trend_summary,
        )

    @staticmethod
    def _dedupe(findings: list[Finding]) -> list[Finding]:
        seen: set[str] = set()
        unique: list[Finding] = []
        for finding in findings:
            finding.ensure_fingerprint()
            if finding.fingerprint in seen:
                continue
            seen.add(finding.fingerprint)
            unique.append(finding)
        return sorted(unique, key=lambda item: (item.relpath, item.line_number, item.rule_id, item.fingerprint))
