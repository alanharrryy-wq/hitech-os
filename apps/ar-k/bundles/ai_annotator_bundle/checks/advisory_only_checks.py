
"""Checks that keep annotations advisory-only."""

from __future__ import annotations

from core.tool_contract import AI_ANNOTATOR_BOUNDARY


class AdvisoryBoundaryError(ValueError):
    """Raised when advisory-only behavior is violated."""


PROMOTION_WORDS = {"promote", "canonicalize", "authoritative", "registry rewrite", "override gate"}


def assert_annotation_status_is_advisory(status: str) -> None:
    allowed = {"suggested", "reviewed", "stale", "accepted", "rejected"}
    if status not in allowed:
        raise AdvisoryBoundaryError(f"Unexpected advisory status: {status}")


def assert_forbidden_write_names(names: list[str]) -> None:
    forbidden = set(AI_ANNOTATOR_BOUNDARY.may_not_write)
    overlap = sorted(forbidden.intersection(names))
    if overlap:
        raise AdvisoryBoundaryError(f"Attempted authoritative writes: {overlap}")


def assert_no_promotion_language(text: str) -> None:
    lowered = text.lower()
    hits = sorted(word for word in PROMOTION_WORDS if word in lowered)
    if hits:
        raise AdvisoryBoundaryError(f"Promotion language detected: {hits}")
