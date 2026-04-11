from __future__ import annotations

from typing import Any, Mapping

from .base import (
    deterministic_id,
    ensure_enum_value,
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

REQUIRED_FIELDS = [
    "signal_id",
    "signal_type",
    "source_path",
    "producer",
    "state",
    "confidence",
    "evidence",
    "snapshot_id",
    "created_at",
]

ALLOWED_SIGNAL_STATES = {State.OBSERVED.value, State.CANDIDATE.value, State.AMBIGUOUS.value, State.DECLARED.value}


def build_signal(*, signal_type: str, source_path: str, producer: str, state: str, confidence: float, evidence: Mapping[str, Any], snapshot_id: str, created_at: str | None = None, tags: list[str] | None = None, module_name: str | None = None) -> dict[str, Any]:
    payload = {
        "signal_id": deterministic_id("sig", signal_type, source_path, state, snapshot_id),
        "signal_type": signal_type,
        "source_path": source_path,
        "producer": producer,
        "state": state,
        "confidence": round(float(confidence), 3),
        "evidence": dict(evidence),
        "snapshot_id": snapshot_id,
        "created_at": created_at or utc_now_z(),
        "tags": list(tags or []),
    }
    if module_name:
        payload["module_name"] = module_name
    validate_signal(payload)
    return payload


def validate_signal(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("signal", payload)
    ensure_required("signal", payload, REQUIRED_FIELDS)
    for field in ["signal_id", "signal_type", "source_path", "producer", "snapshot_id"]:
        ensure_string("signal", payload, field)
    ensure_string("signal", payload, "created_at")
    ensure_iso_timestamp("signal", payload, "created_at")
    ensure_type("signal", payload, "confidence", (int, float))
    if not 0.0 <= float(payload["confidence"]) <= 1.0:
        raise ValueError("signal.confidence must be between 0.0 and 1.0")
    ensure_mapping_field("signal", payload, "evidence")
    if "tags" in payload:
        ensure_list_of_strings("signal", payload, "tags")
    ensure_enum_value("signal", payload, "state", State)
    if payload["state"] not in ALLOWED_SIGNAL_STATES:
        raise ValueError(f"signal.state must be one of {sorted(ALLOWED_SIGNAL_STATES)}")
    if "module_name" in payload:
        ensure_string("signal", payload, "module_name")
    return payload
