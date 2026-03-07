from __future__ import annotations

from collections import Counter

from ..engine.context import ScanOutput
from ..react_graph.models import GraphSummary
from ..risk.risk_scoring_engine import RiskSummary


class MetricsReport:
    def build(self, output: ScanOutput, risk_summary: RiskSummary, regression_summary: dict, graph_summary: GraphSummary, trend_summary: dict) -> dict:
        active = [finding for finding in output.findings if not finding.ignored]
        return {
            'files_scanned': output.stats.files_scanned,
            'active_findings': len(active),
            'ignored_findings': output.stats.baseline_ignored,
            'rule_counts': dict(Counter(finding.rule_id for finding in active)),
            'severity_counts': dict(Counter(finding.severity for finding in active)),
            'risk': risk_summary.to_dict(),
            'regression': regression_summary,
            'graph': graph_summary.to_dict(),
            'trend': trend_summary,
        }
