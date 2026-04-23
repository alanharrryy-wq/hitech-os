
"""Checks preventing promotion of observed or advisory data."""

from __future__ import annotations


class PromotionError(ValueError):
    """Raised when an annotation case attempts promotion behavior."""


FORBIDDEN_PROMOTION_FIELDS = {
    "promote_to_canonical",
    "write_registry_index",
    "rewrite_registry",
    "canonical_owner",
}


def assert_no_promotion_fields(case: dict[str, object]) -> None:
    overlap = sorted(FORBIDDEN_PROMOTION_FIELDS.intersection(case))
    if overlap:
        raise PromotionError(f"Forbidden promotion fields present: {overlap}")


def assert_annotation_output_family(name: str) -> None:
    if name not in {"annotations.json", "annotation_index.json", "annotation_summary.json"}:
        raise PromotionError(f"Unexpected output family: {name}")
