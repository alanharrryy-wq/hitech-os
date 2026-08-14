from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_sha256, read_json, write_json
from .recipes import RecipeRepository
from .repository import BridgeRepository

CORE_RUNTIME_ALIASES = ("tb", "pc", "mb")
REQUIRED_COMPONENT_COORDINATES = (
    "surfaceId",
    "routeId",
    "regionId",
    "slotId",
    "componentUiId",
    "ownerId",
    "adapterId",
)
REQUIRED_TARGET_FIELDS = (
    "styleSourceFile",
    "anchorKind",
    "anchorValue",
    "sourceHash",
)


def load_visual_family_crosswalk(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    payload = read_json(target)
    if payload.get("schema") != "prisma.visual-family-crosswalk.v1":
        raise ValueError("INVALID_VISUAL_FAMILY_CROSSWALK_SCHEMA")
    mappings = payload.get("governedMappings")
    if not isinstance(mappings, list):
        raise ValueError("INVALID_VISUAL_FAMILY_CROSSWALK_MAPPINGS")
    seen: set[str] = set()
    for row in mappings:
        if not isinstance(row, dict):
            raise ValueError("INVALID_VISUAL_FAMILY_MAPPING_ROW")
        widget = str(row.get("widgetTypeId") or "")
        if not widget or widget in seen:
            raise ValueError("DUPLICATE_OR_EMPTY_VISUAL_FAMILY_WIDGET:" + widget)
        for key in ("visualFamilyId", "familyKind", "recipeId", "basis"):
            if not row.get(key):
                raise ValueError(f"VISUAL_FAMILY_MAPPING_FIELD_MISSING:{widget}:{key}")
        seen.add(widget)
    return payload


def _mapping_index(crosswalk: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row["widgetTypeId"]): row
        for row in crosswalk.get("governedMappings", [])
        if isinstance(row, dict) and row.get("widgetTypeId")
    }


def _unique_components(repository: BridgeRepository) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for component in repository.components_by_id.values():
        if not isinstance(component, dict):
            continue
        key = str(component.get("componentUiId") or component.get("componentId") or "")
        if key:
            rows[key] = component
    return [rows[key] for key in sorted(rows)]


def _sha64(value: Any) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in text)


def _target_evidence(
    component: dict[str, Any],
    target: dict[str, Any],
    index: int,
) -> tuple[dict[str, Any], list[str]]:
    blockers: list[str] = []
    for field in REQUIRED_TARGET_FIELDS:
        if not target.get(field):
            blockers.append(f"VISUAL_TARGET_FIELD_MISSING:{index}:{field}")
    source_hash = str(target.get("sourceHash") or "")
    if source_hash and not _sha64(source_hash):
        blockers.append(f"VISUAL_TARGET_SOURCE_HASH_INVALID:{index}")

    style_source = str(target.get("styleSourceFile") or "")
    component_hashes = component.get("sourceHashes")
    component_hashes = component_hashes if isinstance(component_hashes, dict) else {}
    recorded_hash = str(component_hashes.get(style_source) or "")
    if recorded_hash and source_hash and recorded_hash.upper() != source_hash.upper():
        blockers.append(f"VISUAL_TARGET_SOURCE_HASH_DRIFT:{index}")

    stable = {
        "runtimeAlias": component.get("runtimeAlias"),
        "surfaceId": component.get("surfaceId"),
        "componentUiId": component.get("componentUiId"),
        "styleSourceFile": target.get("styleSourceFile"),
        "anchorKind": target.get("anchorKind"),
        "anchorValue": target.get("anchorValue"),
        "selector": target.get("selector"),
        "pseudoElement": target.get("pseudoElement"),
        "stateSelector": target.get("stateSelector"),
        "atRule": target.get("atRule"),
        "sourceHash": source_hash.upper() if source_hash else None,
    }
    digest = canonical_sha256(stable).upper()
    runtime = str(component.get("runtimeAlias") or "XX").upper()
    visual_layer_id = f"LYR.VIS.{runtime}.{digest[:20]}"
    implementation_layer_id = target.get("implementationLayerId") or f"ILYR.SRC.{runtime}.{digest[:20]}"
    row = {
        **stable,
        "visualTargetId": target.get("visualTargetId"),
        "targetRole": target.get("targetRole"),
        "visualLayerId": visual_layer_id,
        "implementationLayerId": implementation_layer_id,
        "implementationLayerIdSource": (
            "UIMAP_EXACT_SOURCE_RECORD"
            if target.get("implementationLayerId")
            else "DETERMINISTIC_EXACT_SOURCE_ANCHOR_ID"
        ),
        "evidenceDigest": digest,
        "status": "EXACT_SOURCE_BOUND" if not blockers else "BLOCKED_BY_SOURCE_EVIDENCE",
        "blockingReasons": sorted(set(blockers)),
    }
    return row, blockers


def _component_row(
    component: dict[str, Any],
    mapping_by_widget: dict[str, dict[str, Any]],
    recipes: RecipeRepository,
) -> dict[str, Any] | None:
    visual_targets = component.get("visualTargets")
    if not isinstance(visual_targets, list) or not visual_targets:
        return None

    blockers: list[str] = []
    missing_coordinates = [
        field for field in REQUIRED_COMPONENT_COORDINATES if not component.get(field)
    ]
    blockers.extend(f"COMPONENT_COORDINATE_MISSING:{field}" for field in missing_coordinates)

    target_rows = []
    for index, target in enumerate(visual_targets):
        if not isinstance(target, dict):
            blockers.append(f"VISUAL_TARGET_INVALID:{index}")
            continue
        row, target_blockers = _target_evidence(component, target, index)
        target_rows.append(row)
        blockers.extend(target_blockers)

    widget = str(component.get("widgetTypeId") or "")
    family = mapping_by_widget.get(widget)
    family_status = "BLOCKED_BY_UNMAPPED_VISUAL_FAMILY"
    recipe_status = "NOT_EVALUATED"
    recipe_id = None
    visual_family_id = None
    family_kind = None
    mapping_basis = None
    if family:
        recipe_id = str(family.get("recipeId") or "")
        visual_family_id = family.get("visualFamilyId")
        family_kind = family.get("familyKind")
        mapping_basis = family.get("basis")
        if recipe_id in recipes.by_id:
            family_status = "GOVERNED_VISUAL_FAMILY"
            recipe_status = "GOVERNED_RECIPE_AVAILABLE"
        else:
            family_status = "BLOCKED_BY_MISSING_GOVERNED_RECIPE"
            recipe_status = "RECIPE_NOT_FOUND"
            blockers.append(f"GOVERNED_RECIPE_NOT_FOUND:{recipe_id}")

    binding_stable = {
        "runtimeAlias": component.get("runtimeAlias"),
        "surfaceId": component.get("surfaceId"),
        "routeId": component.get("routeId"),
        "regionId": component.get("regionId"),
        "slotId": component.get("slotId"),
        "componentUiId": component.get("componentUiId"),
        "ownerId": component.get("ownerId"),
        "adapterId": component.get("adapterId"),
        "visualFamilyId": visual_family_id,
        "layerEvidence": [row.get("evidenceDigest") for row in target_rows],
    }
    binding_digest = canonical_sha256(binding_stable).upper()
    runtime = str(component.get("runtimeAlias") or "XX").upper()
    visual_binding_id = f"BND.VIS.{runtime}.{binding_digest[:20]}"
    source_resolved = bool(target_rows) and not any(
        reason.startswith("COMPONENT_COORDINATE_MISSING:")
        or reason.startswith("VISUAL_TARGET_")
        for reason in blockers
    )
    recipe_ready = source_resolved and family_status == "GOVERNED_VISUAL_FAMILY"

    return {
        "visualBindingId": visual_binding_id,
        "runtimeAlias": component.get("runtimeAlias"),
        "surfaceId": component.get("surfaceId"),
        "interfaceId": component.get("interfaceId"),
        "routeId": component.get("routeId"),
        "routePath": component.get("routePath"),
        "regionId": component.get("regionId"),
        "slotId": component.get("slotId"),
        "componentId": component.get("componentId"),
        "componentUiId": component.get("componentUiId"),
        "widgetTypeId": component.get("widgetTypeId"),
        "ownerId": component.get("ownerId"),
        "adapterId": component.get("adapterId"),
        "neutralMeaningId": component.get("neutralMeaningId"),
        "neutralMeaningBoundary": "PRESERVED_UNCHANGED_NOT_DERIVED_FROM_VISUAL_FAMILY",
        "visualFamilyId": visual_family_id,
        "familyKind": family_kind,
        "familyMappingBasis": mapping_basis,
        "familyStatus": family_status,
        "recipeId": recipe_id,
        "recipeStatus": recipe_status,
        "visualTargets": target_rows,
        "sourceResolvedVisualBinding": source_resolved,
        "visualRecipeProjectionReady": recipe_ready,
        "visualApplicationReadiness": (
            "READY_FOR_EXACT_VISUAL_AUTHORITY_PREFLIGHT"
            if recipe_ready
            else "BLOCKED_BY_VISUAL_AUTHORITY_GAP"
        ),
        "blockingReasons": sorted(set(blockers)),
        "sourceHashes": component.get("sourceHashes", {}),
        "evidenceRefs": component.get("evidenceRefs", []),
        "instructionOnly": True,
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
    }


def _edge_key(*parts: Any) -> str:
    return canonical_sha256([str(part or "") for part in parts]).upper()[:20]


def _visual_control_projection(rows: list[dict[str, Any]]) -> dict[str, Any]:
    surfaces: dict[str, dict[str, Any]] = {}
    for row in rows:
        runtime = str(row.get("runtimeAlias") or "unknown")
        surface = surfaces.setdefault(
            runtime,
            {
                "runtimeAlias": runtime,
                "routeOwnerEdges": {},
                "regionOwnerEdges": {},
                "editableSlotEdges": {},
                "layers": {},
            },
        )
        if not row.get("sourceResolvedVisualBinding"):
            continue
        route_id = row.get("routeId")
        region_id = row.get("regionId")
        slot_id = row.get("slotId")
        owner_id = row.get("ownerId")
        component_ui_id = row.get("componentUiId")
        binding_id = row.get("visualBindingId")
        rk = _edge_key(route_id, owner_id)
        surface["routeOwnerEdges"][rk] = {
            "routeId": route_id,
            "ownerId": owner_id,
            "evidence": "EXACT_UIMAP_COMPONENT_COORDINATES",
        }
        rgk = _edge_key(route_id, region_id, owner_id)
        surface["regionOwnerEdges"][rgk] = {
            "routeId": route_id,
            "regionId": region_id,
            "ownerId": owner_id,
            "evidence": "EXACT_UIMAP_COMPONENT_COORDINATES",
        }
        sk = _edge_key(route_id, region_id, slot_id, component_ui_id)
        surface["editableSlotEdges"][sk] = {
            "routeId": route_id,
            "regionId": region_id,
            "slotId": slot_id,
            "componentUiId": component_ui_id,
            "visualBindingId": binding_id,
            "evidence": "EXACT_UIMAP_COMPONENT_COORDINATES",
        }
        for target in row.get("visualTargets", []):
            layer_id = target.get("visualLayerId")
            if not layer_id:
                continue
            surface["layers"][str(layer_id)] = {
                "visualLayerId": layer_id,
                "visualBindingId": binding_id,
                "componentUiId": component_ui_id,
                "styleSourceFile": target.get("styleSourceFile"),
                "anchorKind": target.get("anchorKind"),
                "anchorValue": target.get("anchorValue"),
                "selector": target.get("selector"),
                "pseudoElement": target.get("pseudoElement"),
                "stateSelector": target.get("stateSelector"),
                "sourceHash": target.get("sourceHash"),
                "implementationLayerId": target.get("implementationLayerId"),
                "evidenceDigest": target.get("evidenceDigest"),
            }
    normalized = {}
    for runtime, surface in surfaces.items():
        normalized[runtime] = {
            "runtimeAlias": runtime,
            "routeOwnerEdges": sorted(surface["routeOwnerEdges"].values(), key=lambda x: (str(x.get("routeId")), str(x.get("ownerId")))),
            "regionOwnerEdges": sorted(surface["regionOwnerEdges"].values(), key=lambda x: (str(x.get("routeId")), str(x.get("regionId")), str(x.get("ownerId")))),
            "editableSlotEdges": sorted(surface["editableSlotEdges"].values(), key=lambda x: (str(x.get("routeId")), str(x.get("regionId")), str(x.get("slotId")), str(x.get("componentUiId")))),
            "layers": sorted(surface["layers"].values(), key=lambda x: str(x.get("visualLayerId"))),
        }
        normalized[runtime]["counts"] = {
            "routeOwnerEdges": len(normalized[runtime]["routeOwnerEdges"]),
            "regionOwnerEdges": len(normalized[runtime]["regionOwnerEdges"]),
            "editableSlotEdges": len(normalized[runtime]["editableSlotEdges"]),
            "layers": len(normalized[runtime]["layers"]),
        }
    return {
        "schema": "prisma.generated.visual-control-projection.v1",
        "schemaVersion": "1.0.0",
        "status": "SOURCE_READY_GENERATED_PROJECTION",
        "surfaces": normalized,
        "certifiesProductRuntime": False,
        "replacesCanonicalTabletVisualControl": False,
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
    }


def build_visual_family_mapping(
    repository: BridgeRepository,
    recipes: RecipeRepository,
    crosswalk: dict[str, Any],
    *,
    runtime_aliases: Iterable[str] = CORE_RUNTIME_ALIASES,
) -> tuple[dict[str, Any], dict[str, Any]]:
    requested = tuple(dict.fromkeys(str(value) for value in runtime_aliases))
    mapping_by_widget = _mapping_index(crosswalk)
    rows = []
    for component in _unique_components(repository):
        if component.get("runtimeAlias") not in requested:
            continue
        row = _component_row(component, mapping_by_widget, recipes)
        if row is not None:
            rows.append(row)
    rows.sort(key=lambda row: (str(row.get("runtimeAlias")), str(row.get("componentUiId"))))

    counts = {}
    for runtime in requested:
        subset = [row for row in rows if row.get("runtimeAlias") == runtime]
        counts[runtime] = {
            "visualCandidateCount": len(subset),
            "sourceResolvedVisualBindingCount": sum(1 for row in subset if row.get("sourceResolvedVisualBinding")),
            "governedVisualFamilyCount": sum(1 for row in subset if row.get("familyStatus") == "GOVERNED_VISUAL_FAMILY"),
            "visualRecipeProjectionReadyCount": sum(1 for row in subset if row.get("visualRecipeProjectionReady")),
            "unmappedVisualFamilyCount": sum(1 for row in subset if row.get("familyStatus") == "BLOCKED_BY_UNMAPPED_VISUAL_FAMILY"),
            "sourceEvidenceBlockedCount": sum(1 for row in subset if not row.get("sourceResolvedVisualBinding")),
        }

    report = {
        "schema": "prisma.visual-family-mapping-report.v1",
        "schemaVersion": "1.0.0",
        "status": "SOURCE_READY_WITH_EXPLICIT_FAMILY_GAPS",
        "runtimeAliases": list(requested),
        "meaningBoundary": crosswalk.get("meaningBoundary", {}),
        "crosswalkVersion": crosswalk.get("version"),
        "counts": counts,
        "totalVisualCandidateCount": len(rows),
        "totalSourceResolvedVisualBindingCount": sum(1 for row in rows if row.get("sourceResolvedVisualBinding")),
        "totalVisualRecipeProjectionReadyCount": sum(1 for row in rows if row.get("visualRecipeProjectionReady")),
        "rows": rows,
        "applicationEnabled": False,
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
    }
    control = _visual_control_projection(rows)
    return report, control


def write_visual_family_mapping(
    output_dir: str | Path,
    report: dict[str, Any],
    visual_control: dict[str, Any],
) -> list[str]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = [
        write_json(root / "PRISMA_VISUAL_FAMILY_MAPPING.json", report),
        write_json(root / "PRISMA_GENERATED_VISUAL_CONTROL_PROJECTION.json", visual_control),
    ]
    return [str(path) for path in paths]
