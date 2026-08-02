#!/usr/bin/env python3
"""Governed resolver for PRISMA portable visual identity bindings."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "authority" / "rifat" / "identity"
REGISTRY_PATH = IDENTITY / "registries" / "element-bindings.registry.json"
COVERAGE_PATH = IDENTITY / "bindings" / "reports" / "BINDING_COVERAGE.json"
PORTABLE_SCHEMA = "prisma.identity.portable-element-export.v1"
ENVELOPE_SCHEMA = "prisma.identity.binding-envelope.v1"
CANONICALIZATION = "json-sort-keys-compact-utf8-v1"
TRACE_FIELDS = ("ownerId", "routeId", "regionId", "slotId", "componentUiId", "layerId")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def portable_payload(artifact: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in artifact.items() if key not in {"exportId", "integrity"}}


def verify_portable_artifact(artifact: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if artifact.get("schema") != PORTABLE_SCHEMA:
        errors.append("unsupported portable artifact schema")
    if artifact.get("instructionOnly") is not True:
        errors.append("portable artifact must be instruction-only")
    if artifact.get("runtimeMutationAllowed") is not False:
        errors.append("portable artifact runtimeMutationAllowed must be false")
    integrity = artifact.get("integrity") or {}
    expected = sha256_bytes(canonical_bytes(portable_payload(artifact)))
    if integrity.get("canonicalPayloadSha256") != expected:
        errors.append("portable artifact canonical checksum mismatch")
    return errors


def load_registry() -> dict[str, Any]:
    return load_json(REGISTRY_PATH)


def refresh_authority_snapshot(registry: dict[str, Any]) -> bool:
    snapshot = registry["authoritySnapshot"]
    refreshed_files = []
    for item in snapshot["files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            raise FileNotFoundError(f"required authority source is missing: {item['path']}")
        refreshed_files.append(
            {
                **item,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    snapshot_id = sha256_bytes(canonical_bytes(refreshed_files))
    changed = snapshot.get("snapshotId") != snapshot_id or snapshot.get("files") != refreshed_files
    snapshot["files"] = refreshed_files
    snapshot["snapshotId"] = snapshot_id
    snapshot["canonicalization"] = CANONICALIZATION
    if changed:
        snapshot["generatedAt"] = datetime.now(timezone.utc).isoformat()
    return changed


def current_authority_snapshot(registry: dict[str, Any]) -> dict[str, Any]:
    records = []
    drift = []
    for item in registry["authoritySnapshot"]["files"]:
        path = ROOT / item["path"]
        actual = sha256_file(path) if path.is_file() else None
        record = {
            "path": item["path"],
            "expectedSha256": item["sha256"],
            "actualSha256": actual,
            "exists": path.is_file(),
            "matches": actual == item["sha256"],
        }
        records.append(record)
        if not record["matches"]:
            drift.append(record)
    return {
        "snapshotId": registry["authoritySnapshot"]["snapshotId"],
        "status": "PASS" if not drift else "BLOCKED_BY_AUTHORITY_DRIFT",
        "files": records,
        "drift": drift,
    }


def authority_indexes() -> dict[str, Any]:
    routes_doc = load_json(ROOT / "authority/rifat/prisma-ui/routes.json")
    owners_doc = load_json(ROOT / "authority/rifat/prisma-ui/visual-control/owners.json")
    components_doc = load_json(ROOT / "authority/rifat/prisma-ui/visual-control/components.json")
    slots_doc = load_json(ROOT / "authority/rifat/prisma-ui/visual-control/editable-slots.json")
    layers_doc = load_json(ROOT / "authority/rifat/prisma-ui/visual-control/layers.json")
    return {
        "routes": {item["route_id"]: item for item in routes_doc.get("routes", [])},
        "componentOwners": {item["component_id"]: item for item in owners_doc.get("componentOwnerSamples", [])},
        "cssOwners": {item["owner_id"]: item for item in owners_doc.get("cssOwnerSamples", [])},
        "regionOwners": {item["region_id"]: item for item in owners_doc.get("regionOwnerSamples", [])},
        "components": {item["component_id"]: item for item in components_doc.get("components", [])},
        "slots": {item["slot_unit_id"]: item for item in slots_doc.get("slotUnitSamples", [])},
        "layers": {
            item["layer_id"]: item
            for item in [
                *layers_doc.get("layerSamples", []),
                *layers_doc.get("certifiedLayers", []),
            ]
        },
    }


def selector_from_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    identity = artifact.get("identity") or {}
    element = artifact.get("element") or {}
    target = artifact.get("target") or {}
    return {
        "neutralMeaningId": element.get("neutralMeaningId"),
        "identityProfileId": identity.get("identityProfileId"),
        "recipePresetId": identity.get("recipePresetId"),
        "objectId": element.get("objectId"),
        "surfaceId": target.get("surfaceId"),
    }


def selector_matches(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if value == "*":
            continue
        if actual.get(key) != value:
            return False
    return True


def validate_target(target: dict[str, Any], indexes: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lookups = {
        "routeId": "routes",
        "ownerId": "componentOwners",
        "regionId": "regionOwners",
        "slotId": "slots",
        "componentUiId": "components",
        "layerId": "layers",
        "ownerCssId": "cssOwners",
    }
    missing_declared = set(target.get("missingBindings") or [])
    for field, index_name in lookups.items():
        value = target.get(field)
        if value is None:
            if field in TRACE_FIELDS and field not in missing_declared:
                errors.append(f"{target.get('targetId')}: null {field} is not declared missing")
            continue
        if value not in indexes[index_name]:
            errors.append(f"{target.get('targetId')}: orphan {field}={value}")
    unresolved = [field for field in TRACE_FIELDS if target.get(field) is None]
    if unresolved and not str(target.get("status", "")).startswith("BLOCKED"):
        errors.append(f"{target.get('targetId')}: unresolved fields require BLOCKED status")
    if not unresolved and target.get("status") != "RESOLVED":
        errors.append(f"{target.get('targetId')}: complete target must be RESOLVED")
    return errors


def validate_registry(registry: dict[str, Any] | None = None) -> tuple[list[str], list[str]]:
    registry = registry or load_registry()
    errors: list[str] = []
    warnings: list[str] = []
    if registry.get("schema") != "prisma.identity.element-bindings.registry.v1":
        errors.append("registry schema mismatch")
    if registry.get("instructionOnly") is not True or registry.get("runtimeMutationAllowed") is not False:
        errors.append("registry must remain instruction-only and runtime-safe")
    if registry.get("productApplicationAllowed") is not False:
        errors.append("registry must forbid product application")

    ids = [item.get("bindingId") for item in registry.get("bindings", [])]
    if len(ids) != len(set(ids)):
        errors.append("duplicate bindingId")
    target_ids: list[str] = []
    resolved_coordinates: list[tuple[Any, ...]] = []
    indexes = authority_indexes()
    for binding in registry.get("bindings", []):
        for target in binding.get("targets", []):
            target_ids.append(target.get("targetId"))
            errors.extend(validate_target(target, indexes))
            if target.get("status") == "RESOLVED":
                resolved_coordinates.append(tuple(target.get(field) for field in TRACE_FIELDS))
    if len(target_ids) != len(set(target_ids)):
        errors.append("duplicate targetId")
    if len(resolved_coordinates) != len(set(resolved_coordinates)):
        errors.append("collision: duplicate fully-resolved coordinates")

    snapshot = current_authority_snapshot(registry)
    if snapshot["drift"]:
        errors.append("authority drift detected")
    if not any(item.get("status") == "BLOCKED_BY_MISSING_LAYER_ID" for item in registry.get("bindings", [])):
        warnings.append("no explicit missing-layer candidate is registered")
    return errors, warnings


def _covered_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in envelope.items() if key not in {"envelopeId", "integrity"}}


def resolve_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    portable_errors = verify_portable_artifact(artifact)
    if portable_errors:
        raise ValueError("; ".join(portable_errors))
    registry = load_registry()
    authority = current_authority_snapshot(registry)
    selector = selector_from_artifact(artifact)
    matches = [item for item in registry["bindings"] if selector_matches(item["selector"], selector)]
    if authority["status"] != "PASS":
        status = "BLOCKED_BY_AUTHORITY_DRIFT"
    elif not matches:
        status = "BLOCKED_BY_NO_REGISTERED_BINDING"
    elif len(matches) > 1:
        status = "BLOCKED_BY_AMBIGUOUS_REGISTRY_MATCH"
    else:
        status = matches[0]["status"]
    envelope = {
        "schema": ENVELOPE_SCHEMA,
        "version": "1.0.0",
        "instructionOnly": True,
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
        "status": status,
        "sourceArtifact": {
            "exportId": artifact.get("exportId"),
            "schema": artifact.get("schema"),
            "kind": artifact.get("kind"),
            "canonicalPayloadSha256": (artifact.get("integrity") or {}).get("canonicalPayloadSha256"),
            "selector": selector,
        },
        "matches": matches,
        "authoritySnapshot": authority,
        "applicationGate": {
            "allowed": False,
            "reason": "IDBIND1 resolves evidence only. Runtime/product application requires a future exact-target Mesh and visual certification.",
        },
    }
    checksum = sha256_bytes(canonical_bytes(_covered_envelope(envelope)))
    envelope["envelopeId"] = f"BENV.{artifact.get('exportId', 'unknown')}.{checksum[:12]}"
    envelope["integrity"] = {
        "algorithm": "SHA-256",
        "canonicalization": CANONICALIZATION,
        "canonicalPayloadSha256": checksum,
        "coveredTopLevelFields": sorted(_covered_envelope(envelope)),
    }
    return envelope


def verify_envelope(envelope: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if envelope.get("schema") != ENVELOPE_SCHEMA:
        errors.append("binding envelope schema mismatch")
    if envelope.get("instructionOnly") is not True:
        errors.append("binding envelope must be instruction-only")
    if envelope.get("runtimeMutationAllowed") is not False or envelope.get("productApplicationAllowed") is not False:
        errors.append("binding envelope must forbid runtime and product mutation")
    integrity = envelope.get("integrity") or {}
    actual = sha256_bytes(canonical_bytes(_covered_envelope(envelope)))
    if integrity.get("canonicalPayloadSha256") != actual:
        errors.append("binding envelope checksum mismatch")
    return errors


def coverage_report() -> dict[str, Any]:
    registry = load_registry()
    status_counts: dict[str, int] = {}
    for item in registry.get("bindings", []):
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
    full = sum(1 for item in registry.get("bindings", []) if item.get("status") == "RESOLVED")
    partial = sum(1 for item in registry.get("bindings", []) if item.get("targets"))
    return {
        "schema": "prisma.identity.binding-coverage.v1",
        "version": registry["version"],
        "status": "SOURCE_READY_NO_FULLY_RESOLVED_BINDINGS" if full == 0 else "SOURCE_READY_PARTIAL_RESOLUTION",
        "bindingDefinitionCount": len(registry.get("bindings", [])),
        "fullyResolvedCount": full,
        "partiallyGroundedCount": partial,
        "blockedCount": len(registry.get("bindings", [])) - full,
        "surfaceCounts": {
            surface: sum(1 for item in registry.get("bindings", []) if item["selector"].get("surfaceId") == surface)
            for surface in sorted({item["selector"].get("surfaceId") for item in registry.get("bindings", [])})
        },
        "statusCounts": status_counts,
        "authoritySnapshotId": registry["authoritySnapshot"]["snapshotId"],
        "hardTruth": "No binding is RESOLVED until ownerId, routeId, regionId, slotId, componentUiId and layerId are all directly verified.",
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
    }
