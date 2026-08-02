from __future__ import annotations
from typing import Any

from .contracts import CANONICAL_ADAPTERS
from .drift import verify_component_drift
from .recipes import RecipeRepository
from .repository import BridgeRepository


def recipe_blocked(component: dict[str, Any]) -> bool:
    value = component.get("recipeCompatibility")
    if isinstance(value, str): return value.upper().startswith("BLOCKED")
    if isinstance(value, dict):
        return any(
            str(value.get(key, "")).upper().startswith("BLOCKED")
            for key in ("status", "coverageStatus")
        )
    return False


def resolve_component(repository: BridgeRepository, recipes: RecipeRepository, component_ref: str, product_root: str, governor_root: str | None = None) -> dict[str, Any]:
    component = repository.component(component_ref)
    runtime = component.get("runtimeAlias")
    adapter = component.get("adapterId") or CANONICAL_ADAPTERS.get(runtime)
    recipe_matches = recipes.compatible(component)
    drift = verify_component_drift(component, product_root, governor_root)
    blockers = list(component.get("blockingReasons") or [])
    if component.get("targetResolutionStatus") != "SOURCE_RESOLVED": blockers.append("TARGET_NOT_SOURCE_RESOLVED")
    if component.get("ndcStatus") not in {"CONFIRMED", "CANONICAL_READY"}: blockers.append("NDC_NOT_CONFIRMED")
    if component.get("confidence") not in {"HIGH", "VERY_HIGH"}: blockers.append("CONFIDENCE_NOT_HIGH")
    if not drift["ok"]: blockers.append("SOURCE_DRIFT_OR_MISSING")
    if recipe_blocked(component): blockers.append("RECIPE_COMPATIBILITY_BLOCKED")
    if not recipe_matches: blockers.append("NO_COMPATIBLE_RECIPE_RESOLVED")
    if component.get("applicationReadiness") != "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT": blockers.append("NOT_ELIGIBLE_FOR_AUTHORITY_PREFLIGHT")
    blockers = sorted(set(blockers))
    return {
        "schema": "prisma.ui.bridge.resolution.v1",
        "componentId": component.get("componentId"),
        "componentUiId": component.get("componentUiId"),
        "target": {
            "ownerId": component.get("ownerId"),
            "ownerFile": component.get("ownerFile"),
            "ownerSymbol": component.get("ownerSymbol"),
            "renderSourceFile": component.get("renderSourceFile"),
            "renderSymbol": component.get("renderSymbol"),
            "visualTargets": component.get("visualTargets", []),
        },
        "neutralMeaningId": component.get("neutralMeaningId"),
        "relatedNeutralIds": component.get("relatedNeutralIds", []),
        "bindingId": component.get("bindingId"),
        "layerId": component.get("layerId"),
        "implementationLayerId": component.get("implementationLayerId"),
        "adapterId": adapter,
        "recipes": [{"recipeId": r.get("recipeId"), "canonicalPayloadSha256": r.get("canonicalPayloadSha256")} for r in recipe_matches],
        "drift": drift,
        "blockingReasons": blockers,
        "status": "ELIGIBLE_FOR_READ_ONLY_PLAN" if not blockers else "BLOCKED",
    }
