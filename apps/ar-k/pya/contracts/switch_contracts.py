from __future__ import annotations

from typing import Any, Mapping

from .base import (
    deterministic_id,
    ensure_iso_timestamp,
    ensure_list_of_strings,
    ensure_mapping,
    ensure_mapping_field,
    ensure_required,
    ensure_string,
    ensure_type,
    utc_now_z,
)
from .enums import State

SWITCH_REQUIRED = [
    "switch_id",
    "target_type",
    "target_id",
    "default_value",
    "applicable_rules",
    "allowed_overrides",
    "rollout",
    "metadata",
    "state",
    "updated_at",
]

RESOLUTION_REQUIRED = [
    "switch_id",
    "target_type",
    "target_id",
    "evaluated_context",
    "default_value",
    "resolved_value",
    "decision_source",
    "precedence_path",
    "justification",
    "timestamp",
]

ALLOWED_SWITCH_STATES = {State.CANDIDATE.value, State.CANONICAL.value, State.DEPRECATED.value}
ALLOWED_RESOLUTION_STATES = {State.RESOLVED.value, State.EFFECTIVE.value}


def build_switch_registry_entry(**kwargs: Any) -> dict[str, Any]:
    payload = {
        "switch_id": kwargs.get("switch_id") or deterministic_id(
            "swh", kwargs["target_type"], kwargs["target_id"]
        ),
        "target_type": kwargs["target_type"],
        "target_id": kwargs["target_id"],
        "default_value": bool(kwargs.get("default_value", True)),
        "applicable_rules": list(kwargs.get("applicable_rules", [])),
        "allowed_overrides": list(kwargs.get("allowed_overrides", [])),
        "rollout": dict(kwargs.get("rollout", {"strategy": "static"})),
        "metadata": dict(kwargs.get("metadata", {})),
        "state": kwargs.get("state", State.CANONICAL.value),
        "updated_at": kwargs.get("updated_at", utc_now_z()),
    }
    validate_switch_registry_entry(payload)
    return payload


def validate_switch_registry_entry(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("switch_registry_entry", payload)
    ensure_required("switch_registry_entry", payload, SWITCH_REQUIRED)
    for field in ["switch_id", "target_type", "target_id", "state"]:
        ensure_string("switch_registry_entry", payload, field)
    ensure_type("switch_registry_entry", payload, "default_value", bool)
    ensure_list_of_strings("switch_registry_entry", payload, "applicable_rules")
    ensure_list_of_strings("switch_registry_entry", payload, "allowed_overrides")
    ensure_mapping_field("switch_registry_entry", payload, "rollout")
    ensure_mapping_field("switch_registry_entry", payload, "metadata")
    ensure_iso_timestamp("switch_registry_entry", payload, "updated_at")
    if payload["state"] not in ALLOWED_SWITCH_STATES:
        raise ValueError(f"switch_registry_entry.state must be one of {sorted(ALLOWED_SWITCH_STATES)}")
    return payload


def build_switch_resolution(**kwargs: Any) -> dict[str, Any]:
    payload = {
        "switch_id": kwargs["switch_id"],
        "target_type": kwargs["target_type"],
        "target_id": kwargs["target_id"],
        "evaluated_context": dict(kwargs.get("evaluated_context", {})),
        "default_value": bool(kwargs["default_value"]),
        "resolved_value": bool(kwargs["resolved_value"]),
        "decision_source": kwargs["decision_source"],
        "precedence_path": list(kwargs["precedence_path"]),
        "justification": kwargs["justification"],
        "timestamp": kwargs.get("timestamp", utc_now_z()),
        "state": kwargs.get("state", State.RESOLVED.value),
    }
    validate_switch_resolution(payload)
    return payload


def validate_switch_resolution(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("switch_resolution", payload)
    ensure_required("switch_resolution", payload, RESOLUTION_REQUIRED)
    for field in ["switch_id", "target_type", "target_id", "decision_source", "justification"]:
        ensure_string("switch_resolution", payload, field)
    ensure_mapping_field("switch_resolution", payload, "evaluated_context")
    ensure_type("switch_resolution", payload, "default_value", bool)
    ensure_type("switch_resolution", payload, "resolved_value", bool)
    ensure_list_of_strings("switch_resolution", payload, "precedence_path")
    ensure_iso_timestamp("switch_resolution", payload, "timestamp")
    if "state" in payload:
        ensure_string("switch_resolution", payload, "state")
        if payload["state"] not in ALLOWED_RESOLUTION_STATES:
            raise ValueError(f"switch_resolution.state must be one of {sorted(ALLOWED_RESOLUTION_STATES)}")
    return payload
