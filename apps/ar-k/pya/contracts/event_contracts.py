from __future__ import annotations

from typing import Any, Mapping

from .base import deterministic_id, ensure_iso_timestamp, ensure_mapping, ensure_mapping_field, ensure_required, ensure_string, utc_now_z
from .enums import Severity

REQUIRED_FIELDS = [
    "event_id",
    "name",
    "producer",
    "target",
    "payload",
    "severity",
    "timestamp",
]


def build_event(*, name: str, producer: str, target: str, payload: Mapping[str, Any], severity: str = Severity.INFO.value, timestamp: str | None = None, correlation_id: str | None = None) -> dict[str, Any]:
    event = {
        "event_id": deterministic_id("evt", name, producer, target, timestamp or utc_now_z()),
        "name": name,
        "producer": producer,
        "target": target,
        "payload": dict(payload),
        "severity": severity,
        "timestamp": timestamp or utc_now_z(),
        "correlation_id": correlation_id,
    }
    validate_event(event)
    return event


def validate_event(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("event", payload)
    ensure_required("event", payload, REQUIRED_FIELDS)
    for field in ["event_id", "name", "producer", "target", "severity"]:
        ensure_string("event", payload, field)
    ensure_mapping_field("event", payload, "payload")
    ensure_iso_timestamp("event", payload, "timestamp")
    allowed = {item.value for item in Severity}
    if payload["severity"] not in allowed:
        raise ValueError(f"event.severity must be one of {sorted(allowed)}")
    if payload.get("correlation_id") is not None:
        ensure_string("event", payload, "correlation_id")
    return payload
