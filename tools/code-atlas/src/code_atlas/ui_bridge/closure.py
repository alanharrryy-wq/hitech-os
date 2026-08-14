from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from code_atlas.app_map.uimap.runner import run_uimap

from .binding_promotion import build_binding_promotion_report, write_binding_promotion_report
from .canonical import canonical_sha256, write_json
from .consistency import audit_visual_authority, write_visual_authority_audit
from .projection import build_projection_map, write_projection_map
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


def build_three_app_readiness(repository: BridgeRepository, promotion_report: dict[str, Any]) -> dict[str, Any]:
    components = [row for row in _unique_components(repository) if row.get("runtimeAlias") in CORE_RUNTIME_ALIASES]
    promotion_by_ui = {
        str(row.get("componentUiId")): row
        for row in [*promotion_report.get("candidates", []), *promotion_report.get("alreadyRegistered", [])]
        if row.get("componentUiId")
    }
    by_neutral: dict[str, dict[str, Any]] = {}
    for component in components:
        neutral = str(component.get("neutralMeaningId") or "").strip()
        if not neutral:
            continue
        runtime = str(component.get("runtimeAlias") or "")
        group = by_neutral.setdefault(
            neutral,
            {"neutralMeaningId": neutral, "surfaces": {alias: [] for alias in CORE_RUNTIME_ALIASES}},
        )
        group["surfaces"][runtime].append(
            {
                "componentId": component.get("componentId"),
                "componentUiId": component.get("componentUiId"),
                "targetResolutionStatus": component.get("targetResolutionStatus"),
                "applicationReadiness": component.get("applicationReadiness"),
                "promotionStatus": (promotion_by_ui.get(str(component.get("componentUiId"))) or {}).get("status"),
            }
        )

    neutral_rows = []
    for neutral in sorted(by_neutral):
        row = by_neutral[neutral]
        present = [alias for alias, items in row["surfaces"].items() if items]
        all_surfaces_present = set(present) == set(CORE_RUNTIME_ALIASES)
        all_targets_source_resolved = all(
            item.get("targetResolutionStatus") == "SOURCE_RESOLVED"
            for items in row["surfaces"].values()
            for item in items
        ) and any(row["surfaces"].values())
        all_targets_promotable = all(
            item.get("promotionStatus") in {"ALREADY_REGISTERED", "CENTRAL_REGISTRY_PROMOTION_CANDIDATE"}
            for items in row["surfaces"].values()
            for item in items
        ) and any(row["surfaces"].values())
        row.update(
            {
                "presentRuntimeAliases": present,
                "missingRuntimeAliases": [alias for alias in CORE_RUNTIME_ALIASES if alias not in present],
                "allCoreSurfacesPresent": all_surfaces_present,
                "allTargetsSourceResolved": all_targets_source_resolved,
                "allTargetsPromotable": all_targets_promotable,
                "threeAppTransferReady": all_surfaces_present and all_targets_source_resolved and all_targets_promotable,
            }
        )
        neutral_rows.append(row)

    surface_counts = {}
    for runtime in CORE_RUNTIME_ALIASES:
        runtime_components = [row for row in components if row.get("runtimeAlias") == runtime]
        surface_counts[runtime] = {
            "components": len(runtime_components),
            "withNeutralMeaning": sum(1 for row in runtime_components if row.get("neutralMeaningId")),
            "sourceResolved": sum(1 for row in runtime_components if row.get("targetResolutionStatus") == "SOURCE_RESOLVED"),
            "authorityPreflightEligible": sum(
                1 for row in runtime_components if row.get("applicationReadiness") == "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT"
            ),
        }

    return {
        "schema": "prisma.ui.bridge.three-app-mapping-readiness.v1",
        "schemaVersion": "1.0.0",
        "mode": "READ_ONLY_SOURCE_MAPPING",
        "runtimeAliases": list(CORE_RUNTIME_ALIASES),
        "surfaceCounts": surface_counts,
        "neutralMeaningCount": len(neutral_rows),
        "threeAppTransferReadyNeutralMeaningCount": sum(1 for row in neutral_rows if row["threeAppTransferReady"]),
        "neutralMeanings": neutral_rows,
        "applicationEnabled": False,
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
        "policy": {
            "exactUimapCoordinatesOnly": True,
            "samplingOneToManyAllowed": False,
            "missingCoreSurfaceBlocksThreeAppTransfer": True,
            "futureApplyRequiresFreshExactTargetMesh": True,
        },
    }


def refresh_three_app_mapping(
    *,
    product_root: str | Path,
    governor_root: str | Path,
    output_root: str | Path,
    binding_registry_path: str | Path | None = None,
    pilot_contract_paths: Iterable[str | Path] = (),
    recipe_paths: Iterable[str | Path] = (),
    previous_batches_source: str | None = None,
    workers: int = 18,
) -> dict[str, Any]:
    product = Path(product_root).resolve()
    governor = Path(governor_root).resolve()
    output = Path(output_root).resolve()
    output.mkdir(parents=True, exist_ok=True)

    uimap_root = output / "uimap"
    uimap_result = run_uimap(
        product_root=str(product),
        governor_root=str(governor),
        output_dir=str(uimap_root),
        workers=max(1, min(18, int(workers))),
        previous_batches_source=previous_batches_source,
    )
    if not uimap_result.get("ok"):
        manifest = {
            "schema": "prisma.ui.bridge.three-app-mapping-refresh.v1",
            "schemaVersion": "1.0.0",
            "status": "BLOCKED_BY_UIMAP",
            "uimap": uimap_result,
            "applicationEnabled": False,
        }
        write_json(output / "PRISMA_THREE_APP_VISUAL_MAPPING_REFRESH.json", manifest)
        return manifest

    repository = BridgeRepository.load([uimap_root / "batches"])
    central_registry = Path(binding_registry_path) if binding_registry_path else governor / "authority/rifat/identity/registries/element-bindings.registry.json"
    promotion, gaps = build_binding_promotion_report(
        repository,
        binding_registry_path=central_registry,
        pilot_contract_paths=pilot_contract_paths,
        runtime_aliases=CORE_RUNTIME_ALIASES,
    )
    write_binding_promotion_report(output, promotion, gaps)

    consistency = audit_visual_authority(governor)
    write_visual_authority_audit(output, consistency)
    readiness = build_three_app_readiness(repository, promotion)
    write_json(output / "PRISMA_THREE_APP_VISUAL_MAPPING_READINESS.json", readiness)

    recipes = RecipeRepository.load(recipe_paths)
    projection, projection_blockers = build_projection_map(
        repository,
        recipes,
        str(product),
        str(governor),
        ("tablet", "pc", "mobile"),
    )
    write_projection_map(output, projection, projection_blockers)

    blockers = []
    if consistency.get("status") != "PASS":
        blockers.append("VISUAL_AUTHORITY_CONSISTENCY_BLOCKED")
    if gaps.get("status") == "GAPS_PRESENT":
        blockers.append("EXACT_BINDING_GAPS_PRESENT")
    if readiness.get("threeAppTransferReadyNeutralMeaningCount", 0) == 0:
        blockers.append("NO_NEUTRAL_MEANING_READY_ACROSS_ALL_THREE_APPS")
    if projection.get("status") == "BLOCKED_BY_GLOBAL_AUTHORITY_GAP":
        blockers.append("MULTI_SURFACE_PROJECTION_GLOBAL_AUTHORITY_BLOCKED")

    stable = {
        "uimapSourceSnapshotHash": uimap_result.get("sourceSnapshotHash"),
        "consistencyChecksum": consistency.get("reportChecksum"),
        "bindingPromotionCounts": {
            "promotable": promotion.get("promotableCount"),
            "new": promotion.get("newPromotionCandidateCount"),
            "blocked": promotion.get("blockedCount"),
        },
        "readiness": {
            "neutralMeaningCount": readiness.get("neutralMeaningCount"),
            "threeAppTransferReadyNeutralMeaningCount": readiness.get("threeAppTransferReadyNeutralMeaningCount"),
        },
        "projection": {
            "projectionId": projection.get("projectionId"),
            "status": projection.get("status"),
            "componentCount": projection.get("componentCount"),
            "authorityPreflightReadyCount": projection.get("authorityPreflightReadyCount"),
            "blockedComponentCount": projection.get("blockedComponentCount"),
        },
        "blockers": blockers,
    }
    manifest = {
        "schema": "prisma.ui.bridge.three-app-mapping-refresh.v1",
        "schemaVersion": "1.0.0",
        "status": "READY_FOR_SOURCE_REVIEW" if not blockers else "SOURCE_GAPS_EXPLICIT",
        "mode": "READ_ONLY",
        "uimap": uimap_result,
        "bindingPromotionReport": "PRISMA_UI_BRIDGE_BINDING_PROMOTION.json",
        "bindingGapMatrix": "PRISMA_UI_BRIDGE_BINDING_GAP_MATRIX.json",
        "consistencyReport": "PRISMA_UI_BRIDGE_VISUAL_AUTHORITY_CONSISTENCY.json",
        "readinessReport": "PRISMA_THREE_APP_VISUAL_MAPPING_READINESS.json",
        "projectionReport": "PRISMA_UI_MULTI_SURFACE_PROJECTION.json",
        "projectionBlockersReport": "PRISMA_UI_MULTI_SURFACE_BLOCKERS.json",
        "projectionSummary": "PRISMA_UI_MULTI_SURFACE_SUMMARY.md",
        "blockers": blockers,
        "checksum": canonical_sha256(stable),
        "applicationEnabled": False,
        "sourceMutationPerformed": False,
        "runtimeMutationPerformed": False,
        "productMutationPerformed": False,
    }
    write_json(output / "PRISMA_THREE_APP_VISUAL_MAPPING_REFRESH.json", manifest)
    return manifest
