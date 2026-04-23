
"""Checks preventing switch, gate, and registry override behavior."""

from __future__ import annotations


class OverrideError(ValueError):
    """Raised when advisory output tries to override authoritative state."""


FORBIDDEN_KEYS = {
    "resolved_value",
    "gate_status",
    "gate_result",
    "canonical_status",
    "promoted_status",
    "authoritative_decision",
}


def assert_annotation_payload_is_non_authoritative(payload: dict[str, object]) -> None:
    bad_keys = sorted(FORBIDDEN_KEYS.intersection(payload))
    if bad_keys:
        raise OverrideError(f"Annotation payload carries authoritative keys: {bad_keys}")
    if payload.get("mode") == "authoritative":
        raise OverrideError("Annotation payload may not claim authoritative mode")


def assert_no_switch_override(payload: dict[str, object]) -> None:
    proposed = payload.get("proposed_switch_value")
    if proposed not in (None, "advisory_only"):
        raise OverrideError("Annotation payload may not override switch output")


def assert_no_gate_override(payload: dict[str, object]) -> None:
    proposed = payload.get("proposed_gate")
    if proposed not in (None, "advisory_only"):
        raise OverrideError("Annotation payload may not override validator gate")
