#!/usr/bin/env python3
"""Portable, verifiable and instruction-only exports for PRISMA identity objects."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from identity_dictionary_core import IDENTITY, ROOT, SURFACES, load_json, load_model, merge_tokens

ARTIFACT_SCHEMA = "prisma.identity.portable-element-export.v1"
ARTIFACT_VERSION = "1.0.0"
CANONICALIZATION = "json-sort-keys-compact-utf8-v1"
EXTENSION = ".prisma-visual.json"
EXCLUDED_INTEGRITY_FIELDS = ("exportId", "integrity")
SAFE_ID = re.compile(r"[^a-zA-Z0-9._-]+")


def canonical_compact(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def covered_payload(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in artifact.items()
        if key not in EXCLUDED_INTEGRITY_FIELDS
    }


def verify_artifact(artifact: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if artifact.get("schema") != ARTIFACT_SCHEMA:
        errors.append("unsupported artifact schema")
    if artifact.get("instructionOnly") is not True:
        errors.append("instructionOnly must be true")
    if artifact.get("runtimeMutationAllowed") is not False:
        errors.append("runtimeMutationAllowed must be false")

    integrity = artifact.get("integrity")
    if not isinstance(integrity, dict):
        errors.append("integrity block missing")
        return errors, warnings
    if integrity.get("algorithm") != "SHA-256":
        errors.append("integrity algorithm must be SHA-256")
    if integrity.get("canonicalization") != CANONICALIZATION:
        errors.append("unsupported canonicalization")
    expected = sha256_hex(canonical_compact(covered_payload(artifact)))
    actual = integrity.get("canonicalPayloadSha256")
    if actual != expected:
        errors.append(f"checksum mismatch: expected {expected}, got {actual}")

    target = artifact.get("target") or {}
    trace_fields = ("surfaceId", "ownerId", "routeId", "regionId", "slotId")
    missing = [field for field in trace_fields if target.get(field) is None]
    declared_missing = set(target.get("missingBindings") or [])
    undeclared = [field for field in missing if field not in declared_missing]
    if undeclared:
        errors.append(f"null bindings not declared as missing: {undeclared}")
    binding_status = str(target.get("bindingStatus") or "")
    if missing and "BLOCKED" not in binding_status:
        errors.append("missing bindings require a blocking bindingStatus")

    application = artifact.get("applicationPolicy") or {}
    if application.get("mode") != "INSTRUCTION_ONLY":
        errors.append("application policy must remain INSTRUCTION_ONLY")
    if application.get("productApplicationAllowed") is not False:
        errors.append("product application must remain forbidden")

    if target.get("surfaceReadiness") == "CERTIFIED_BINDING_SOURCE" and missing:
        warnings.append(
            "Surface-level binding sources exist, but this element has no concrete owner/route/region/slot binding."
        )
    return errors, warnings


def _profile_version(profile: dict[str, Any]) -> str:
    return str(profile.get("version") or "1.0.0")


def _definition(model: dict[str, Any], token_id: str) -> dict[str, Any]:
    for item in model["tokens"]["tokens"]:
        if item["id"] == token_id:
            return item
    raise KeyError(f"Unknown semantic token: {token_id}")


def _profile(model: dict[str, Any], profile_id: str) -> dict[str, Any]:
    try:
        return model["profiles"][profile_id]
    except KeyError as exc:
        raise KeyError(f"Unknown identity profile: {profile_id}") from exc


def _surface(model: dict[str, Any], surface: str) -> None:
    if surface not in SURFACES:
        raise KeyError(f"Unknown surface: {surface}")
    if surface not in model["bindings"] or surface not in model["adapters"]:
        raise KeyError(f"Surface lacks identity authority: {surface}")


def _target(
    model: dict[str, Any],
    surface: str | None,
    *,
    component_ui_id: str | None = None,
    owner_id: str | None = None,
    route_id: str | None = None,
    region_id: str | None = None,
    slot_id: str | None = None,
) -> dict[str, Any]:
    binding = model["bindings"].get(surface) if surface else None
    values = {
        "surfaceId": surface,
        "ownerId": owner_id,
        "routeId": route_id,
        "regionId": region_id,
        "slotId": slot_id,
    }
    missing = [key for key, value in values.items() if value is None]
    if component_ui_id is None:
        missing.append("componentUiId")
    if not surface:
        status = "BLOCKED_BY_MISSING_BINDING"
    elif binding and binding.get("readiness") == "CERTIFIED_BINDING_SOURCE":
        status = "BLOCKED_BY_MISSING_ELEMENT_BINDING" if missing else "ELEMENT_BINDING_READY_SOURCE_ONLY"
    elif binding and binding.get("readiness") == "NEUTRAL_SOURCE_READY":
        status = "BLOCKED_BY_MISSING_BINDING"
    else:
        status = "BLOCKED_BY_MISSING_BINDING"
    return {
        **values,
        "bindingStatus": status,
        "surfaceReadiness": binding.get("readiness") if binding else None,
        "surfaceBindingSources": {
            "routeSource": binding.get("routeSource") if binding else None,
            "ownerSource": binding.get("ownerSource") if binding else None,
            "slotSource": binding.get("slotSource") if binding else None,
            "layerSource": binding.get("layerSource") if binding else None,
        },
        "missingBindings": sorted(set(missing)),
    }


def _origin(path: str, registry: str, selected_profile: str) -> dict[str, Any]:
    return {
        "authority": "prisma-html/authority/rifat/identity",
        "sourcePath": path,
        "sourceRegistry": registry,
        "selectedProfileId": selected_profile,
        "generatedBy": "tools/portable_identity_export.py",
    }


def _application_policy() -> dict[str, Any]:
    return {
        "mode": "INSTRUCTION_ONLY",
        "productApplicationAllowed": False,
        "runtimeMutationAllowed": False,
        "requiresFutureGovernedApplicationGate": True,
        "requiredFutureEvidence": [
            "fresh Authority Mesh for the exact target",
            "concrete owner/route/region/slot binding",
            "pre-change hashes",
            "transactional backup and rollback",
            "surface-specific static validation",
            "visual evidence",
            "no fake green",
        ],
    }


def _finalize(artifact: dict[str, Any]) -> dict[str, Any]:
    checksum = sha256_hex(canonical_compact(covered_payload(artifact)))
    slug = SAFE_ID.sub("-", f"{artifact['kind']}-{artifact['element']['objectId']}").strip("-").lower()
    artifact["exportId"] = f"PEX.{slug}.{checksum[:12]}"
    artifact["integrity"] = {
        "algorithm": "SHA-256",
        "canonicalization": CANONICALIZATION,
        "coveredTopLevelFields": sorted(covered_payload(artifact)),
        "canonicalPayloadSha256": checksum,
    }
    errors, _warnings = verify_artifact(artifact)
    if errors:
        raise ValueError("Invalid generated artifact: " + "; ".join(errors))
    return artifact


def _base(
    *,
    kind: str,
    profile: dict[str, Any],
    recipe_preset_id: str | None,
    neutral_meaning_id: str,
    object_id: str,
    component_ui_id: str | None,
    target: dict[str, Any],
    values: dict[str, Any],
    origin: dict[str, Any],
    compatibility: dict[str, Any],
    preview: dict[str, Any] | None,
) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    artifact = {
        "schema": ARTIFACT_SCHEMA,
        "artifactVersion": ARTIFACT_VERSION,
        "kind": kind,
        "createdAt": created_at,
        "instructionOnly": True,
        "runtimeMutationAllowed": False,
        "identity": {
            "identityProfileId": profile["id"],
            "identityProfileVersion": _profile_version(profile),
            "recipePresetId": recipe_preset_id,
        },
        "element": {
            "neutralMeaningId": neutral_meaning_id,
            "objectId": object_id,
            "componentUiId": component_ui_id,
            "version": ARTIFACT_VERSION,
        },
        "target": target,
        "values": values,
        "origin": origin,
        "compatibility": compatibility,
        "preview": preview,
        "applicationPolicy": _application_policy(),
        "manifest": {
            "recordCount": 1,
            "records": [
                {
                    "recordId": object_id,
                    "recordKind": kind,
                    "instructionOnly": True,
                }
            ],
        },
    }
    return _finalize(artifact)


def export_profile(
    profile_id: str,
    *,
    surface: str = "shared-ui",
    model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = model or load_model()
    _surface(model, surface)
    profile = _profile(model, profile_id)
    return _base(
        kind="identity-profile",
        profile=profile,
        recipe_preset_id=profile["id"],
        neutral_meaning_id="VIS.identity.profile",
        object_id=profile["id"],
        component_ui_id=None,
        target=_target(model, surface),
        values={"profile": copy.deepcopy(profile)},
        origin=_origin(
            f"profiles/{profile['id']}.identity.json",
            "registries/identity.registry.json",
            profile["id"],
        ),
        compatibility={
            "supportedSurfaces": list(SURFACES),
            "selectedSurface": surface,
            "surfaceRuntimeProjectionAllowed": False,
            "artifactSchema": ARTIFACT_SCHEMA,
        },
        preview={
            "traits": profile.get("traits", []),
            "tokenOverrideCount": len(profile.get("tokenOverrides", {})),
        },
    )


def export_token(
    token_id: str,
    *,
    profile_id: str,
    surface: str,
    model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = model or load_model()
    _surface(model, surface)
    profile = _profile(model, profile_id)
    definition = _definition(model, token_id)
    resolved = merge_tokens(model, profile_id, surface)[token_id]
    override_source = "default"
    if token_id in profile.get("tokenOverrides", {}):
        override_source = "identity-profile"
    if token_id in model["adapters"][surface].get("tokenOverrides", {}):
        override_source = "surface-adapter"
    preview = {
        "type": definition.get("type"),
        "value": resolved,
    }
    return _base(
        kind="semantic-token",
        profile=profile,
        recipe_preset_id=profile["id"],
        neutral_meaning_id=f"TOK.{token_id}",
        object_id=token_id,
        component_ui_id=None,
        target=_target(model, surface),
        values={
            "definition": copy.deepcopy(definition),
            "resolvedValue": resolved,
            "defaultValue": definition.get("default"),
            "overrideSource": override_source,
            "cssVariable": "--prisma-identity-" + token_id.replace(".", "-"),
        },
        origin=_origin(
            "registries/semantic-tokens.registry.json",
            "registries/semantic-tokens.registry.json",
            profile_id,
        ),
        compatibility={
            "supportedSurfaces": list(SURFACES),
            "selectedSurface": surface,
            "surfaceRuntimeProjectionAllowed": False,
            "valueType": definition.get("type"),
        },
        preview=preview,
    )


def export_surface_adapter(
    surface: str,
    *,
    profile_id: str,
    model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = model or load_model()
    _surface(model, surface)
    profile = _profile(model, profile_id)
    adapter = model["adapters"][surface]
    projection_tokens = merge_tokens(model, profile_id, surface)
    return _base(
        kind="surface-adapter",
        profile=profile,
        recipe_preset_id=adapter["id"],
        neutral_meaning_id="VIS.surface.adapter",
        object_id=adapter["id"],
        component_ui_id=None,
        target=_target(model, surface),
        values={
            "adapter": copy.deepcopy(adapter),
            "resolvedTokenCount": len(projection_tokens),
            "surfaceBinding": copy.deepcopy(model["bindings"][surface]),
        },
        origin=_origin(
            f"adapters/{surface}.adapter.json",
            "registries/surface-adapters.registry.json",
            profile_id,
        ),
        compatibility={
            "supportedSurfaces": [surface],
            "selectedSurface": surface,
            "surfaceRuntimeProjectionAllowed": False,
        },
        preview={
            "surfaceIntent": profile.get("surfaceIntent", {}).get(surface),
            "tokenOverrides": adapter.get("tokenOverrides", {}),
        },
    )


def export_preview_component(
    component_id: str,
    *,
    profile_id: str,
    surface: str = "shared-ui",
    model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = model or load_model()
    _surface(model, surface)
    profile = _profile(model, profile_id)
    registry = model["exportRegistry"]
    component = next(
        (item for item in registry.get("viewerComponents", []) if item["id"] == component_id),
        None,
    )
    if not component:
        raise KeyError(f"Unknown preview component: {component_id}")
    tokens = merge_tokens(model, profile_id, surface)
    exact = {token_id: tokens[token_id] for token_id in component["tokenRefs"]}
    target = _target(model, surface, component_ui_id=component_id)
    target["bindingStatus"] = component.get(
        "productBindingStatus",
        "BLOCKED_BY_MISSING_BINDING",
    )
    return _base(
        kind="preview-component-recipe",
        profile=profile,
        recipe_preset_id=component["recipePresetId"],
        neutral_meaning_id=component["neutralMeaningId"],
        object_id=component["id"],
        component_ui_id=component["id"],
        target=target,
        values={
            "componentName": component["name"],
            "tokenRefs": component["tokenRefs"],
            "resolvedTokens": exact,
        },
        origin=_origin(
            "registries/portable-export.registry.json",
            "registries/portable-export.registry.json",
            profile_id,
        ),
        compatibility={
            "supportedSurfaces": [surface],
            "selectedSurface": surface,
            "surfaceRuntimeProjectionAllowed": False,
            "productBindingResolved": False,
        },
        preview={"resolvedTokens": exact},
    )


def write_artifact(path: Path, artifact: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_artifact(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))
