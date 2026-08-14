from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_sha256, write_json
from .planner import build_plan
from .recipes import RecipeRepository
from .repository import BridgeRepository
from .resolver import resolve_component

SURFACE_TO_RUNTIME = {
    "tablet": "tb",
    "pc": "pc",
    "mobile": "mb",
}
RUNTIME_TO_SURFACE = {value: key for key, value in SURFACE_TO_RUNTIME.items()}
TRACE_FIELDS = (
    "surfaceId",
    "interfaceId",
    "routeId",
    "routePath",
    "regionId",
    "slotId",
    "componentId",
    "componentUiId",
    "ownerId",
    "ownerFile",
    "ownerSymbol",
    "renderSourceFile",
    "renderSymbol",
    "bindingId",
    "layerId",
    "implementationLayerId",
    "adapterId",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _component_key(component: dict[str, Any]) -> str:
    return str(component.get("componentUiId") or component.get("componentId") or canonical_sha256(component))


def _iter_components(repository: BridgeRepository) -> list[dict[str, Any]]:
    """Return canonical component records once; later corrective batches win."""
    by_key: dict[str, dict[str, Any]] = {}
    for batch in repository.batches:
        for component in batch.get("components", []):
            if not isinstance(component, dict):
                continue
            by_key[_component_key(component)] = component
    return [by_key[key] for key in sorted(by_key)]


def _trace(component: dict[str, Any]) -> dict[str, Any]:
    return {field: component.get(field) for field in TRACE_FIELDS}


def _missing_trace(component: dict[str, Any]) -> list[str]:
    return [field for field in TRACE_FIELDS if component.get(field) in (None, "", [], {})]


def _load_json_object(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _authority_snapshot(governor_root: str | Path) -> dict[str, Any]:
    root = Path(governor_root)
    adapter_rel = "extras/atlasfin/assets/data/surface-adapter.registry.json"
    bindings_rel = "authority/rifat/identity/registries/bindings.registry.json"
    element_bindings_rel = "authority/rifat/identity/registries/element-bindings.registry.json"
    atlas_reference_rel = "extras/atlasfin/assets/data/visual.recipe.registry.json"
    adapter_path = root / adapter_rel
    bindings_path = root / bindings_rel
    element_bindings_path = root / element_bindings_rel
    atlas_reference_path = root / atlas_reference_rel

    adapters = _load_json_object(adapter_path)
    bindings = _load_json_object(bindings_path)
    element_bindings = _load_json_object(element_bindings_path)
    atlas_reference = _load_json_object(atlas_reference_path)

    issues: list[str] = []
    if adapters is None:
        issues.append("MISSING_OR_INVALID_SURFACE_ADAPTER_REGISTRY")
        adapters = {}
    elif adapters.get("schema") != "PRISMA_SURFACE_ADAPTER_REGISTRY_V2":
        issues.append("SURFACE_ADAPTER_REGISTRY_SCHEMA_MISMATCH")

    if bindings is None:
        issues.append("MISSING_OR_INVALID_STATIC_BINDING_REGISTRY")
        bindings = {}
    elif bindings.get("schema") != "prisma.identity.bindings.registry.v1":
        issues.append("STATIC_BINDING_REGISTRY_SCHEMA_MISMATCH")

    if element_bindings is None:
        issues.append("MISSING_OR_INVALID_ELEMENT_BINDING_REGISTRY")
        element_bindings = {}
    elif element_bindings.get("schema") != "prisma.identity.element-bindings.registry.v1":
        issues.append("ELEMENT_BINDING_REGISTRY_SCHEMA_MISMATCH")
    else:
        if element_bindings.get("instructionOnly") is not True:
            issues.append("ELEMENT_BINDING_REGISTRY_NOT_INSTRUCTION_ONLY")
        if element_bindings.get("runtimeMutationAllowed") is not False:
            issues.append("ELEMENT_BINDING_REGISTRY_RUNTIME_MUTATION_NOT_DISABLED")
        if element_bindings.get("productApplicationAllowed") is not False:
            issues.append("ELEMENT_BINDING_REGISTRY_PRODUCT_APPLICATION_NOT_DISABLED")

    if atlas_reference is None:
        issues.append("MISSING_OR_INVALID_ATLASFIN_VISUAL_REFERENCE")
        atlas_reference = {}
    elif (atlas_reference.get("capabilities") or {}).get("directProductMutation") is not False:
        issues.append("ATLASFIN_REFERENCE_DIRECT_PRODUCT_MUTATION_NOT_DISABLED")

    adapter_ids = {
        str(item.get("id"))
        for item in adapters.get("items", [])
        if isinstance(item, dict) and item.get("id")
    }
    surface_binding_rows = {
        str(item.get("surface")): item
        for item in bindings.get("bindings", [])
        if isinstance(item, dict) and item.get("surface")
    }
    binding_status_counts = Counter(
        str(item.get("status", "UNKNOWN"))
        for item in element_bindings.get("bindings", [])
        if isinstance(item, dict)
    )
    atlas_target_status_counts = Counter()
    atlas_elements = atlas_reference.get("elements", [])
    for element in atlas_elements if isinstance(atlas_elements, list) else []:
        if not isinstance(element, dict):
            continue
        for target in element.get("target_bindings", []):
            if isinstance(target, dict):
                atlas_target_status_counts[str(target.get("status", "UNKNOWN"))] += 1

    required_adapter_ids = {
        "tablet": "ADP.TB.TOUCH.V2",
        "pc": "ADP.PC.ADMIN.V2",
        "mobile": "ADP.MB.TOUCH.V2",
    }
    adapter_checks = {
        surface: {
            "adapterId": adapter_id,
            "present": adapter_id in adapter_ids,
        }
        for surface, adapter_id in required_adapter_ids.items()
    }
    for surface in required_adapter_ids:
        if surface not in surface_binding_rows:
            issues.append(f"MISSING_STATIC_SURFACE_BINDING_ROW:{surface}")

    return {
        "status": "PASS" if not issues else "BLOCKED",
        "issues": sorted(set(issues)),
        "adapterRegistry": {
            "path": adapter_rel,
            "exists": adapter_path.is_file(),
            "sha256": _sha256_file(adapter_path),
            "schema": adapters.get("schema"),
            "version": adapters.get("version"),
            "adapterCount": len(adapter_ids),
            "requiredSurfaceAdapters": adapter_checks,
        },
        "staticBindingRegistry": {
            "path": bindings_rel,
            "exists": bindings_path.is_file(),
            "sha256": _sha256_file(bindings_path),
            "schema": bindings.get("schema"),
            "version": bindings.get("version"),
            "surfaces": {
                surface: {
                    "readiness": row.get("readiness"),
                    "missing": row.get("missing", []),
                    "runtimeProjectionAllowed": row.get("runtimeProjectionAllowed"),
                }
                for surface, row in sorted(surface_binding_rows.items())
            },
        },
        "elementBindingRegistry": {
            "path": element_bindings_rel,
            "exists": element_bindings_path.is_file(),
            "sha256": _sha256_file(element_bindings_path),
            "schema": element_bindings.get("schema"),
            "version": element_bindings.get("version"),
            "status": element_bindings.get("status"),
            "bindingCount": len(element_bindings.get("bindings", [])),
            "statusCounts": dict(sorted(binding_status_counts.items())),
            "instructionOnly": element_bindings.get("instructionOnly"),
            "runtimeMutationAllowed": element_bindings.get("runtimeMutationAllowed"),
            "productApplicationAllowed": element_bindings.get("productApplicationAllowed"),
        },
        "atlasfinReference": {
            "path": atlas_reference_rel,
            "exists": atlas_reference_path.is_file(),
            "sha256": _sha256_file(atlas_reference_path),
            "version": (atlas_reference.get("bundle") or {}).get("version"),
            "elementCount": len(atlas_elements) if isinstance(atlas_elements, list) else 0,
            "targetBindingStatusCounts": dict(sorted(atlas_target_status_counts.items())),
            "directProductMutation": (atlas_reference.get("capabilities") or {}).get("directProductMutation"),
        },
    }


def _component_projection(
    repository: BridgeRepository,
    recipes: RecipeRepository,
    component: dict[str, Any],
    product_root: str,
    governor_root: str,
) -> dict[str, Any]:
    ref = _component_key(component)
    resolution = resolve_component(repository, recipes, ref, product_root, governor_root)
    compatible = recipes.compatible(component)
    missing_trace = _missing_trace(component)
    plan_rows: list[dict[str, Any]] = []

    for recipe in compatible:
        recipe_id = str(recipe.get("recipeId"))
        plan, semantic_diff = build_plan(
            repository,
            recipes,
            ref,
            product_root,
            governor_root,
            recipe_id,
        )
        plan_rows.append(
            {
                "recipeId": recipe_id,
                "planId": plan.get("planId"),
                "status": plan.get("status"),
                "blockingReasons": plan.get("blockingReasons", []),
                "operationCount": len(plan.get("operations", [])),
                "semanticDiffChecksum": semantic_diff.get("checksum"),
                "sourceMutationPerformed": semantic_diff.get("sourceMutationPerformed"),
                "applicationEnabled": plan.get("applicationEnabled"),
            }
        )

    clean_plans = [row for row in plan_rows if row.get("status") == "PLAN_READY_FOR_REVIEW"]
    exact_trace = not missing_trace and component.get("targetResolutionStatus") == "SOURCE_RESOLVED"
    resolution_ready = resolution.get("status") == "ELIGIBLE_FOR_READ_ONLY_PLAN"

    if exact_trace and resolution_ready and clean_plans:
        status = "READY_FOR_EXACT_TARGET_AUTHORITY_PREFLIGHT"
    elif exact_trace and resolution_ready:
        status = "SOURCE_RESOLVED_NO_PLANABLE_RECIPE"
    elif exact_trace:
        status = "SOURCE_RESOLVED_WITH_EXPLICIT_BLOCKERS"
    else:
        status = "BLOCKED_BY_INCOMPLETE_EXACT_MAPPING"

    blockers = sorted(
        set(
            list(component.get("blockingReasons") or [])
            + list(resolution.get("blockingReasons") or [])
            + [f"MISSING_TRACE:{field}" for field in missing_trace]
            + [
                f"PLAN:{reason}"
                for row in plan_rows
                for reason in row.get("blockingReasons", [])
            ]
        )
    )

    return {
        "componentId": component.get("componentId"),
        "componentUiId": component.get("componentUiId"),
        "runtimeAlias": component.get("runtimeAlias"),
        "surface": RUNTIME_TO_SURFACE.get(str(component.get("runtimeAlias"))),
        "status": status,
        "exactTraceComplete": exact_trace,
        "trace": _trace(component),
        "neutralMeaningId": component.get("neutralMeaningId"),
        "relatedNeutralIds": component.get("relatedNeutralIds", []),
        "ndcStatus": component.get("ndcStatus"),
        "confidence": component.get("confidence"),
        "targetResolutionStatus": component.get("targetResolutionStatus"),
        "applicationReadiness": component.get("applicationReadiness"),
        "sourceHashes": component.get("sourceHashes", {}),
        "visualTargets": component.get("visualTargets", []),
        "recipeCompatibility": component.get("recipeCompatibility"),
        "compatibleRecipeIds": [str(item.get("recipeId")) for item in compatible],
        "plans": plan_rows,
        "blockingReasons": blockers,
    }


def build_projection_map(
    repository: BridgeRepository,
    recipes: RecipeRepository,
    product_root: str,
    governor_root: str,
    surfaces: Iterable[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    requested = sorted(set(surfaces or SURFACE_TO_RUNTIME))
    unknown = sorted(set(requested) - set(SURFACE_TO_RUNTIME))
    if unknown:
        raise ValueError(f"Unsupported projection surfaces: {', '.join(unknown)}")

    runtime_filter = {SURFACE_TO_RUNTIME[surface] for surface in requested}
    components = [
        component
        for component in _iter_components(repository)
        if component.get("runtimeAlias") in runtime_filter
    ]
    projections = [
        _component_projection(repository, recipes, component, product_root, governor_root)
        for component in components
    ]

    by_surface: dict[str, dict[str, Any]] = {}
    for surface in requested:
        rows = [row for row in projections if row.get("surface") == surface]
        status_counts = Counter(str(row.get("status")) for row in rows)
        by_surface[surface] = {
            "runtimeAlias": SURFACE_TO_RUNTIME[surface],
            "componentCount": len(rows),
            "exactTraceCompleteCount": sum(bool(row.get("exactTraceComplete")) for row in rows),
            "authorityPreflightReadyCount": sum(
                row.get("status") == "READY_FOR_EXACT_TARGET_AUTHORITY_PREFLIGHT" for row in rows
            ),
            "blockedCount": sum(bool(row.get("blockingReasons")) for row in rows),
            "statusCounts": dict(sorted(status_counts.items())),
        }

    global_blockers: list[str] = []
    if not components:
        global_blockers.append("NO_REQUESTED_SURFACE_COMPONENTS_IN_UIMAP")
    authority = _authority_snapshot(governor_root)
    global_blockers.extend(f"AUTHORITY:{issue}" for issue in authority.get("issues", []))
    adapter_checks = authority["adapterRegistry"]["requiredSurfaceAdapters"]
    for surface in requested:
        if not adapter_checks.get(surface, {}).get("present"):
            global_blockers.append(f"MISSING_CANONICAL_SURFACE_ADAPTER:{surface}")

    ready_count = sum(
        row.get("status") == "READY_FOR_EXACT_TARGET_AUTHORITY_PREFLIGHT" for row in projections
    )
    blocked_count = sum(bool(row.get("blockingReasons")) for row in projections)
    if global_blockers:
        status = "BLOCKED_BY_GLOBAL_AUTHORITY_GAP"
    elif ready_count:
        status = "SOURCE_READY_WITH_EXPLICIT_COMPONENT_BLOCKERS" if blocked_count else "SOURCE_READY"
    else:
        status = "SOURCE_MAPPED_NO_EXACT_TARGET_READY"

    stable_payload = {
        "requestedSurfaces": requested,
        "sourceBatchIds": sorted(
            str(batch.get("batchId")) for batch in repository.batches if batch.get("batchId")
        ),
        "projectionComponents": projections,
        "authority": authority,
        "globalBlockers": sorted(set(global_blockers)),
    }
    projection_id = "PRJMAP." + canonical_sha256(stable_payload)[:24]
    payload = {
        "schema": "prisma.ui.multi-surface-projection-map.v1",
        "schemaVersion": "1.0.0",
        "projectionId": projection_id,
        "generatedAt": _utc_now(),
        "mode": "READ_ONLY_SOURCE_PROJECTION",
        "applicationEnabled": False,
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
        "status": status,
        "requestedSurfaces": requested,
        "componentCount": len(projections),
        "exactTraceCompleteCount": sum(bool(row.get("exactTraceComplete")) for row in projections),
        "authorityPreflightReadyCount": ready_count,
        "blockedComponentCount": blocked_count,
        "surfaceSummary": by_surface,
        "globalBlockers": sorted(set(global_blockers)),
        "authority": authority,
        "components": projections,
        "hardTruth": (
            "A visual projection is not application-ready until its exact owner, route, region, slot, "
            "component, layer, implementation layer, source hashes and compatible recipe plan are all proven."
        ),
    }
    blockers = {
        "schema": "prisma.ui.multi-surface-projection-blockers.v1",
        "schemaVersion": "1.0.0",
        "projectionId": projection_id,
        "status": "PASS_NO_BLOCKERS" if not blocked_count and not global_blockers else "EXPLICIT_BLOCKERS_PRESENT",
        "globalBlockers": sorted(set(global_blockers)),
        "components": [
            {
                "componentId": row.get("componentId"),
                "componentUiId": row.get("componentUiId"),
                "surface": row.get("surface"),
                "status": row.get("status"),
                "blockingReasons": row.get("blockingReasons", []),
            }
            for row in projections
            if row.get("blockingReasons")
        ],
    }
    return payload, blockers


def _summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# PRISMA Multi-Surface Visual Projection",
        "",
        f"- Projection: `{payload.get('projectionId')}`",
        f"- Status: `{payload.get('status')}`",
        f"- Mode: `{payload.get('mode')}`",
        f"- Components: `{payload.get('componentCount')}`",
        f"- Exact trace complete: `{payload.get('exactTraceCompleteCount')}`",
        f"- Ready for exact-target Authority Mesh: `{payload.get('authorityPreflightReadyCount')}`",
        f"- Components with blockers: `{payload.get('blockedComponentCount')}`",
        "- Product application: `DISABLED`",
        "",
        "## Surface summary",
        "",
        "| Surface | Components | Exact trace | Ready | Blocked |",
        "|---|---:|---:|---:|---:|",
    ]
    for surface, row in payload.get("surfaceSummary", {}).items():
        lines.append(
            f"| {surface} | {row.get('componentCount', 0)} | {row.get('exactTraceCompleteCount', 0)} | "
            f"{row.get('authorityPreflightReadyCount', 0)} | {row.get('blockedCount', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Contract",
            "",
            "This artifact is a read-only projection map. It never authorizes product mutation. "
            "Each actual visual application still requires a fresh exact-target Authority Mesh, source drift checks, "
            "visual evidence and rollback.",
            "",
        ]
    )
    return "\n".join(lines)


def write_projection_map(
    output_dir: str | Path,
    payload: dict[str, Any],
    blockers: dict[str, Any],
) -> list[str]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    projection_path = write_json(root / "PRISMA_UI_MULTI_SURFACE_PROJECTION.json", payload)
    blocker_path = write_json(root / "PRISMA_UI_MULTI_SURFACE_BLOCKERS.json", blockers)
    summary_path = root / "PRISMA_UI_MULTI_SURFACE_SUMMARY.md"
    summary_path.write_text(_summary_markdown(payload), encoding="utf-8")
    return [str(projection_path), str(blocker_path), str(summary_path)]
