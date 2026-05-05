
from __future__ import annotations

from .models import Finding


def evaluate(case: dict) -> list[Finding]:
    findings: list[Finding] = []
    for action in case.get('promotion_actions', []):
        findings.append(Finding(
            rule_id='promotion_policy.validator_non_authority',
            severity='error',
            family='promotion_policy',
            message='Validator is attempting to promote observed data or canonical state.',
            entity=case['case_id'],
            location='promotion_actions',
            expected='validator never promotes observed data',
            observed=action,
            remediation='Move promotion logic back to registry_builder and keep validator read-only over canonical state.',
        ))
    if not case.get('promotion_actions'):
        findings.append(Finding(
            rule_id='promotion_policy.clean',
            severity='info',
            family='promotion_policy',
            message='Validator does not perform promotion actions.',
            entity=case['case_id'],
            location='promotion_actions',
            expected=[],
            observed=[],
            remediation='None.',
        ))
    return findings
