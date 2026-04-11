from __future__ import annotations

from typing import Any, Mapping

from .base import deterministic_id, ensure_iso_timestamp, ensure_mapping, ensure_required, ensure_string, utc_now_z

SNAPSHOT_REQUIRED = ["snapshot_id", "format", "hash", "family", "created_at", "payload"]
DELTA_REQUIRED = ["delta_id", "snapshot_id", "family", "hash", "created_at", "payload"]


def build_snapshot(*, family: str, payload: Any, content_hash: str, created_at: str | None = None, snapshot_id: str | None = None) -> dict[str, Any]:
    snapshot = {
        "snapshot_id": snapshot_id or deterministic_id("snp", family, content_hash),
        "format": "json",
        "hash": content_hash,
        "family": family,
        "created_at": created_at or utc_now_z(),
        "payload": payload,
    }
    validate_snapshot(snapshot)
    return snapshot


def build_delta(*, snapshot_id: str, family: str, payload: Any, content_hash: str, created_at: str | None = None) -> dict[str, Any]:
    delta = {
        "delta_id": deterministic_id("dlt", snapshot_id, family, content_hash),
        "snapshot_id": snapshot_id,
        "family": family,
        "hash": content_hash,
        "created_at": created_at or utc_now_z(),
        "payload": payload,
    }
    validate_delta(delta)
    return delta


def validate_snapshot(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("snapshot", payload)
    ensure_required("snapshot", payload, SNAPSHOT_REQUIRED)
    for field in ["snapshot_id", "format", "hash", "family"]:
        ensure_string("snapshot", payload, field)
    ensure_iso_timestamp("snapshot", payload, "created_at")
    return payload


def validate_delta(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("delta", payload)
    ensure_required("delta", payload, DELTA_REQUIRED)
    for field in ["delta_id", "snapshot_id", "family", "hash"]:
        ensure_string("delta", payload, field)
    ensure_iso_timestamp("delta", payload, "created_at")
    return payload
