from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_sha256, write_json
from .planner import build_plan
from .recipes import RecipeRepository
from .repository import BridgeRepository

CORE_RUNTIME_ALIASES = ("tb", "pc", "mb")


def _unique_components(repository: BridgeRepository) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for component in repository.components_by_id.values():
        if not isinstance(component, dict):
            continue
        key = str(component.get("componentUiId") or component.get("componentId") or "")
        if key:
            rows[key] = component
    return [rows[key] for key in sorted(rows)]


def _neutral_id(
    repository: BridgeRepository,
    source_component: str | None,
    neutral_meaning_id: str | None,
) -> str:
    explicit = str(neutral_meaning_id or "").strip()
    source_neutral = ""
    if source_component:
        source = repository.component(source_component)
        source_neutral = str(source.get("neutralMeaningId") or "").strip()
        if not source_neutral:
            raise ValueError(f"SOURCE_COMPONENT_HAS_NO_NEUTRAL_MEANING:{source_component}")
    if explicit and source_neutral and explicit != source_neutral:
        raise ValueError(
            f"NEUTRAL_MEANING_MISMATCH:explicit={explicit}:source={source_neutral}"
        )
    resolved = explicit or source_neutral
    if not resolved:
        raise ValueError("NEUTRAL_MEANING_REQUIRED")
    return resolved


def _targets(
    repository: BridgeRepository,
    neutral_meaning_id: str,
    runtime_aliases: Iterable[str],
) -> dict[str, list[dict[str, Any]]]:
    requested = tuple(dict.fromkeys(str(value).strip() for value in runtime_aliases if str(value).strip()))
    if not requested:
        requested = CORE_RUNTIME_ALIASES
    unsupported = sorted(set(requested) - set(CORE_RUNTIME_ALIASES))
    if unsupported:
        raise ValueError("UNSUPPORTED_CORE_RUNTIME_ALIAS:" + ",".join(unsupported))
    by_runtime = {runtime: [] for runtime in requested}
    for component in _unique_components(repository):
        runtime = str(component.get("runtimeAlias") or "")
        if runtime not in by_runtime:
            continue
        if str(component.get("neutralMeaningId") or "") != neutral_meaning_id:
            continue
        by_runtime[runtime].append(component)
    for runtime in by_runtime:
        by_runtime[runtime].sort(key=lambda row: str(row.get("componentUiId") or row.get("componentId") or ""))
    return by_runtime


def build_multisurface_plan(
    repository: BridgeRepository,
    recipes: RecipeRepository,
    product_root: str,
    governor_root: str | None = None,
    *,
    source_component: str | None = None,
    neutral_meaning_id: str | None = None,
    recipe_id: str | None = None,
    runtime_aliases: Iterable[str] = CORE_RUNTIME_ALIASES,
    require_all_surfaces: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    neutral = _neutral_id(repository, source_component, neutral_meaning_id)
    by_runtime = _targets(repository, neutral, runtime_aliases)
    target_rows: list[dict[str, Any]] = []
    blockers: list[str] = []

    for runtime, components in by_runtime.items():
        if require_all_surfaces and not components:
            blockers.append(f"SURFACE_HAS_NO_EXACT_NEUTRAL_MATCH:{runtime}:{neutral}")
        surface_targets: list[dict[str, Any]] = []
        for component in components:
            component_ref = str(component.get("componentUiId") or component.get("componentId"))
            plan, diff = build_plan(
                repository,
                recipes,
                component_ref,
                product_root,
                governor_root,
                recipe_id,
            )
            target_blockers = list(plan.get("blockingReasons") or [])
            blockers.extend(
                f"{runtime}:{component_ref}:{reason}" for reason in target_blockers
            )
            surface_targets.append(
                {
                    "componentId": component.get("componentId"),
                    "componentUiId": component.get("componentUiId"),
                    "surfaceId": component.get("surfaceId"),
                    "interfaceId": component.get("interfaceId"),
                    "routeId": component.get("routeId"),
                    "routePath": component.get("routePath"),
                    "ownerId": component.get("ownerId"),
                    "regionId": component.get("regionId"),
                    "slotId": component.get("slotId"),
                    "bindingId": component.get("bindingId"),
                    "layerId": component.get("layerId"),
                    "implementationLayerId": component.get("implementationLayerId"),
                    "adapterId": plan.get("adapterId"),
                    "neutralMeaningId": component.get("neutralMeaningId"),
                    "targetResolutionStatus": component.get("targetResolutionStatus"),
                    "applicationReadiness": component.get("applicationReadiness"),
                    "plan": plan,
                    "semanticDiff": diff,
                }
            )
        target_rows.append(
            {
                "runtimeAlias": runtime,
                "matchPolicy": "ALL_EXACT_NEUTRAL_MEANING_MATCHES",
                "matchCount": len(surface_targets),
                "targets": surface_targets,
            }
        )

    blockers = sorted(set(blockers))
    stable = {
        "neutralMeaningId": neutral,
        "sourceComponent": source_component,
        "requestedRecipeId": recipe_id,
        "requireAllSurfaces": bool(require_all_surfaces),
        "surfaceOrder": list(by_runtime),
        "surfaces": target_rows,
        "blockingReasons": blockers,
    }
    plan_id = "BRMULTI." + canonical_sha256(stable)[:24]
    plan = {
        "schema": "prisma.ui.bridge.multisurface-plan.v1",
        "schemaVersion": "1.0.0",
        "planId": plan_id,
        "createdAt": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "mode": "READ_ONLY_SOURCE_PLAN",
        "status": "PLAN_READY_FOR_REVIEW" if not blockers else "PLAN_BLOCKED",
        "applicationEnabled": False,
        "productMutationAllowed": False,
        "runtimeMutationAllowed": False,
        "targetSetPolicy": "EXHAUSTIVE_WITHIN_REQUESTED_RUNTIME_ALIASES",
        "futureApplicationGate": "FRESH_EXACT_TARGET_AUTHORITY_MESH_REQUIRED",
        **stable,
    }
    diff_rows = [
        {
            "runtimeAlias": surface["runtimeAlias"],
            "componentUiId": target.get("componentUiId"),
            "diffChecksum": (target.get("semanticDiff") or {}).get("checksum"),
            "operations": (target.get("semanticDiff") or {}).get("operations", []),
        }
        for surface in target_rows
        for target in surface["targets"]
    ]
    semantic_diff = {
        "schema": "prisma.ui.bridge.multisurface-diff.v1",
        "schemaVersion": "1.0.0",
        "planId": plan_id,
        "status": "DIFF_READY" if diff_rows and not blockers else "DIFF_BLOCKED",
        "sourceMutationPerformed": False,
        "productMutationPerformed": False,
        "runtimeMutationPerformed": False,
        "targets": diff_rows,
        "checksum": canonical_sha256(diff_rows),
    }
    return plan, semantic_diff


def write_multisurface_plan(
    output_dir: str | Path,
    plan: dict[str, Any],
    semantic_diff: dict[str, Any],
) -> list[str]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = [
        write_json(root / "PRISMA_UI_BRIDGE_MULTISURFACE_PLAN.json", plan),
        write_json(root / "PRISMA_UI_BRIDGE_MULTISURFACE_DIFF.json", semantic_diff),
    ]
    return [str(path) for path in paths]
