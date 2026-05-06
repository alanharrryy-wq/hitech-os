
from __future__ import annotations

from pathlib import PurePosixPath

from .canon import EXCLUDED_PATH_PARTS
from .models import Finding


def evaluate(case: dict) -> list[Finding]:
    findings: list[Finding] = []
    for path in case.get('paths_examined', []):
        parts = set(PurePosixPath(path.replace('\\', '/')).parts)
        if any(excluded in parts for excluded in EXCLUDED_PATH_PARTS):
            findings.append(Finding(
                rule_id='exclusions.generated_path_filtered',
                severity='info',
                family='exclusions',
                message='Generated or excluded path is recognised as out-of-scope.',
                entity=case['case_id'],
                location='paths_examined',
                expected='excluded path stays outside validator authority',
                observed=path,
                remediation='None.',
            ))
    violations = case.get('excluded_paths_written', [])
    for path in violations:
        findings.append(Finding(
            rule_id='exclusions.write_violation',
            severity='critical',
            family='exclusions',
            message='Validator attempted to write into an excluded or generated runtime path.',
            entity=case['case_id'],
            location='excluded_paths_written',
            expected='no writes under excluded paths such as reports_real/',
            observed=path,
            remediation='Confine writes to validator-owned verification output directories only.',
        ))
    return findings
