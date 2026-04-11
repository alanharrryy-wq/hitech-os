from __future__ import annotations

from typing import Any, Mapping

from .base import (
    deterministic_id,
    ensure_iso_timestamp,
    ensure_list_of_mappings,
    ensure_list_of_strings,
    ensure_mapping,
    ensure_mapping_field,
    ensure_required,
    ensure_string,
    ensure_type,
    utc_now_z,
)
from .enums import State

MODULE_REQUIRED = [
    "module_id",
    "name",
    "kind",
    "area",
    "status",
    "source_of_truth",
    "confidence",
    "declared_by",
    "observed_in",
    "tags",
    "boundaries",
    "switches",
    "contracts",
    "artifacts",
    "updated_at",
    "snapshot_id",
]

BOUNDARY_REQUIRED = [
    "boundary_id",
    "source_module_id",
    "target_id",
    "target_type",
    "boundary_type",
    "source_of_truth",
    "status",
    "evidence",
    "snapshot_id",
    "updated_at",
]

CONTRACT_REGISTRY_REQUIRED = [
    "contract_id",
    "version",
    "owner",
    "module",
    "state",
    "compatibility",
    "description",
    "updated_at",
]

REGISTRY_BUILD_SUMMARY_REQUIRED = [
    "snapshot_id",
    "module_count",
    "boundary_count",
    "contract_count",
    "conflicts",
    "created_at",
]

MODULE_ALLOWED_STATES = {
    State.CANDIDATE.value,
    State.CANONICAL.value,
    State.DEPRECATED.value,
    State.SUPERSEDED.value,
    State.AMBIGUOUS.value,
}

BOUNDARY_ALLOWED_STATES = {State.CANDIDATE.value, State.CANONICAL.value, State.DEPRECATED.value}


def build_module_registry_entry(**kwargs: Any) -> dict[str, Any]:
    payload = {
        "module_id": kwargs["module_id"],
        "name": kwargs["name"],
        "kind": kwargs["kind"],
        "area": kwargs["area"],
        "status": kwargs["status"],
        "source_of_truth": kwargs["source_of_truth"],
        "confidence": round(float(kwargs["confidence"]), 3),
        "declared_by": list(kwargs["declared_by"]),
        "observed_in": list(kwargs["observed_in"]),
        "tags": list(kwargs.get("tags", [])),
        "boundaries": list(kwargs.get("boundaries", [])),
        "switches": list(kwargs.get("switches", [])),
        "contracts": list(kwargs.get("contracts", [])),
        "artifacts": list(kwargs.get("artifacts", [])),
        "updated_at": kwargs.get("updated_at", utc_now_z()),
        "snapshot_id": kwargs["snapshot_id"],
    }
    validate_module_registry_entry(payload)
    return payload


def validate_module_registry_entry(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("module_registry_entry", payload)
    ensure_required("module_registry_entry", payload, MODULE_REQUIRED)
    for field in ["module_id", "name", "kind", "area", "status", "source_of_truth", "snapshot_id"]:
        ensure_string("module_registry_entry", payload, field)
    ensure_type("module_registry_entry", payload, "confidence", (int, float))
    if not 0.0 <= float(payload["confidence"]) <= 1.0:
        raise ValueError("module_registry_entry.confidence must be between 0.0 and 1.0")
    for field in ["declared_by", "observed_in", "tags", "boundaries", "switches", "contracts", "artifacts"]:
        ensure_list_of_strings("module_registry_entry", payload, field)
    ensure_iso_timestamp("module_registry_entry", payload, "updated_at")
    if payload["status"] not in MODULE_ALLOWED_STATES:
        raise ValueError(f"module_registry_entry.status must be one of {sorted(MODULE_ALLOWED_STATES)}")
    return payload


def build_boundary_entry(**kwargs: Any) -> dict[str, Any]:
    payload = {
        "boundary_id": kwargs.get("boundary_id") or deterministic_id(
            "bnd",
            kwargs["source_module_id"],
            kwargs["target_id"],
            kwargs["boundary_type"],
            kwargs["snapshot_id"],
        ),
        "source_module_id": kwargs["source_module_id"],
        "target_id": kwargs["target_id"],
        "target_type": kwargs["target_type"],
        "boundary_type": kwargs["boundary_type"],
        "source_of_truth": kwargs["source_of_truth"],
        "status": kwargs["status"],
        "evidence": dict(kwargs["evidence"]),
        "snapshot_id": kwargs["snapshot_id"],
        "updated_at": kwargs.get("updated_at", utc_now_z()),
    }
    validate_boundary_entry(payload)
    return payload


def validate_boundary_entry(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("boundary_entry", payload)
    ensure_required("boundary_entry", payload, BOUNDARY_REQUIRED)
    for field in [
        "boundary_id",
        "source_module_id",
        "target_id",
        "target_type",
        "boundary_type",
        "source_of_truth",
        "status",
        "snapshot_id",
    ]:
        ensure_string("boundary_entry", payload, field)
    ensure_mapping_field("boundary_entry", payload, "evidence")
    ensure_iso_timestamp("boundary_entry", payload, "updated_at")
    if payload["status"] not in BOUNDARY_ALLOWED_STATES:
        raise ValueError(f"boundary_entry.status must be one of {sorted(BOUNDARY_ALLOWED_STATES)}")
    return payload


def validate_contract_registry_entry(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("contract_registry_entry", payload)
    ensure_required("contract_registry_entry", payload, CONTRACT_REGISTRY_REQUIRED)
    for field in ["contract_id", "version", "owner", "module", "state", "description"]:
        ensure_string("contract_registry_entry", payload, field)
    ensure_mapping_field("contract_registry_entry", payload, "compatibility")
    ensure_iso_timestamp("contract_registry_entry", payload, "updated_at")
    return payload


def build_contract_registry_entry(**kwargs: Any) -> dict[str, Any]:
    payload = {
        "contract_id": kwargs["contract_id"],
        "version": kwargs["version"],
        "owner": kwargs["owner"],
        "module": kwargs["module"],
        "state": kwargs.get("state", State.CANONICAL.value),
        "compatibility": dict(kwargs.get("compatibility", {"backward": [kwargs["version"]]})),
        "description": kwargs["description"],
        "updated_at": kwargs.get("updated_at", utc_now_z()),
    }
    validate_contract_registry_entry(payload)
    return payload


def validate_registry_build_summary(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = ensure_mapping("registry_build_summary", payload)
    ensure_required("registry_build_summary", payload, REGISTRY_BUILD_SUMMARY_REQUIRED)
    ensure_string("registry_build_summary", payload, "snapshot_id")
    for field in ["module_count", "boundary_count", "contract_count"]:
        ensure_type("registry_build_summary", payload, field, int)
    ensure_list_of_mappings("registry_build_summary", payload, "conflicts")
    ensure_iso_timestamp("registry_build_summary", payload, "created_at")
    return payload


def build_registry_build_summary(snapshot_id: str, module_count: int, boundary_count: int, contract_count: int, conflicts: list[dict[str, Any]], created_at: str | None = None) -> dict[str, Any]:
    payload = {
        "snapshot_id": snapshot_id,
        "module_count": module_count,
        "boundary_count": boundary_count,
        "contract_count": contract_count,
        "conflicts": conflicts,
        "created_at": created_at or utc_now_z(),
    }
    validate_registry_build_summary(payload)
    return payload
