from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import canonical_sha256, write_json
from .recipes import RecipeRepository
from .repository import BridgeRepository
from .resolver import resolve_component


def _recipe_operations(
    recipe: dict[str, Any],
    component: dict[str, Any],
    repository: BridgeRepository,
) -> tuple[list[dict[str, Any]], list[str]]:
    values = recipe.get("values", {}) if isinstance(recipe.get("values"), dict) else {}
    visual_stack = values.get("visualStack") or recipe.get("visualStack") or {}
    units = visual_stack.get("units", []) if isinstance(visual_stack, dict) else []
    operations: list[dict[str, Any]] = []
    unresolved: list[str] = []
    for unit in units if isinstance(units, list) else []:
        if not isinstance(unit, dict): continue
        selector = unit.get("selector")
        matched = repository.related_visual_targets(component, str(selector) if selector else None)
        properties = unit.get("properties", {}) if isinstance(unit.get("properties"), dict) else {}
        property_modes = {
            str(instruction.get("mode"))
            for instruction in properties.values()
            if isinstance(instruction, dict) and instruction.get("mode")
        }
        policy_only = bool(properties) and property_modes.issubset({"POLICY", "INHERIT"})
        target_required = not policy_only
        if target_required and not matched:
            unresolved.append(str(unit.get("unitId") or selector or "<unidentified>"))
        operations.append({
            "unitId": unit.get("unitId"),
            "kind": unit.get("kind"),
            "selector": selector,
            "matchedVisualTargetIds": [str(target.get("visualTargetId")) for _, target in matched],
            "matchedComponentUiIds": sorted({
                str(candidate.get("componentUiId"))
                for candidate, _ in matched
                if candidate.get("componentUiId")
            }),
            "targetResolutionStatus": (
                "SOURCE_RESOLVED"
                if matched
                else "POLICY_ONLY_NO_SOURCE_TARGET_REQUIRED"
                if policy_only
                else "BLOCKED_BY_MISSING_SOURCE_TARGET"
            ),
            "propertyChanges": [{"property": key, "instruction": properties[key]} for key in sorted(properties)],
            "applicationPolicy": unit.get("applicationPolicy"),
            "patchPolicy": "PLAN_ONLY_NO_SOURCE_MUTATION",
        })
    return operations, sorted(set(unresolved))


def build_plan(repository: BridgeRepository, recipes: RecipeRepository, component_ref: str, product_root: str, governor_root: str | None = None, recipe_id: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    component = repository.component(component_ref)
    resolution = resolve_component(repository, recipes, component_ref, product_root, governor_root)
    candidates = recipes.compatible(component)
    recipe = next((r for r in candidates if r.get("recipeId") == recipe_id), None) if recipe_id else (candidates[0] if candidates else None)
    blockers = list(resolution["blockingReasons"])
    if recipe_id and recipe is None: blockers.append("REQUESTED_RECIPE_NOT_COMPATIBLE_OR_MISSING")
    operations, unresolved_units = _recipe_operations(recipe, component, repository) if recipe else ([], [])
    blockers.extend(f"RECIPE_UNIT_TARGET_UNRESOLVED:{unit_id}" for unit_id in unresolved_units)
    if not operations: blockers.append("RECIPE_HAS_NO_PLANABLE_VISUAL_STACK")
    blockers = sorted(set(blockers))
    stable_payload = {
        "componentId": component.get("componentId"),
        "componentUiId": component.get("componentUiId"),
        "sourceSnapshotHash": next((b.get("sourceSnapshotHash") for b in repository.batches if component in b.get("components", [])), None),
        "recipeId": recipe.get("recipeId") if recipe else recipe_id,
        "recipeSha256": recipe.get("canonicalPayloadSha256") if recipe else None,
        "adapterId": resolution.get("adapterId"),
        "bindingId": resolution.get("bindingId"),
        "layerId": resolution.get("layerId"),
        "implementationLayerId": resolution.get("implementationLayerId"),
        "operations": operations,
        "blockingReasons": blockers,
    }
    plan_id = "BRPLAN." + canonical_sha256(stable_payload)[:24]
    plan = {
        "schema": "prisma.ui.bridge.plan.v1",
        "schemaVersion": "1.0.0",
        "planId": plan_id,
        "createdAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": "READ_ONLY_SOURCE_PLAN",
        "applicationEnabled": False,
        "status": "PLAN_READY_FOR_REVIEW" if not blockers else "PLAN_BLOCKED",
        **stable_payload,
        "resolution": resolution,
    }
    semantic_diff = {
        "schema": "prisma.ui.bridge.semantic-diff.v1",
        "planId": plan_id,
        "status": "DIFF_READY" if operations else "DIFF_BLOCKED",
        "sourceMutationPerformed": False,
        "operations": operations,
        "checksum": canonical_sha256(operations),
    }
    return plan, semantic_diff


def write_plan(output_dir: str | Path, plan: dict[str, Any], semantic_diff: dict[str, Any]) -> list[str]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = [write_json(root / "PRISMA_UI_BRIDGE_PLAN.json", plan), write_json(root / "PRISMA_UI_BRIDGE_DIFF.json", semantic_diff)]
    return [str(p) for p in paths]
