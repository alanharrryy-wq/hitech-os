
"""Checks for annotation artifact invariants."""

from __future__ import annotations

from checks.authoritative_override_checks import assert_annotation_payload_is_non_authoritative
from checks.promotion_checks import assert_annotation_output_family


class AnnotationContractError(ValueError):
    """Raised when annotation artifacts fail contract checks."""


REQUIRED_KEYS = {
    "annotation_id",
    "target_type",
    "target_id",
    "summary",
    "rationale",
    "confidence",
    "status",
    "advisory_only",
}


def assert_annotation_record(record: dict[str, object]) -> None:
    missing = sorted(REQUIRED_KEYS.difference(record))
    if missing:
        raise AnnotationContractError(f"Annotation record missing keys: {missing}")
    if record.get('advisory_only') is not True:
        raise AnnotationContractError('Annotation records must carry advisory_only=True')
    if not 0.0 <= float(record['confidence']) <= 1.0:
        raise AnnotationContractError('Annotation confidence must be between 0.0 and 1.0')
    assert_annotation_payload_is_non_authoritative(record)


def assert_output_name(name: str) -> None:
    assert_annotation_output_family(name)
