from __future__ import annotations

from collections import Counter

from ..engine.context import ScanOutput
from ..react_graph.models import GraphSummary
from ..risk.risk_scoring_engine import RiskSummary


class DiagnosticsFormatter:
    def recommendations(self, output: ScanOutput, risk_summary: RiskSummary, graph_summary: GraphSummary, trend_summary: dict) -> list[str]:
        counts = Counter(finding.rule_id for finding in output.findings if not finding.ignored)
        recommendations: list[str] = []
        if counts.get('browser_api_non_client') or counts.get('graph_server_client_chain'):
            recommendations.append('Audit browser APIs and client boundaries together. Tighten the island contract where server entrypoints reach client-only surfaces.')
        if counts.get('storage_hydration') or counts.get('graph_storage_reachability'):
            recommendations.append('Review storage-backed render state and move persistence reads behind post-mount hydration or explicit client entrypoints.')
        if counts.get('nondeterministic_render') or counts.get('graph_nondeterministic_reachability'):
            recommendations.append('Replace render-time Date, random, and UUID generation with deterministic server data or client effects.')
        if counts.get('dynamic_ssr_false'):
            recommendations.append('Limit dynamic(..., { ssr: false }) to well-documented tooling-only boundaries.')
        if counts.get('suppress_hydration_warning'):
            recommendations.append('Reduce suppressHydrationWarning usage to route-local exceptions with written root cause notes.')
        if counts.get('graph_client_island_pressure'):
            recommendations.append('Split high-fan-in client islands into smaller surfaces so one boundary does not hydrate half the barrio.')
        if graph_summary.path_counts.get('dom_mutation', 0):
            recommendations.append('Move DOM mutation helpers behind effects or tooling-only wrappers before they leak into normal entrypoints.')
        if trend_summary.get('has_previous') and trend_summary.get('new_findings', 0) > trend_summary.get('resolved_findings', 0):
            recommendations.append('The historical snapshot trend is worsening. Stabilize the newest graph regressions before expanding enforcement.')
        if risk_summary.risk_level in {'high', 'critical'}:
            recommendations.append('Do not enable strict enforcement yet. Clean exclusions and highest-risk files before turning the scanner into hard policy.')
        if not recommendations:
            recommendations.append('No critical graph regressions detected. Maintain exclusions, keep snapshots flowing, and keep the guardrails boring in the best way.')
        return recommendations

    def top_findings_lines(self, output: ScanOutput, limit: int = 15) -> list[str]:
        active = [finding for finding in output.findings if not finding.ignored][:limit]
        return [
            f"- [{finding.severity}] {finding.rule_id} :: {finding.relpath}:{finding.line_number} -> {finding.message}"
            for finding in active
        ]
