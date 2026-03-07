from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.context import ScanOutput


SEVERITY_WEIGHTS = {'info': 1, 'low': 2, 'medium': 5, 'high': 9, 'critical': 15}
RULE_MULTIPLIERS = {
    'browser_api_non_client': 1.2,
    'dynamic_ssr_false': 1.4,
    'suppress_hydration_warning': 1.3,
    'server_client_import': 1.1,
    'storage_hydration': 1.6,
    'nondeterministic_render': 1.8,
    'dom_mutation_signature': 1.5,
    'graph_server_client_chain': 1.45,
    'graph_storage_reachability': 1.75,
    'graph_nondeterministic_reachability': 1.85,
    'graph_dom_mutation_reachability': 1.6,
    'graph_client_island_pressure': 1.25,
}


@dataclass(slots=True)
class PathRisk:
    relpath: str
    score: float
    finding_count: int
    highest_severity: str


@dataclass(slots=True)
class RiskSummary:
    total_score: float
    risk_level: str
    top_paths: list[PathRisk] = field(default_factory=list)
    rule_scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'total_score': round(self.total_score, 2),
            'risk_level': self.risk_level,
            'top_paths': [
                {
                    'relpath': item.relpath,
                    'score': round(item.score, 2),
                    'finding_count': item.finding_count,
                    'highest_severity': item.highest_severity,
                }
                for item in self.top_paths
            ],
            'rule_scores': {key: round(value, 2) for key, value in self.rule_scores.items()},
        }


class RiskScoringEngine:
    def compute(self, output: ScanOutput) -> RiskSummary:
        path_scores: dict[str, float] = {}
        path_counts: dict[str, int] = {}
        path_highest: dict[str, str] = {}
        rule_scores: dict[str, float] = {}

        for finding in output.findings:
            if finding.ignored:
                continue
            base = SEVERITY_WEIGHTS.get(finding.severity, 1)
            multiplier = RULE_MULTIPLIERS.get(finding.rule_id, 1.0)
            path_multiplier = 1.2 if '/app/' in finding.relpath else 0.85 if '/app/dev/' in finding.relpath else 1.0
            score = base * multiplier * path_multiplier
            path_scores[finding.relpath] = path_scores.get(finding.relpath, 0.0) + score
            path_counts[finding.relpath] = path_counts.get(finding.relpath, 0) + 1
            path_highest[finding.relpath] = self._max_severity(path_highest.get(finding.relpath), finding.severity)
            rule_scores[finding.rule_id] = rule_scores.get(finding.rule_id, 0.0) + score

        total = sum(path_scores.values())
        top_paths = [
            PathRisk(relpath=relpath, score=score, finding_count=path_counts[relpath], highest_severity=path_highest[relpath])
            for relpath, score in sorted(path_scores.items(), key=lambda item: (-item[1], item[0]))[:10]
        ]
        return RiskSummary(
            total_score=total,
            risk_level=self._classify(total),
            top_paths=top_paths,
            rule_scores=dict(sorted(rule_scores.items(), key=lambda item: (-item[1], item[0]))),
        )

    @staticmethod
    def _classify(total: float) -> str:
        if total >= 120:
            return 'critical'
        if total >= 60:
            return 'high'
        if total >= 25:
            return 'medium'
        if total > 0:
            return 'low'
        return 'clean'

    @staticmethod
    def _max_severity(existing: str | None, incoming: str) -> str:
        rank = {'info': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        if existing is None:
            return incoming
        return incoming if rank.get(incoming, 0) > rank.get(existing, 0) else existing
