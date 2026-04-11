from __future__ import annotations

from typing import Any, Mapping

from .base import deterministic_id, ensure_iso_timestamp, ensure_mapping, ensure_required, ensure_string, utc_now_z

REQUIRED_FIELDS = [
    "artifact_id",
    "family",
    "path",
    "producer",
    "snapshot_id",
    "created_at",
]


def build_artifact(*, family: str, path: str, producer: str, snapshot_id: str, content_hash: str | None = None, created_at: str | None = None) -> dict[str, Any]:
    payload = {
        "artifact_id": deterministic_id("art", family, path, snapshot_id),
        "family": family,
        "path": path,
        "producer": producer,
        "snapshot_id": snapshot_id,
        "hash": content_hash,
        "created_at": created_at or utc_now_z(),
    }
    validate_artifact(payload)
    return payload


def validate_artifact(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("artifact", payload)
    ensure_required("artifact", payload, REQUIRED_FIELDS)
    for field in ["artifact_id", "family", "path", "producer", "snapshot_id"]:
        ensure_string("artifact", payload, field)
    if payload.get("hash") is not None:
        ensure_string("artifact", payload, "hash")
    ensure_iso_timestamp("artifact", payload, "created_at")
    return payload
