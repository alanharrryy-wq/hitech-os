
from __future__ import annotations

from .models import Finding


def evaluate(case: dict) -> list[Finding]:
    findings: list[Finding] = []
    modules = set(case.get('module_ids', []))
    boundaries = set(case.get('boundary_ids', []))
    for ref in case.get('cross_refs', []):
        target_family = ref['target_family']
        target_id = ref['target_id']
        if target_family == 'module' and target_id not in modules:
            findings.append(Finding(
                rule_id='cross_reference.module',
                severity='error',
                family='cross_reference',
                message='Cross-reference points to a module that does not exist.',
                entity=case['case_id'],
                location='cross_refs',
                expected='known module id',
                observed=ref,
                remediation='Repair or remove the broken reference before handoff.',
            ))
        if target_family == 'boundary' and target_id not in boundaries:
            findings.append(Finding(
                rule_id='cross_reference.boundary',
                severity='error',
                family='cross_reference',
                message='Cross-reference points to a boundary that does not exist.',
                entity=case['case_id'],
                location='cross_refs',
                expected='known boundary id',
                observed=ref,
                remediation='Repair or remove the broken boundary reference before handoff.',
            ))
    if not [ref for ref in case.get('cross_refs', []) if (ref['target_family'] == 'module' and ref['target_id'] not in modules) or (ref['target_family'] == 'boundary' and ref['target_id'] not in boundaries)]:
        findings.append(Finding(
            rule_id='cross_reference.clean',
            severity='info',
            family='cross_reference',
            message='Cross-reference integrity is intact.',
            entity=case['case_id'],
            location='cross_refs',
            expected='known module and boundary ids',
            observed=case.get('cross_refs', []),
            remediation='None.',
        ))
    return findings
