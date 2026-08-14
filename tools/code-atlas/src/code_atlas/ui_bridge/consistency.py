from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from code_atlas.app_map.uimap.contracts import ADAPTERS as UIMAP_ADAPTERS

from .canonical import canonical_sha256, write_json


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _adapter_ids(registry: dict[str, Any]) -> set[str]:
    return {
        str(row.get("id"))
        for row in registry.get("items", [])
        if isinstance(row, dict) and row.get("id")
    }


def _resolved_cobrar(registry: dict[str, Any]) -> dict[str, Any] | None:
    for binding in registry.get("bindings", []):
        if not isinstance(binding, dict):
            continue
        if binding.get("bindingId") != "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1":
            continue
        for target in binding.get("targets", []):
            if (
                isinstance(target, dict)
                and target.get("status") == "RESOLVED"
                and target.get("layerId")
            ):
                return target
    return None


def audit_visual_authority(governor_root: str | Path) -> dict[str, Any]:
    root = Path(governor_root).resolve()
    paths = {
        "bindingContract": root
        / "authority/rifat/identity/contract/PRISMA_IDENTITY_BINDING_CONTRACT.md",
        "elementBindings": root
        / "authority/rifat/identity/registries/element-bindings.registry.json",
        "surfaceBindings": root
        / "authority/rifat/identity/registries/bindings.registry.json",
        "surfaceAdapters": root
        / "extras/atlasfin/assets/data/surface-adapter.registry.json",
        "visualRecipeProjection": root
        / "extras/atlasfin/assets/data/visual.recipe.registry.json",
    }
    missing_files = [
        key for key, path in paths.items() if not path.is_file()
    ]
    issues: list[dict[str, Any]] = []
    if missing_files:
        issues.append(
            {
                "code": "REQUIRED_AUTHORITY_FILE_MISSING",
                "severity": "BLOCKER",
                "details": missing_files,
            }
        )
        return {
            "schema": "prisma.ui.bridge.visual-authority-consistency.v1",
            "schemaVersion": "1.0.0",
            "status": "BLOCKED",
            "governorRoot": str(root),
            "issues": issues,
            "checks": {},
        }

    element_bindings = _load(paths["elementBindings"])
    surface_bindings = _load(paths["surfaceBindings"])
    surface_adapters = _load(paths["surfaceAdapters"])
    visual_projection = _load(paths["visualRecipeProjection"])
    binding_contract = paths["bindingContract"].read_text(
        encoding="utf-8", errors="replace"
    )

    adapter_ids = _adapter_ids(surface_adapters)
    required_adapters = {
        runtime: UIMAP_ADAPTERS[runtime] for runtime in ("tb", "pc", "mb")
    }
    missing_adapters = sorted(
        adapter_id
        for adapter_id in required_adapters.values()
        if adapter_id not in adapter_ids
    )
    if missing_adapters:
        issues.append(
            {
                "code": "UIMAP_CANONICAL_ADAPTER_MISSING_FROM_VISREC2",
                "severity": "BLOCKER",
                "details": missing_adapters,
            }
        )

    cobrar = _resolved_cobrar(element_bindings)
    stale_contract = bool(
        cobrar
        and "current Tablet `Cobrar` candidate remains blocked" in binding_contract
    )
    if stale_contract:
        issues.append(
            {
                "code": "STALE_COBRAR_BINDING_CONTRACT",
                "severity": "BLOCKER",
                "details": {
                    "resolvedLayerId": cobrar.get("layerId"),
                    "bindingId": "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1",
                },
            }
        )

    surface_rows = {
        str(row.get("surface")): row
        for row in surface_bindings.get("bindings", [])
        if isinstance(row, dict) and row.get("surface")
    }
    for surface in ("pc", "mobile"):
        row = surface_rows.get(surface, {})
        readiness = str(row.get("readiness") or "")
        missing = list(row.get("missing") or [])
        map_sources = [
            row.get("ownerSource"),
            row.get("slotSource"),
            row.get("layerSource"),
        ]
        claims_certified = readiness in {
            "CERTIFIED_BINDING_SOURCE",
            "BINDING_READY_SOURCE_ONLY",
        }
        if claims_certified and (missing or any(not value for value in map_sources)):
            issues.append(
                {
                    "code": "SURFACE_BINDING_FALSE_GREEN",
                    "severity": "BLOCKER",
                    "details": {
                        "surface": surface,
                        "readiness": readiness,
                        "missing": missing,
                    },
                }
            )

    pending_projection_rows = []
    for element in visual_projection.get("elements", []):
        if not isinstance(element, dict):
            continue
        for target in element.get("target_bindings", []):
            if not isinstance(target, dict):
                continue
            if target.get("surface_id") in {"SURF.PC.ADMIN", "SURF.MB.OWNER"} and str(
                target.get("status") or ""
            ).startswith("BLOCKED"):
                pending_projection_rows.append(
                    {
                        "componentId": element.get("component_id"),
                        "semanticId": element.get("semantic_id"),
                        "surfaceId": target.get("surface_id"),
                        "status": target.get("status"),
                    }
                )

    blockers = [issue for issue in issues if issue.get("severity") == "BLOCKER"]
    checks = {
        "uimapCanonicalAdapters": required_adapters,
        "visrec2AdapterIdsPresent": not missing_adapters,
        "resolvedCobrarLayerId": cobrar.get("layerId") if cobrar else None,
        "bindingContractCobrarConsistent": not stale_contract,
        "pcBindingReadiness": (surface_rows.get("pc") or {}).get("readiness"),
        "mobileBindingReadiness": (surface_rows.get("mobile") or {}).get("readiness"),
        "pcMobilePendingVisualProjectionBindingCount": len(pending_projection_rows),
        "pcMobilePendingVisualProjectionBindings": pending_projection_rows,
    }
    stable = {
        "issues": issues,
        "checks": checks,
    }
    return {
        "schema": "prisma.ui.bridge.visual-authority-consistency.v1",
        "schemaVersion": "1.0.0",
        "status": "PASS" if not blockers else "BLOCKED",
        "governorRoot": str(root),
        "checks": checks,
        "issues": issues,
        "blockingIssueCount": len(blockers),
        "reportChecksum": canonical_sha256(stable),
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
    }


def write_visual_authority_audit(
    output_dir: str | Path, report: dict[str, Any]
) -> str:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    return str(
        write_json(root / "PRISMA_UI_BRIDGE_VISUAL_AUTHORITY_CONSISTENCY.json", report)
    )
