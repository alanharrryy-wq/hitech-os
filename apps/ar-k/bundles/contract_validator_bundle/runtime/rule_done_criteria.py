
from __future__ import annotations

from .models import Finding

REQUIRED_DONE_FLAGS = {
    'stage_order_documented',
    'ownership_documented',
    'validator_artifacts_documented',
    'reports_real_excluded',
    'read_only_canonical_state',
    'gates_executable',
}


def evaluate(case: dict) -> list[Finding]:
    findings: list[Finding] = []
    flags = set(case.get('done_flags', []))
    missing = sorted(REQUIRED_DONE_FLAGS - flags)
    for flag in missing:
        findings.append(Finding(
            rule_id='done_criteria.missing_flag',
            severity='warning',
            family='done_criteria',
            message='Done criteria flag is missing from the handoff evidence.',
            entity=case['case_id'],
            location='done_flags',
            expected=flag,
            observed=sorted(flags),
            remediation='Add explicit evidence for the missing done criterion.',
        ))
    if not missing:
        findings.append(Finding(
            rule_id='done_criteria.complete',
            severity='info',
            family='done_criteria',
            message='Done criteria are explicit and complete.',
            entity=case['case_id'],
            location='done_flags',
            expected=sorted(REQUIRED_DONE_FLAGS),
            observed=sorted(flags),
            remediation='None.',
        ))
    return findings
