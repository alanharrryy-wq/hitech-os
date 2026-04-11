from __future__ import annotations

from typing import Any, Mapping

from .base import deterministic_id, ensure_iso_timestamp, ensure_list_of_strings, ensure_mapping, ensure_required, ensure_string, utc_now_z

REQUIRED_FIELDS = [
    "index_id",
    "entity_type",
    "entity_id",
    "lookup_keys",
    "registry_source",
    "snapshot_id",
    "updated_at",
]


def build_query_index_entry(*, entity_type: str, entity_id: str, lookup_keys: list[str], registry_source: str, snapshot_id: str, updated_at: str | None = None) -> dict[str, Any]:
    payload = {
        "index_id": deterministic_id("idx", entity_type, entity_id, snapshot_id),
        "entity_type": entity_type,
        "entity_id": entity_id,
        "lookup_keys": lookup_keys,
        "registry_source": registry_source,
        "snapshot_id": snapshot_id,
        "updated_at": updated_at or utc_now_z(),
    }
    validate_query_index_entry(payload)
    return payload


def validate_query_index_entry(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("query_index", payload)
    ensure_required("query_index", payload, REQUIRED_FIELDS)
    for field in ["index_id", "entity_type", "entity_id", "registry_source", "snapshot_id"]:
        ensure_string("query_index", payload, field)
    ensure_list_of_strings("query_index", payload, "lookup_keys")
    ensure_iso_timestamp("query_index", payload, "updated_at")
    return payload
