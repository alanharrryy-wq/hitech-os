
from __future__ import annotations

from .canon import SINGLE_WRITER
from .models import Finding


def evaluate(case: dict) -> list[Finding]:
    findings: list[Finding] = []
    for write in case.get('writes', []):
        family = write['family']
        writer = write['writer']
        expected_writer = SINGLE_WRITER.get(family)
        if expected_writer is None:
            findings.append(Finding(
                rule_id='ownership.unknown_family',
                severity='warning',
                family='ownership',
                message='Write family is not declared in the single-writer map.',
                entity=case['case_id'],
                location='writes.family',
                expected='declared family',
                observed=family,
                remediation='Declare the family in the canon before using it.',
            ))
        elif writer != expected_writer:
            findings.append(Finding(
                rule_id='ownership.single_writer',
                severity='critical',
                family='ownership',
                message='Artifact was written by a non-sovereign writer.',
                entity=case['case_id'],
                location='writes.writer',
                expected=expected_writer,
                observed=writer,
                remediation='Route the write through the canonical owner only.',
            ))
    if not case.get('writes'):
        findings.append(Finding(
            rule_id='ownership.no_writes',
            severity='info',
            family='ownership',
            message='Case does not emit writes, so ownership remains intact.',
            entity=case['case_id'],
            location='writes',
            expected='optional writes',
            observed=[],
            remediation='None.',
        ))
    return findings
