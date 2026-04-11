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
from .enums import State

REQUIRED_FIELDS = [
    "annotation_id",
    "target_type",
    "target_id",
    "annotation_kind",
    "summary",
    "rationale",
    "source_basis",
    "confidence",
    "status",
    "model_info",
    "snapshot_id",
    "created_at",
]

ALLOWED_STATUS = {
    State.SUGGESTED.value,
    State.REVIEWED.value,
    State.ACCEPTED.value,
    State.REJECTED.value,
    State.STALE.value,
}


def build_annotation(**kwargs: Any) -> dict[str, Any]:
    payload = {
        "annotation_id": kwargs.get("annotation_id") or deterministic_id(
            "ann",
            kwargs["target_type"],
            kwargs["target_id"],
            kwargs["annotation_kind"],
            kwargs["snapshot_id"],
        ),
        "target_type": kwargs["target_type"],
        "target_id": kwargs["target_id"],
        "annotation_kind": kwargs["annotation_kind"],
        "summary": kwargs["summary"],
        "rationale": kwargs["rationale"],
        "source_basis": dict(kwargs["source_basis"]),
        "confidence": round(float(kwargs["confidence"]), 3),
        "status": kwargs.get("status", State.SUGGESTED.value),
        "model_info": dict(kwargs["model_info"]),
        "snapshot_id": kwargs["snapshot_id"],
        "created_at": kwargs.get("created_at", utc_now_z()),
    }
    validate_annotation(payload)
    return payload


def validate_annotation(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("annotation", payload)
    ensure_required("annotation", payload, REQUIRED_FIELDS)
    for field in ["annotation_id", "target_type", "target_id", "annotation_kind", "summary", "rationale", "status", "snapshot_id"]:
        ensure_string("annotation", payload, field)
    ensure_mapping_field("annotation", payload, "source_basis")
    ensure_mapping_field("annotation", payload, "model_info")
    ensure_type("annotation", payload, "confidence", (int, float))
    if not 0.0 <= float(payload["confidence"]) <= 1.0:
        raise ValueError("annotation.confidence must be between 0.0 and 1.0")
    ensure_iso_timestamp("annotation", payload, "created_at")
    if payload["status"] not in ALLOWED_STATUS:
        raise ValueError(f"annotation.status must be one of {sorted(ALLOWED_STATUS)}")
    return payload
