
from __future__ import annotations

from collections import Counter

from .models import Finding
from .severities import GateDecision, bundle_status_from_findings, max_severity


def summarize(findings: list[Finding]) -> dict:
    counts = Counter(item.severity for item in findings)
    status = bundle_status_from_findings([item.severity for item in findings])
    return {
        'overall_status': status,
        'counts_by_severity': {
            'info': counts.get('info', 0),
            'warning': counts.get('warning', 0),
            'error': counts.get('error', 0),
            'critical': counts.get('critical', 0),
        },
        'finding_count': len(findings),
    }


def build_gate_decisions(findings: list[Finding]) -> list[dict]:
    by_family: dict[str, list[Finding]] = {}
    for finding in findings:
        by_family.setdefault(finding.family, []).append(finding)
    decisions: list[dict] = []
    for family in sorted(by_family):
        severities = [item.severity for item in by_family[family]]
        max_level = max_severity(severities)
        status = bundle_status_from_findings(severities)
        decisions.append(GateDecision(
            gate_id=f'gate.{family}',
            status=status,
            reason=f'{family} evaluated with max severity {max_level}',
            max_severity=max_level,
        ).__dict__)
    return decisions
