from __future__ import annotations

from typing import Any, Mapping

from .base import ensure_iso_timestamp, ensure_list_of_strings, ensure_mapping, ensure_mapping_field, ensure_required, ensure_string, ensure_type, utc_now_z
from .enums import EngineType, Stage

MANIFEST_REQUIRED = [
    "engine_id",
    "engine_type",
    "version",
    "owner",
    "area",
    "purpose",
    "execution_modes",
    "inputs_declared",
    "outputs_declared",
    "events_emitted",
    "registries_touched",
    "feature_flags_used",
    "health_contract",
    "error_contract",
    "observability_contract",
    "permissions",
    "dependencies",
    "compatibility",
    "stage",
    "entrypoint",
]

EXECUTION_SUMMARY_REQUIRED = [
    "execution_id",
    "engine_id",
    "stage",
    "status",
    "started_at",
    "finished_at",
    "metrics",
    "registries_written",
    "artifacts",
    "events",
]


def validate_engine_manifest(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("engine_manifest", payload)
    ensure_required("engine_manifest", payload, MANIFEST_REQUIRED)
    for field in ["engine_id", "engine_type", "version", "owner", "area", "purpose", "stage", "entrypoint"]:
        ensure_string("engine_manifest", payload, field)
    for field in ["execution_modes", "inputs_declared", "outputs_declared", "events_emitted", "feature_flags_used", "dependencies"]:
        ensure_list_of_strings("engine_manifest", payload, field)
    for field in ["registries_touched", "health_contract", "error_contract", "observability_contract", "permissions", "compatibility"]:
        ensure_mapping_field("engine_manifest", payload, field)
    engine_types = {item.value for item in EngineType}
    if payload["engine_type"] not in engine_types:
        raise ValueError(f"engine_manifest.engine_type must be one of {sorted(engine_types)}")
    stages = {item.value for item in Stage}
    if payload["stage"] not in stages:
        raise ValueError(f"engine_manifest.stage must be one of {sorted(stages)}")
    return payload


def build_execution_summary(**kwargs: Any) -> dict[str, Any]:
    payload = {
        "execution_id": kwargs["execution_id"],
        "engine_id": kwargs["engine_id"],
        "stage": kwargs["stage"],
        "status": kwargs.get("status", "ok"),
        "started_at": kwargs["started_at"],
        "finished_at": kwargs.get("finished_at", utc_now_z()),
        "metrics": dict(kwargs.get("metrics", {})),
        "registries_written": list(kwargs.get("registries_written", [])),
        "artifacts": list(kwargs.get("artifacts", [])),
        "events": list(kwargs.get("events", [])),
        "notes": list(kwargs.get("notes", [])),
    }
    validate_execution_summary(payload)
    return payload


def validate_execution_summary(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("execution_summary", payload)
    ensure_required("execution_summary", payload, EXECUTION_SUMMARY_REQUIRED)
    for field in ["execution_id", "engine_id", "stage", "status"]:
        ensure_string("execution_summary", payload, field)
    for field in ["started_at", "finished_at"]:
        ensure_iso_timestamp("execution_summary", payload, field)
    ensure_mapping_field("execution_summary", payload, "metrics")
    ensure_list_of_strings("execution_summary", payload, "registries_written")
    ensure_type("execution_summary", payload, "artifacts", list)
    ensure_type("execution_summary", payload, "events", list)
    if "notes" in payload:
        ensure_list_of_strings("execution_summary", payload, "notes")
    return payload
