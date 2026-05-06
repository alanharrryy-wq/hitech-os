
from __future__ import annotations

from .canon import SHARED_STAGE_ORDER
from .models import Finding


def evaluate(case: dict) -> list[Finding]:
    findings: list[Finding] = []
    observed = case.get('stage_sequence', [])
    if observed != SHARED_STAGE_ORDER:
        findings.append(Finding(
            rule_id='stage_order.canonical_sequence',
            severity='error',
            family='stage_order',
            message='Stage order diverges from the shared canon.',
            entity=case['case_id'],
            location='stage_sequence',
            expected=SHARED_STAGE_ORDER,
            observed=observed,
            remediation='Reorder execution to the shared five-stage sequence.',
        ))
    else:
        findings.append(Finding(
            rule_id='stage_order.canonical_sequence',
            severity='info',
            family='stage_order',
            message='Stage order matches the shared canon.',
            entity=case['case_id'],
            location='stage_sequence',
            expected=SHARED_STAGE_ORDER,
            observed=observed,
            remediation='None.',
        ))
    return findings
