from __future__ import annotations

from ..react_graph.models import GraphSummary


class GraphReport:
    def payload(self, graph_summary: GraphSummary, trend_summary: dict) -> dict:
        payload = graph_summary.to_dict()
        payload['trend'] = trend_summary
        return payload
