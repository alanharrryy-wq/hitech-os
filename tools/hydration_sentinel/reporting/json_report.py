from __future__ import annotations

from ..engine.context import ScanOutput
from ..react_graph.models import GraphSummary
from ..risk.risk_scoring_engine import RiskSummary


class JsonReport:
    def findings_payload(
        self,
        output: ScanOutput,
        risk_summary: RiskSummary,
        regression_summary: dict,
        graph_summary: GraphSummary,
        history_snapshot: dict,
        trend_summary: dict,
    ) -> dict:
        payload = output.to_findings_payload()
        payload['summary']['risk'] = risk_summary.to_dict()
        payload['summary']['regression'] = regression_summary
        payload['summary']['graph'] = graph_summary.to_dict()
        payload['summary']['trend'] = trend_summary
        payload['summary']['history_snapshot'] = {
            'created_at': history_snapshot.get('created_at'),
            'active_fingerprint_count': len(history_snapshot.get('active_fingerprints', [])),
        }
        return payload

    def summary_payload(
        self,
        output: ScanOutput,
        risk_summary: RiskSummary,
        regression_summary: dict,
        recommendations: list[str],
        graph_summary: GraphSummary,
        history_snapshot: dict,
        trend_summary: dict,
    ) -> dict:
        summary = output.to_summary()
        summary['risk'] = risk_summary.to_dict()
        summary['regression'] = regression_summary
        summary['recommendations'] = recommendations
        summary['graph'] = graph_summary.to_dict()
        summary['history_snapshot'] = {
            'created_at': history_snapshot.get('created_at'),
            'active_fingerprint_count': len(history_snapshot.get('active_fingerprints', [])),
        }
        summary['trend'] = trend_summary
        return summary
