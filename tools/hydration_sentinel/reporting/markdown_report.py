from __future__ import annotations

from ..engine.context import ScanOutput
from ..react_graph.models import GraphSummary
from ..risk.risk_scoring_engine import RiskSummary


class MarkdownReport:
    def render(
        self,
        output: ScanOutput,
        risk_summary: RiskSummary,
        regression_summary: dict,
        recommendations: list[str],
        top_findings: list[str],
        graph_summary: GraphSummary,
        trend_summary: dict,
    ) -> str:
        lines = [
            '# Hydration Sentinel PRO Report',
            '',
            f'- Repo root: `{output.repo_root}`',
            f'- Files scanned: **{output.stats.files_scanned}**',
            f'- Total findings: **{output.stats.findings_total}**',
            f'- Baseline ignored: **{output.stats.baseline_ignored}**',
            f'- Risk level: **{risk_summary.risk_level}**',
            f'- Risk score: **{round(risk_summary.total_score, 2)}**',
            f'- React graph nodes: **{graph_summary.node_count}**',
            f'- React graph edges: **{graph_summary.edge_count}**',
            '',
            '## Findings by category',
            '',
        ]
        for key, value in output.findings_by_rule().items():
            lines.append(f'- `{key}`: {value}')
        lines.extend(['', '## Findings by severity', ''])
        for key, value in output.findings_by_severity().items():
            lines.append(f'- `{key}`: {value}')
        lines.extend([
            '',
            '## Regression summary',
            '',
            f"- Previous run available: **{regression_summary['has_previous']}**",
            f"- New findings: **{regression_summary['new_findings']}**",
            f"- Resolved findings: **{regression_summary['resolved_findings']}**",
            f"- Unchanged findings: **{regression_summary['unchanged_findings']}**",
            '',
            '## Graph trend summary',
            '',
            f"- Previous snapshot available: **{trend_summary['has_previous']}**",
            f"- Graph new findings: **{trend_summary['new_findings']}**",
            f"- Graph resolved findings: **{trend_summary['resolved_findings']}**",
            f"- Delta total findings: **{trend_summary['delta_total_findings']}**",
            '',
            '## Top risky paths',
            '',
        ])
        for item in risk_summary.top_paths:
            lines.append(f"- `{item.relpath}` -> score {round(item.score, 2)} ({item.finding_count} findings, highest `{item.highest_severity}`)")
        lines.extend(['', '## React graph summary', ''])
        lines.append(f"- Entry points: **{graph_summary.entrypoint_count}**")
        lines.append(f"- Client nodes: **{graph_summary.client_node_count}**")
        lines.append(f"- Serverish nodes: **{graph_summary.serverish_node_count}**")
        lines.append(f"- Shared nodes: **{graph_summary.shared_node_count}**")
        lines.append(f"- Tooling nodes: **{graph_summary.tooling_node_count}**")
        lines.append('')
        lines.append('### Graph path counts')
        lines.append('')
        for key, value in graph_summary.path_counts.items():
            lines.append(f'- `{key}`: {value}')
        lines.append('')
        lines.append('### Graph notes')
        lines.append('')
        for note in graph_summary.notes:
            lines.append(f'- {note}')
        lines.extend(['', '## Recommendations', ''])
        for item in recommendations:
            lines.append(f'- {item}')
        lines.extend(['', '## Sample findings', ''])
        lines.extend(top_findings or ['- None'])
        return '\n'.join(lines) + '\n'
