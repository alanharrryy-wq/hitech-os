from __future__ import annotations

PATCH_RESULT_STATUS = (
    "applied",
    "noop",
    "skipped",
    "failed",
    "rolled_back",
)

SYSTEM_RESULT_STATUS = (
    "verified",
    "caution",
    "failed",
    "rolled_back",
    "not_verified",
)

INTERVENTION_GATE_STATUS = (
    "pass",
    "caution",
    "fail",
)


def is_valid_patch_status(value: str) -> bool:
    return value in PATCH_RESULT_STATUS


def is_valid_system_status(value: str) -> bool:
    return value in SYSTEM_RESULT_STATUS


def is_valid_intervention_gate_status(value: str) -> bool:
    return value in INTERVENTION_GATE_STATUS
