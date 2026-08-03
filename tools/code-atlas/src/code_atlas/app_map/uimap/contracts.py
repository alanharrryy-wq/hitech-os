from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.1.0"
TASK_ID = "MAP_ALL_PRISMA_UI_SURFACES_SOURCE_ONLY_V1"
CANONICALIZATION = "RFC8785-compatible-sorted-json-v1"

RUNTIME_ORDER = ("contract", "tb", "pc", "mb", "web", "cl", "cc", "cmd", "shared")
ACTIVE_RUNTIME_ALIASES = RUNTIME_ORDER[1:]

ADAPTERS = {
    "tb": "ADP.TB.TOUCH.V2",
    "pc": "ADP.PC.ADMIN.V2",
    "mb": "ADP.MB.TOUCH.V2",
    "web": "ADP.WEB.RESPONSIVE.V2",
    "cl": "ADP.CL.ANALYTIC.V2",
    "cc": "ADP.CC.OPERATIONS.V2",
    "cmd": "ADP.CMD.OPERATIONS.V2",
    "shared": "ADP.SHARED.NEUTRAL.V2",
}

REQUIRED_STATES = (
    "default", "hover", "focus", "focus-visible", "pressed", "disabled", "loading", "reduced-motion"
)
CONDITIONAL_STATES = ("success", "warning", "error")
STATE_VALUES = {
    "SOURCE_DEFINED", "OWNER_INHERITED", "NOT_APPLICABLE", "MISSING_REQUIRED", "NOT_EVALUATED"
}
RECIPE_COVERAGE = {
    "CURRENT_SOURCE_COVERAGE_COMPLETE",
    "FULL_VISUAL_STATE_RECIPE_COMPLETE",
    "PARTIAL_VISUAL_STATE_COVERAGE",
    "BLOCKED_BY_UNRESOLVED_VISUAL_STATE",
    "NOT_EVALUATED",
}
NDC_STATUSES = {
    "CANDIDATE", "INFERRED", "CONFIRMED", "CANONICAL_READY", "CONFLICT", "ORPHAN", "INTERNAL",
    "DEPRECATED", "NEEDS_REVIEW", "BLOCKED",
}
CONFIDENCE_VALUES = {"LOW", "MEDIUM", "HIGH", "VERY_HIGH", "BLOCKED"}
TARGET_RESOLUTION_STATUSES = {
    "UNMAPPED", "PARTIAL", "SOURCE_RESOLVED", "BLOCKED_BY_CONFLICT", "BLOCKED_BY_MISSING_SOURCE",
    "BLOCKED_BY_MISSING_OWNER", "BLOCKED_BY_MISSING_LAYER", "BLOCKED_BY_DRIFT", "NOT_APPLICABLE",
}
APPLICATION_READINESS = {"BLOCKED", "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT"}
ANCHOR_KINDS = {
    "CSS_SELECTOR", "CSS_MODULE_CLASS", "DATA_ATTRIBUTE", "COMPONENT_SYMBOL", "COMPONENT_PROP",
    "TOKEN_BINDING", "INLINE_STYLE_OBJECT", "STYLED_COMPONENT", "GENERATED_PROJECTION",
}
TARGET_ROLES = {
    "ROOT", "SCENE", "CHROME", "CONTENT", "CONTAINER", "CONTROL", "TEXT", "ICON", "BORDER",
    "BACKGROUND", "OVERLAY", "FEEDBACK", "PSEUDO_ELEMENT", "EFFECT", "STATE",
}
FINAL_STATUSES = {"PASS_SOURCE_MAP_COMPLETE", "PASS_SOURCE_MAP_WITH_EXPLICIT_GAPS", "FAIL_SOURCE_MAP"}

PROHIBITED_CANONICAL_KEYS = {
    "uiId", "elementId", "targetId", "semanticId", "mapsTo", "region", "path", "owner",
    "selectorPath", "mappingStatus", "ready", "COMPLETE",
}
RESERVED_ID_SEGMENTS = {"unknown", "undefined", "null", "temp", "tmp", "new", "old", "fix1", "fix2", "final_final"}

NDC_ID_PATTERN = r"^[A-Z][A-Z0-9_]*\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"
COMPONENT_UI_ID_PATTERN = r"^[A-Z0-9]+(?:-[A-Z0-9]+){4,}-[0-9]{2}$"
BINDING_ID_PATTERN = r"^BND\.[A-Z0-9_]+(?:\.[A-Z0-9_]+)*\.V[0-9]+$"
LAYER_ID_PATTERN = r"^LYR\.[A-Z0-9_]+(?:\.[A-Z0-9_]+)+$"
ADAPTER_ID_PATTERN = r"^ADP\.[A-Z0-9_]+(?:\.[A-Z0-9_]+)*\.V[0-9]+$"
IMPLEMENTATION_LAYER_PATTERN = r"^[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+$"
SHA256_PATTERN = r"^[A-F0-9]{64}$"
RELATIVE_SOURCE_PATTERN = r"^(?![A-Za-z]:[\\/])(?!\\\\)(?!/)(?!.*(?:^|/)\.\.(?:/|$)).+$"
PERCENT_PATTERN = r"^(?:100(?:\.0{6})?|[0-9]{1,2}\.[0-9]{6})%$"

CANONICAL_TERMS = {
    "runtimeAlias": "Runtime owner alias",
    "surfaceId": "NDC SURF.* surface",
    "interfaceId": "IFC.* product interface",
    "routeId": "Stable ROUTE.* identity",
    "routePath": "Real URL or application path",
    "regionId": "Functional ZONE.* region",
    "slotId": "Exact governed SLOT.* slot",
    "componentId": "WGT.* projection identity",
    "componentUiId": "Specific UI locator",
    "widgetTypeId": "Neutral WID.* type",
    "neutralMeaningId": "Primary NDC meaning",
    "relatedNeutralIds": "Related ENT/EVT/ACT/STA/MET/EVD/CAP identities",
    "ownerId": "Canonical source owner",
    "ownerFile": "Project-relative owner file",
    "ownerSymbol": "Owning export or symbol",
    "renderSourceFile": "Project-relative render source",
    "renderSymbol": "Rendering symbol",
    "visualTargets": "Exact style targets",
    "bindingId": "Governed visual binding",
    "layerId": "Neutral visual layer",
    "implementationLayerId": "Physical layer implementation",
    "adapterId": "Surface adapter",
    "recipeCompatibility": "Recipe compatibility and state coverage",
    "stateSupport": "Source state support",
    "evidenceRefs": "Evidence references",
    "sourceHashes": "Governing source hashes",
    "ndcStatus": "NDC classification",
    "confidence": "NDC confidence",
    "targetResolutionStatus": "Exact target resolution",
    "applicationReadiness": "Future preflight eligibility",
    "blockingReasons": "Explicit blockers",
}

RECORD_REQUIRED_FIELDS = tuple(CANONICAL_TERMS.keys()) + (
    "schema", "schemaVersion", "instancePolicy", "projectionOfComponentId", "legacyIdPreserved",
)

FULL_CHAIN_FIELDS = (
    "surfaceId", "interfaceId", "routeId", "routePath", "regionId", "slotId", "componentId",
    "componentUiId", "widgetTypeId", "ownerId", "ownerFile", "ownerSymbol", "renderSourceFile",
    "renderSymbol", "visualTargets", "bindingId", "layerId", "implementationLayerId", "adapterId",
    "evidenceRefs", "sourceHashes",
)

CANONICAL_ID_PATTERNS = {
    "surfaceId": re.compile(r"^SURF\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"),
    "interfaceId": re.compile(r"^IFC\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"),
    "routeId": re.compile(r"^ROUTE\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"),
    "regionId": re.compile(r"^ZONE\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"),
    "slotId": re.compile(r"^SLOT\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"),
    "componentId": re.compile(r"^WGT\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"),
    "componentUiId": re.compile(COMPONENT_UI_ID_PATTERN),
    "widgetTypeId": re.compile(r"^WID\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"),
    "ownerId": re.compile(r"^OWN\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"),
    "bindingId": re.compile(BINDING_ID_PATTERN),
    "layerId": re.compile(LAYER_ID_PATTERN),
    "implementationLayerId": re.compile(IMPLEMENTATION_LAYER_PATTERN),
    "adapterId": re.compile(ADAPTER_ID_PATTERN),
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def add_integrity(payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)
    integrity = dict(data.get("integrity") or {})
    integrity.pop("canonicalPayloadSha256", None)
    data["integrity"] = integrity
    digest = sha256_bytes(canonical_bytes(data))
    integrity.update({
        "algorithm": "SHA-256",
        "canonicalization": CANONICALIZATION,
        "canonicalPayloadSha256": digest,
    })
    data["integrity"] = integrity
    return data


def slug(value: str, fallback: str = "item") -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value or "")
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    value = re.sub(r"_+", "_", value)
    if not value:
        return fallback
    parts = ["reserved" if part in RESERVED_ID_SEGMENTS else part for part in value.split("_")]
    value = "_".join(parts)
    return value or fallback


def upper_token(value: str, fallback: str = "ITEM", max_len: int = 28) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "-", value or "").strip("-").upper()
    token = re.sub(r"-+", "-", token)
    if not token:
        token = fallback
    parts = ["ITEM" if part.lower() in RESERVED_ID_SEGMENTS else part for part in token.split("-")]
    token = "-".join(parts)
    return token[:max_len].rstrip("-") or fallback


def stable_id(prefix: str, *segments: str) -> str:
    return ".".join([prefix.upper(), *[slug(s) for s in segments if s is not None and str(s).strip()]])


def contains_reserved_segment(identifier: str) -> bool:
    parts = re.split(r"[.\-_/]+", str(identifier).lower())
    return any(part in RESERVED_ID_SEGMENTS for part in parts)


def is_absolute_file_path(value: str) -> bool:
    value = str(value or "")
    if re.match(r"^[A-Za-z]:[\\/]", value):
        return True
    if value.startswith("\\\\") or value.startswith("/"):
        return True
    return False


def is_relative_source_path(value: str) -> bool:
    value = str(value or "")
    if not value or is_absolute_file_path(value) or "\\" in value:
        return False
    return ".." not in Path(value).parts


def iter_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from iter_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_keys(child)


def validate_identity_contract(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field, pattern in CANONICAL_ID_PATTERNS.items():
        value = record.get(field)
        if value is None:
            if field in {"bindingId", "layerId", "implementationLayerId"}:
                continue
            errors.append(f"missing_identity:{field}")
            continue
        if not pattern.fullmatch(str(value)):
            errors.append(f"invalid_id_grammar:{field}")
    route_path = record.get("routePath")
    if not isinstance(route_path, str) or not route_path.startswith("/"):
        errors.append("invalid_routePath")
    for field in ("ownerFile", "renderSourceFile"):
        value = record.get(field)
        if not is_relative_source_path(str(value or "")):
            errors.append(f"invalid_relative_path:{field}")
    for neutral in [record.get("neutralMeaningId"), *(record.get("relatedNeutralIds") or [])]:
        if neutral is not None and not re.fullmatch(NDC_ID_PATTERN, str(neutral)):
            errors.append("invalid_neutral_id")
    return sorted(set(errors))


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in RECORD_REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing_required_field:{field}")
    bad_keys = sorted(set(iter_keys(record)) & PROHIBITED_CANONICAL_KEYS)
    if bad_keys:
        errors.append("prohibited_keys:" + ",".join(bad_keys))
    if record.get("runtimeAlias") not in ACTIVE_RUNTIME_ALIASES:
        errors.append("invalid_runtimeAlias")
    if record.get("adapterId") not in set(ADAPTERS.values()):
        errors.append("invalid_adapterId")
    if record.get("ndcStatus") not in NDC_STATUSES:
        errors.append("invalid_ndcStatus")
    if record.get("confidence") not in CONFIDENCE_VALUES:
        errors.append("invalid_confidence")
    if record.get("targetResolutionStatus") not in TARGET_RESOLUTION_STATUSES:
        errors.append("invalid_targetResolutionStatus")
    if record.get("applicationReadiness") not in APPLICATION_READINESS:
        errors.append("invalid_applicationReadiness")

    errors.extend(validate_identity_contract(record))

    state_support = record.get("stateSupport") or {}
    for state in REQUIRED_STATES + CONDITIONAL_STATES:
        if state not in state_support:
            errors.append(f"missing_state:{state}")
        elif state_support[state] not in STATE_VALUES:
            errors.append(f"invalid_state:{state}")
    rc = record.get("recipeCompatibility") or {}
    if rc.get("coverageStatus") not in RECIPE_COVERAGE:
        errors.append("invalid_recipe_coverage")
    if rc.get("hoverPolicy") not in {"substitute-pressed", "native-hover"}:
        errors.append("invalid_hoverPolicy")

    for target in record.get("visualTargets") or []:
        if target.get("anchorKind") not in ANCHOR_KINDS:
            errors.append("invalid_anchorKind")
        if target.get("targetRole") not in TARGET_ROLES:
            errors.append("invalid_targetRole")
        if not is_relative_source_path(str(target.get("styleSourceFile") or "")):
            errors.append("invalid_relative_path:styleSourceFile")
        if not re.fullmatch(SHA256_PATTERN, str(target.get("sourceHash") or "")):
            errors.append("invalid_target_sourceHash")
        if target.get("anchorKind") == "GENERATED_PROJECTION" and target.get("patchPolicy") != "DO_NOT_PATCH_GENERATED":
            errors.append("generated_projection_missing_patch_policy")

    for key, value in (record.get("sourceHashes") or {}).items():
        if not isinstance(key, str) or not re.fullmatch(SHA256_PATTERN, str(value or "")):
            errors.append("invalid_sourceHashes")
            break

    if record.get("targetResolutionStatus") == "SOURCE_RESOLVED":
        for field in FULL_CHAIN_FIELDS:
            value = record.get(field)
            if value is None or value == "" or value == [] or value == {}:
                errors.append(f"source_resolved_missing:{field}")
        if record.get("ndcStatus") not in {"CONFIRMED", "CANONICAL_READY"}:
            errors.append("source_resolved_bad_ndc_status")
        if record.get("confidence") not in {"HIGH", "VERY_HIGH"}:
            errors.append("source_resolved_bad_confidence")
        if record.get("blockingReasons"):
            errors.append("source_resolved_has_blockers")
        if validate_identity_contract(record):
            errors.append("source_resolved_identity_contract_invalid")
    if record.get("applicationReadiness") == "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT":
        if record.get("targetResolutionStatus") != "SOURCE_RESOLVED" or record.get("blockingReasons"):
            errors.append("eligible_without_source_resolution")

    id_fields = tuple(CANONICAL_ID_PATTERNS)
    for field in id_fields:
        value = record.get(field)
        if value and contains_reserved_segment(str(value)):
            errors.append(f"reserved_id_segment:{field}")
    return sorted(set(errors))


def nullable(schema: dict[str, Any]) -> dict[str, Any]:
    return {"anyOf": [schema, {"type": "null"}]}


def integrity_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": ["algorithm", "canonicalization", "canonicalPayloadSha256"],
        "properties": {
            "algorithm": {"const": "SHA-256"},
            "canonicalization": {"const": CANONICALIZATION},
            "canonicalPayloadSha256": {"type": "string", "pattern": SHA256_PATTERN},
        },
        "additionalProperties": False,
    }


def state_support_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": list(REQUIRED_STATES + CONDITIONAL_STATES),
        "properties": {
            state: {"enum": sorted(STATE_VALUES)}
            for state in REQUIRED_STATES + CONDITIONAL_STATES
        },
        "additionalProperties": False,
    }


def visual_target_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": [
            "visualTargetId", "targetRole", "styleSourceFile", "anchorKind", "anchorValue",
            "selector", "pseudoElement", "stateSelector", "atRule", "implementationLayerId", "sourceHash",
        ],
        "properties": {
            "visualTargetId": {"type": "string", "pattern": r"^VTR\.[A-Z0-9_.-]+$"},
            "targetRole": {"enum": sorted(TARGET_ROLES)},
            "styleSourceFile": {"type": "string", "minLength": 1, "pattern": RELATIVE_SOURCE_PATTERN},
            "anchorKind": {"enum": sorted(ANCHOR_KINDS)},
            "anchorValue": {"type": "string", "minLength": 1},
            "selector": {"type": "string", "minLength": 1},
            "pseudoElement": nullable({"type": "string", "enum": ["::before", "::after"]}),
            "stateSelector": {"enum": list(REQUIRED_STATES + CONDITIONAL_STATES)},
            "atRule": nullable({"type": "string"}),
            "implementationLayerId": nullable({"type": "string", "pattern": IMPLEMENTATION_LAYER_PATTERN}),
            "sourceHash": {"type": "string", "pattern": SHA256_PATTERN},
            "patchPolicy": {"enum": ["DO_NOT_PATCH_GENERATED"]},
        },
        "additionalProperties": False,
    }


def record_schema() -> dict[str, Any]:
    properties: dict[str, Any] = {
        "schema": {"const": "prisma.ui.component-record.v1"},
        "schemaVersion": {"const": SCHEMA_VERSION},
        "runtimeAlias": {"enum": list(ACTIVE_RUNTIME_ALIASES)},
        "surfaceId": {"type": "string", "pattern": r"^SURF\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"},
        "interfaceId": {"type": "string", "pattern": r"^IFC\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"},
        "routeId": {"type": "string", "pattern": r"^ROUTE\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"},
        "routePath": {"type": "string", "pattern": r"^/.*$"},
        "regionId": {"type": "string", "pattern": r"^ZONE\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"},
        "slotId": {"type": "string", "pattern": r"^SLOT\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"},
        "componentId": {"type": "string", "pattern": r"^WGT\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"},
        "componentUiId": {"type": "string", "pattern": COMPONENT_UI_ID_PATTERN},
        "widgetTypeId": {"type": "string", "pattern": r"^WID\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"},
        "neutralMeaningId": nullable({"type": "string", "pattern": NDC_ID_PATTERN}),
        "relatedNeutralIds": {"type": "array", "items": {"type": "string", "pattern": NDC_ID_PATTERN}},
        "ownerId": {"type": "string", "pattern": r"^OWN\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"},
        "ownerFile": {"type": "string", "minLength": 1, "pattern": RELATIVE_SOURCE_PATTERN},
        "ownerSymbol": {"type": "string", "minLength": 1},
        "renderSourceFile": {"type": "string", "minLength": 1, "pattern": RELATIVE_SOURCE_PATTERN},
        "renderSymbol": {"type": "string", "minLength": 1},
        "visualTargets": {"type": "array", "items": visual_target_schema()},
        "bindingId": nullable({"type": "string", "pattern": BINDING_ID_PATTERN}),
        "layerId": nullable({"type": "string", "pattern": LAYER_ID_PATTERN}),
        "implementationLayerId": nullable({"type": "string", "pattern": IMPLEMENTATION_LAYER_PATTERN}),
        "adapterId": {"enum": sorted(ADAPTERS.values())},
        "recipeCompatibility": {
            "type": "object",
            "required": ["coverageStatus", "compatibleRecipeIds", "hoverPolicy"],
            "properties": {
                "coverageStatus": {"enum": sorted(RECIPE_COVERAGE)},
                "compatibleRecipeIds": {"type": "array", "items": {"type": "string", "minLength": 1}},
                "hoverPolicy": {"enum": ["substitute-pressed", "native-hover"]},
            },
            "additionalProperties": False,
        },
        "stateSupport": state_support_schema(),
        "evidenceRefs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["evidenceType", "sourceFile"],
                "properties": {
                    "evidenceType": {"type": "string", "minLength": 1},
                    "sourceFile": {"type": "string", "minLength": 1},
                    "sourceHash": {"type": "string", "pattern": SHA256_PATTERN},
                    "selector": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "sourceHashes": {
            "type": "object",
            "additionalProperties": {"type": "string", "pattern": SHA256_PATTERN},
        },
        "ndcStatus": {"enum": sorted(NDC_STATUSES)},
        "confidence": {"enum": sorted(CONFIDENCE_VALUES)},
        "targetResolutionStatus": {"enum": sorted(TARGET_RESOLUTION_STATUSES)},
        "applicationReadiness": {"enum": sorted(APPLICATION_READINESS)},
        "blockingReasons": {"type": "array", "items": {"type": "string", "minLength": 1}},
        "instancePolicy": {"enum": ["SINGLE_OR_STATIC", "REPEATED_BY_DATA"]},
        "projectionOfComponentId": nullable({"type": "string", "pattern": r"^WGT\.[a-z0-9_]+(?:\.[a-z0-9_]+)*$"}),
        "legacyIdPreserved": {"type": "boolean"},
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://prisma.local/schemas/PRISMA_UI_COMPONENT_RECORD_V1.schema.json",
        "title": "PRISMA UI Component Record V1",
        "type": "object",
        "required": list(RECORD_REQUIRED_FIELDS),
        "properties": properties,
        "additionalProperties": False,
    }


def coverage_metric_schema() -> dict[str, Any]:
    count_fields = [
        "discoveredRoutes", "mappedRoutes", "eligibleComponents", "identifiedComponents",
        "sourceResolvedComponents", "partialComponents", "unmappedComponents", "conflictComponents",
        "orphanComponents", "layerResolvedComponents", "neutralMeaningResolvedComponents",
        "recipeCompatibleComponents", "deprecatedComponents",
    ]
    ratio_fields = [
        "routeCoverage", "identificationCoverage", "sourceResolutionCoverage", "layerCoverage",
        "neutralMeaningCoverage", "recipeCompatibilityCoverage",
    ]
    return {
        "type": "object",
        "required": count_fields + ratio_fields + ["runtimeDisposition"],
        "properties": {
            "runtimeDisposition": {
                "enum": [
                    "ACTIVE_AGGREGATE",
                    "ACTIVE_SOURCE_DISCOVERY",
                    "BLOCKED_BY_MISSING_ROUTE_REGISTRY",
                    "INTERNAL_NO_ROUTE_REGISTRY",
                    "SKIPPED_OFFLINE",
                ]
            },
            **{field: {"type": "integer", "minimum": 0} for field in count_fields},
            **{
                field: {"anyOf": [
                    {"type": "string", "pattern": PERCENT_PATTERN},
                    {"const": "NOT_EVALUATED"},
                ]}
                for field in ratio_fields
            },
        },
        "additionalProperties": False,
    }


def atlas_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://prisma.local/schemas/PRISMA_UI_COMPONENT_ATLAS_V1.schema.json",
        "title": "PRISMA UI Component Atlas V1",
        "type": "object",
        "required": [
            "schema", "schemaVersion", "taskId", "generatedAt", "contractHash",
            "sourceSnapshotHash", "components", "coverage", "authorityMeshHash", "integrity",
        ],
        "properties": {
            "schema": {"const": "prisma.ui.component-atlas.v1"},
            "schemaVersion": {"const": SCHEMA_VERSION},
            "taskId": {"const": TASK_ID},
            "generatedAt": {"type": "string", "minLength": 20},
            "contractHash": {"type": "string", "pattern": SHA256_PATTERN},
            "sourceSnapshotHash": {"type": "string", "pattern": SHA256_PATTERN},
            "components": {"type": "array", "items": record_schema()},
            "coverage": {
                "type": "object",
                "required": ["global", "byRuntime"],
                "properties": {
                    "global": coverage_metric_schema(),
                    "byRuntime": {
                        "type": "object",
                        "required": list(ACTIVE_RUNTIME_ALIASES),
                        "properties": {
                            alias: coverage_metric_schema() for alias in ACTIVE_RUNTIME_ALIASES
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
            "authorityMeshHash": {"type": "string", "pattern": SHA256_PATTERN},
            "integrity": integrity_schema(),
        },
        "additionalProperties": False,
    }


def handoff_schema() -> dict[str, Any]:
    blocked_schema = {
        "type": "object",
        "required": ["componentUiId", "targetResolutionStatus", "blockingReasons"],
        "properties": {
            "componentUiId": {"type": "string", "pattern": COMPONENT_UI_ID_PATTERN},
            "targetResolutionStatus": {"enum": sorted(TARGET_RESOLUTION_STATUSES)},
            "blockingReasons": {"type": "array", "items": {"type": "string"}},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://prisma.local/schemas/PRISMA_UI_BRIDGE_HANDOFF_V1.schema.json",
        "title": "PRISMA UI Bridge Handoff V1",
        "type": "object",
        "required": [
            "schema", "schemaVersion", "generatedAt", "contractHash", "sourceSnapshotHash",
            "eligibleComponents", "blockedComponents", "gateReminder", "integrity",
        ],
        "properties": {
            "schema": {"const": "prisma.ui.bridge-handoff.v1"},
            "schemaVersion": {"const": SCHEMA_VERSION},
            "generatedAt": {"type": "string", "minLength": 20},
            "contractHash": {"type": "string", "pattern": SHA256_PATTERN},
            "sourceSnapshotHash": {"type": "string", "pattern": SHA256_PATTERN},
            "eligibleComponents": {"type": "array", "items": record_schema()},
            "blockedComponents": {"type": "array", "items": blocked_schema},
            "gateReminder": {"type": "array", "minItems": 8, "items": {"type": "string"}},
            "integrity": integrity_schema(),
        },
        "additionalProperties": False,
    }


def validate_schema_subset(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate the JSON-Schema subset emitted by UIMAP without adding dependencies."""
    errors: list[str] = []

    if "$ref" in schema:
        return errors

    if "anyOf" in schema:
        branches = [validate_schema_subset(value, branch, path) for branch in schema["anyOf"]]
        if all(branch for branch in branches):
            errors.append(f"{path}:anyOf")
        return errors

    expected = schema.get("type")
    if expected:
        type_ok = {
            "object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, str),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "boolean": isinstance(value, bool),
            "null": value is None,
        }.get(expected, True)
        if not type_ok:
            return [f"{path}:type:{expected}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}:const")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}:enum")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}:minLength")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            errors.append(f"{path}:pattern")
    if isinstance(value, int) and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{path}:minimum")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}:minItems")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_schema_subset(item, item_schema, f"{path}[{index}]"))
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}:required:{key}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in properties:
                errors.extend(validate_schema_subset(item, properties[key], f"{path}.{key}"))
            elif additional is False:
                errors.append(f"{path}:additional:{key}")
            elif isinstance(additional, dict):
                errors.extend(validate_schema_subset(item, additional, f"{path}.{key}"))
    return errors
