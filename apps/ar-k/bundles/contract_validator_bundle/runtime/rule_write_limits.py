
from __future__ import annotations

from .models import Finding

FORBIDDEN_FAMILIES = {
    'module_registry', 'boundary_registry', 'registry_index', 'switch_decision_registry',
    'switch_decision_trace', 'annotations', 'annotation_index'
}


def evaluate(case: dict) -> list[Finding]:
    findings: list[Finding] = []
    for write in case.get('writes', []):
        if write['family'] in FORBIDDEN_FAMILIES:
            findings.append(Finding(
                rule_id='write_limits.validator_scope',
                severity='critical',
                family='write_limits',
                message='Validator write escaped its narrow artifact scope.',
                entity=case['case_id'],
                location='writes.family',
                expected='validator-owned artifacts only',
                observed=write['family'],
                remediation='Keep validator writes limited to validation_report, gate_decisions, and validator_summary.',
            ))
    if not [w for w in case.get('writes', []) if w['family'] in FORBIDDEN_FAMILIES]:
        findings.append(Finding(
            rule_id='write_limits.clean',
            severity='info',
            family='write_limits',
            message='Validator writes stay inside its owned scope.',
            entity=case['case_id'],
            location='writes',
            expected='validator-owned artifacts only',
            observed=case.get('writes', []),
            remediation='None.',
        ))
    return findings
