
from __future__ import annotations

from .canon import PORTABLE_INDEX_NAME, REQUIRED_VALIDATOR_ARTIFACTS
from .models import Finding


def evaluate(case: dict) -> list[Finding]:
    findings: list[Finding] = []
    required = set(REQUIRED_VALIDATOR_ARTIFACTS)
    artifacts = case.get('artifact_names', [])
    present = set(artifacts)
    missing = sorted(required - present)
    extra_bad = [name for name in artifacts if name.endswith('.json') and ' ' in name]
    if PORTABLE_INDEX_NAME not in case.get('index_names_seen', [PORTABLE_INDEX_NAME]):
        findings.append(Finding(
            rule_id='artifact_naming.portable_index',
            severity='error',
            family='artifact_naming',
            message='Portable index name is missing from the case metadata.',
            entity=case['case_id'],
            location='index_names_seen',
            expected=PORTABLE_INDEX_NAME,
            observed=case.get('index_names_seen', []),
            remediation='Expose registry_index.json as the portable canonical index.',
        ))
    for name in missing:
        findings.append(Finding(
            rule_id='artifact_naming.required_validator_artifact',
            severity='error',
            family='artifact_naming',
            message='Required validator artifact name is absent.',
            entity=case['case_id'],
            location='artifact_names',
            expected=name,
            observed=artifacts,
            remediation='Add the required validator artifact to verification output generation.',
        ))
    for name in extra_bad:
        findings.append(Finding(
            rule_id='artifact_naming.whitespace',
            severity='warning',
            family='artifact_naming',
            message='Artifact name contains whitespace and is not canonical.',
            entity=case['case_id'],
            location='artifact_names',
            expected='snake_case file name',
            observed=name,
            remediation='Rename the artifact using canonical snake_case without spaces.',
        ))
    if not missing and not extra_bad:
        findings.append(Finding(
            rule_id='artifact_naming.clean',
            severity='info',
            family='artifact_naming',
            message='Validator artifact naming is canonical.',
            entity=case['case_id'],
            location='artifact_names',
            expected=sorted(required),
            observed=sorted(artifacts),
            remediation='None.',
        ))
    return findings
