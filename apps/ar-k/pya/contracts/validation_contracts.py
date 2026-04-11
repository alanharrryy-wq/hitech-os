from __future__ import annotations

from typing import Any, Mapping

from .base import (
    deterministic_id,
    ensure_iso_timestamp,
    ensure_mapping,
    ensure_mapping_field,
    ensure_required,
    ensure_string,
    ensure_type,
    utc_now_z,
)
from .enums import Severity, State

VIOLATION_REQUIRED = [
    "violation_id",
    "rule_id",
    "severity",
    "entity_type",
    "entity_id",
    "location",
    "message",
    "expected",
    "observed",
    "autofixable",
    "snapshot_id",
    "created_at",
]

HEALTH_REQUIRED = [
    "snapshot_id",
    "status",
    "total_rules",
    "total_violations",
    "counts_by_severity",
    "validated_at",
]


def build_validation_violation(**kwargs: Any) -> dict[str, Any]:
    payload = {
        "violation_id": kwargs.get("violation_id") or deterministic_id(
            "vio",
            kwargs["rule_id"],
            kwargs["entity_type"],
            kwargs["entity_id"],
            kwargs["location"],
            kwargs["snapshot_id"],
        ),
        "rule_id": kwargs["rule_id"],
        "severity": kwargs["severity"],
        "entity_type": kwargs["entity_type"],
        "entity_id": kwargs["entity_id"],
        "location": kwargs["location"],
        "message": kwargs["message"],
        "expected": kwargs.get("expected"),
        "observed": kwargs.get("observed"),
        "autofixable": bool(kwargs.get("autofixable", False)),
        "snapshot_id": kwargs["snapshot_id"],
        "created_at": kwargs.get("created_at", utc_now_z()),
    }
    validate_validation_violation(payload)
    return payload


def validate_validation_violation(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("validation_violation", payload)
    ensure_required("validation_violation", payload, VIOLATION_REQUIRED)
    for field in [
        "violation_id",
        "rule_id",
        "severity",
        "entity_type",
        "entity_id",
        "location",
        "message",
        "snapshot_id",
    ]:
        ensure_string("validation_violation", payload, field)
    ensure_type("validation_violation", payload, "autofixable", bool)
    ensure_iso_timestamp("validation_violation", payload, "created_at")
    allowed = {item.value for item in Severity}
    if payload["severity"] not in allowed:
        raise ValueError(f"validation_violation.severity must be one of {sorted(allowed)}")
    return payload


def build_contract_health_summary(snapshot_id: str, total_rules: int, total_violations: int, counts_by_severity: Mapping[str, int], validated_at: str | None = None) -> dict[str, Any]:
    payload = {
        "snapshot_id": snapshot_id,
        "status": State.VALIDATED.value if counts_by_severity.get(Severity.ERROR.value, 0) == 0 and counts_by_severity.get(Severity.CRITICAL.value, 0) == 0 else State.REJECTED.value,
        "total_rules": total_rules,
        "total_violations": total_violations,
        "counts_by_severity": dict(counts_by_severity),
        "validated_at": validated_at or utc_now_z(),
    }
    validate_contract_health_summary(payload)
    return payload


def validate_contract_health_summary(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("contract_health_summary", payload)
    ensure_required("contract_health_summary", payload, HEALTH_REQUIRED)
    ensure_string("contract_health_summary", payload, "snapshot_id")
    ensure_string("contract_health_summary", payload, "status")
    ensure_type("contract_health_summary", payload, "total_rules", int)
    ensure_type("contract_health_summary", payload, "total_violations", int)
    ensure_mapping_field("contract_health_summary", payload, "counts_by_severity")
    ensure_iso_timestamp("contract_health_summary", payload, "validated_at")
    return payload
