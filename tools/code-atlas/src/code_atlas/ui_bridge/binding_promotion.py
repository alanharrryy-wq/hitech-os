from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_sha256, read_json, write_json
from .repository import BridgeRepository

CORE_RUNTIME_ALIASES = ("tb", "pc", "mb")
REQUIRED_COORDINATE_FIELDS = (
    "ownerId",
    "routeId",
    "regionId",
    "slotId",
    "componentUiId",
    "layerId",
    "bindingId",
    "neutralMeaningId",
    "adapterId",
    "implementationLayerId",
)


def _unique_components(repository: BridgeRepository) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for component in repository.components_by_id.values():
        if not isinstance(component, dict):
            continue
        key = str(component.get("componentUiId") or component.get("componentId") or "")
        if key:
            rows[key] = component
    return [rows[key] for key in sorted(rows)]


def load_registered_binding_ids(path: str | Path | None) -> set[str]:
    if not path:
        return set()
    target = Path(path)
    if not target.is_file():
        return set()
    payload = read_json(target)
    return {
        str(row.get("bindingId"))
        for row in payload.get("bindings", [])
        if isinstance(row, dict) and row.get("bindingId")
    }


def load_pilot_contracts(paths: Iterable[str | Path]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for raw in paths:
        path = Path(raw)
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        pilot = payload.get("pilot") if isinstance(payload, dict) else None
        if not isinstance(pilot, dict):
            continue
        component_ui_id = pilot.get("componentUiId")
        if component_ui_id:
            out[str(component_ui_id)] = {
                "path": path.as_posix(),
                "schema": payload.get("schema"),
                "status": payload.get("status"),
                "pilot": pilot,
            }
    return out


def _visual_target_errors(component: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    visual_targets = component.get("visualTargets")
    if not isinstance(visual_targets, list) or not visual_targets:
        return ["VISUAL_TARGETS_MISSING"]
    for index, target in enumerate(visual_targets):
        if not isinstance(target, dict):
            errors.append(f"VISUAL_TARGET_INVALID:{index}")
            continue
        if not target.get("styleSourceFile"):
            errors.append(f"STYLE_SOURCE_MISSING:{index}")
        source_hash = str(target.get("sourceHash") or "")
        if len(source_hash) != 64:
            errors.append(f"STYLE_SOURCE_HASH_MISSING:{index}")
        if not target.get("anchorKind") or not target.get("anchorValue"):
            errors.append(f"VISUAL_ANCHOR_MISSING:{index}")
    return errors


def evaluate_component(
    component: dict[str, Any],
    registered_binding_ids: set[str],
    pilot_contracts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    missing = [
        field for field in REQUIRED_COORDINATE_FIELDS if not component.get(field)
    ]
    blockers = [f"MISSING_COORDINATE:{field}" for field in missing]
    if component.get("targetResolutionStatus") != "SOURCE_RESOLVED":
        blockers.append("TARGET_NOT_SOURCE_RESOLVED")
    if component.get("ndcStatus") not in {"CONFIRMED", "CANONICAL_READY"}:
        blockers.append("NDC_NOT_CONFIRMED")
    if component.get("confidence") not in {"HIGH", "VERY_HIGH"}:
        blockers.append("CONFIDENCE_NOT_HIGH")
    if component.get("applicationReadiness") != "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT":
        blockers.append("NOT_ELIGIBLE_FOR_AUTHORITY_PREFLIGHT")
    blockers.extend(_visual_target_errors(component))
    source_hashes = component.get("sourceHashes")
    if not isinstance(source_hashes, dict) or not source_hashes:
        blockers.append("SOURCE_HASHES_MISSING")

    component_ui_id = str(component.get("componentUiId") or "")
    pilot = pilot_contracts.get(component_ui_id)
    pilot_alignment: dict[str, Any] | None = None
    if pilot:
        pilot_row = pilot["pilot"]
        comparisons = {
            "routeId": (component.get("routeId"), pilot_row.get("routeId")),
            "ownerId": (component.get("ownerId"), pilot_row.get("ownerId")),
            "regionId": (component.get("regionId"), pilot_row.get("regionId")),
            "slotId": (component.get("slotId"), pilot_row.get("slotId")),
            "componentUiId": (
                component.get("componentUiId"),
                pilot_row.get("componentUiId"),
            ),
            "bindingId": (component.get("bindingId"), pilot_row.get("bindingId")),
            "implementationLayerId": (
                component.get("implementationLayerId"),
                pilot_row.get("implementationLayerId"),
            ),
        }
        mismatches = [
            key
            for key, (uimap_value, pilot_value) in comparisons.items()
            if pilot_value is not None and uimap_value != pilot_value
        ]
        pilot_alignment = {
            "contractPath": pilot["path"],
            "contractSchema": pilot.get("schema"),
            "contractStatus": pilot.get("status"),
            "mismatches": mismatches,
            "aligned": not mismatches,
        }
        if mismatches:
            blockers.append("PILOT_CONTRACT_DRIFT:" + ",".join(sorted(mismatches)))

    blockers = sorted(set(blockers))
    binding_id = component.get("bindingId")
    central_status = (
        "ALREADY_REGISTERED"
        if binding_id and str(binding_id) in registered_binding_ids
        else "CENTRAL_REGISTRY_PROMOTION_CANDIDATE"
    )
    return {
        "promotionKey": "BPROM."
        + canonical_sha256(
            {
                "componentUiId": component.get("componentUiId"),
                "bindingId": component.get("bindingId"),
                "sourceHashes": component.get("sourceHashes"),
            }
        )[:20],
        "runtimeAlias": component.get("runtimeAlias"),
        "surfaceId": component.get("surfaceId"),
        "componentId": component.get("componentId"),
        "componentUiId": component.get("componentUiId"),
        "neutralMeaningId": component.get("neutralMeaningId"),
        "ownerId": component.get("ownerId"),
        "routeId": component.get("routeId"),
        "regionId": component.get("regionId"),
        "slotId": component.get("slotId"),
        "bindingId": component.get("bindingId"),
        "layerId": component.get("layerId"),
        "implementationLayerId": component.get("implementationLayerId"),
        "adapterId": component.get("adapterId"),
        "visualTargets": component.get("visualTargets", []),
        "sourceHashes": component.get("sourceHashes", {}),
        "evidenceRefs": component.get("evidenceRefs", []),
        "uimapState": {
            "targetResolutionStatus": component.get("targetResolutionStatus"),
            "ndcStatus": component.get("ndcStatus"),
            "confidence": component.get("confidence"),
            "applicationReadiness": component.get("applicationReadiness"),
        },
        "pilotAlignment": pilot_alignment,
        "centralRegistryStatus": central_status,
        "status": (
            central_status
            if not blockers
            else "BLOCKED_BY_INCOMPLETE_OR_DRIFTED_SOURCE_EVIDENCE"
        ),
        "blockingReasons": blockers,
        "instructionOnly": True,
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
    }


def build_binding_promotion_report(
    repository: BridgeRepository,
    *,
    binding_registry_path: str | Path | None = None,
    pilot_contract_paths: Iterable[str | Path] = (),
    runtime_aliases: Iterable[str] = CORE_RUNTIME_ALIASES,
) -> tuple[dict[str, Any], dict[str, Any]]:
    requested = tuple(
        dict.fromkeys(str(value).strip() for value in runtime_aliases if str(value).strip())
    ) or CORE_RUNTIME_ALIASES
    unsupported = sorted(set(requested) - set(CORE_RUNTIME_ALIASES))
    if unsupported:
        raise ValueError("UNSUPPORTED_CORE_RUNTIME_ALIAS:" + ",".join(unsupported))

    registered = load_registered_binding_ids(binding_registry_path)
    pilots = load_pilot_contracts(pilot_contract_paths)
    rows = [
        evaluate_component(component, registered, pilots)
        for component in _unique_components(repository)
        if component.get("runtimeAlias") in requested
    ]
    rows.sort(
        key=lambda row: (
            str(row.get("runtimeAlias") or ""),
            str(row.get("componentUiId") or ""),
        )
    )
    promotable = [
        row
        for row in rows
        if row["status"] in {
            "ALREADY_REGISTERED",
            "CENTRAL_REGISTRY_PROMOTION_CANDIDATE",
        }
    ]
    candidates = [
        row for row in promotable if row["status"] == "CENTRAL_REGISTRY_PROMOTION_CANDIDATE"
    ]
    gaps = [row for row in rows if row["blockingReasons"]]
    report = {
        "schema": "prisma.ui.bridge.binding-promotion.v1",
        "schemaVersion": "1.0.0",
        "mode": "READ_ONLY_SOURCE_PROMOTION_ANALYSIS",
        "status": "PROMOTION_CANDIDATES_READY" if candidates else "NO_NEW_PROMOTION_CANDIDATES",
        "runtimeAliases": list(requested),
        "registeredBindingCount": len(registered),
        "componentCount": len(rows),
        "promotableCount": len(promotable),
        "newPromotionCandidateCount": len(candidates),
        "blockedCount": len(gaps),
        "candidates": candidates,
        "alreadyRegistered": [
            row for row in promotable if row["status"] == "ALREADY_REGISTERED"
        ],
        "instructionOnly": True,
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
        "policy": {
            "inventCoordinates": False,
            "exactUimapFullChainRequired": True,
            "pilotContractsAreCrosscheckEvidenceOnly": True,
            "oneToManySamplingAllowed": False,
        },
    }
    gap_matrix = {
        "schema": "prisma.ui.bridge.binding-gap-matrix.v1",
        "schemaVersion": "1.0.0",
        "status": "GAPS_PRESENT" if gaps else "NO_GAPS",
        "runtimeAliases": list(requested),
        "rows": gaps,
        "counts": {
            runtime: {
                "total": sum(1 for row in rows if row.get("runtimeAlias") == runtime),
                "promotable": sum(
                    1
                    for row in promotable
                    if row.get("runtimeAlias") == runtime
                ),
                "blocked": sum(
                    1 for row in gaps if row.get("runtimeAlias") == runtime
                ),
            }
            for runtime in requested
        },
        "sourceMutationPerformed": False,
    }
    return report, gap_matrix


def write_binding_promotion_report(
    output_dir: str | Path,
    report: dict[str, Any],
    gap_matrix: dict[str, Any],
) -> list[str]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = [
        write_json(root / "PRISMA_UI_BRIDGE_BINDING_PROMOTION.json", report),
        write_json(root / "PRISMA_UI_BRIDGE_BINDING_GAP_MATRIX.json", gap_matrix),
    ]
    return [str(path) for path in paths]
