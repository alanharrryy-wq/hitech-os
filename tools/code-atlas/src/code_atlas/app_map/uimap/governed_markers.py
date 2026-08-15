from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

CERTIFIED_PILOT_STATUSES = {"EXACT_TARGET_AUTHORIZED_FOR_GOVERNED_APPLICATION"}

MARKER_TO_PILOT_FIELD = {
    "data-prisma-route": "runtimeRoute",
    "data-prisma-owner": "ownerSymbol",
    "data-prisma-region": "regionId",
    "data-prisma-slot": "slotId",
    "data-prisma-component-ui-id": "componentUiId",
    "data-prisma-recipe": "recipeId",
    "data-prisma-visual-stack": "visualStackId",
    "data-prisma-binding": "bindingId",
    "data-prisma-adapter": "adapterId",
    "data-prisma-neutral-layer": "neutralLayerId",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _repo_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _pilot_contract_paths(product_root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for products in (
        product_root / "apps/terminal-de-venta-system/products",
        product_root / "products",
    ):
        if not products.is_dir():
            continue
        for path in sorted(products.glob("*/app/docs/visual-pilots/*.contract.json")):
            resolved = path.resolve()
            if resolved in seen or not resolved.is_file():
                continue
            seen.add(resolved)
            yield resolved


def load_certified_pilot_contracts(product_root: Path) -> dict[str, list[dict[str, Any]]]:
    root = product_root.resolve()
    index: dict[str, list[dict[str, Any]]] = {}
    for path in _pilot_contract_paths(root):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict) or payload.get("status") not in CERTIFIED_PILOT_STATUSES:
            continue
        pilot = payload.get("pilot")
        if not isinstance(pilot, dict):
            continue
        alias_id = str(pilot.get("componentUiId") or "").strip()
        if not alias_id:
            continue
        index.setdefault(alias_id, []).append({
            "contractPath": _repo_rel(root, path),
            "contractHash": _sha256(path),
            "contractSchema": payload.get("schema"),
            "contractStatus": payload.get("status"),
            "taskId": payload.get("taskId"),
            "pilot": pilot,
        })
    for alias_id in list(index):
        index[alias_id] = sorted(index[alias_id], key=lambda row: (str(row["contractPath"]), str(row["contractHash"])))
    return index


def _conflict(alias_id: str, candidate: Any, reasons: list[str]) -> dict[str, Any]:
    return {
        "conflictType": "CERTIFIED_VISUAL_PILOT_CROSSWALK_BLOCKED",
        "aliasId": alias_id,
        "runtimeAlias": str(getattr(candidate, "runtime_alias", "") or ""),
        "routePath": str(getattr(candidate, "route_path", "") or ""),
        "ownerFile": str(getattr(candidate, "owner_file", "") or ""),
        "blockingReasons": sorted(set(reasons)),
        "resolution": "ALIAS_WITHHELD",
    }


def certified_pilot_alias_for_candidate(
    candidate: Any,
    css_targets: list[Any],
    canonical_record: dict[str, Any],
    pilot_index: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Crosswalk one certified visual-pilot identity to canonical UIMAP.

    The pilot ID never replaces canonical UIMAP identity. Raw markers only
    activate validation; exact source/route/style/contract agreement is
    required before an alias is emitted.
    """
    attrs = dict(getattr(candidate, "data_attributes", {}) or {})
    pilot_ref = str(attrs.get("data-prisma-visual-pilot") or "").strip()
    if not pilot_ref:
        return None, None

    marker_route = str(attrs.get("data-prisma-route") or "").strip()
    candidate_route = str(getattr(candidate, "route_path", "") or "")
    if marker_route and marker_route != candidate_route:
        # Shared source legitimately projected through a different route.
        return None, None

    alias_id = str(attrs.get("data-prisma-component-ui-id") or "").strip()
    if not alias_id:
        return None, _conflict("", candidate, ["CERTIFIED_PILOT_COMPONENT_UI_ID_MARKER_MISSING"])

    matches = list(pilot_index.get(alias_id) or [])
    if not matches:
        return None, _conflict(alias_id, candidate, ["CERTIFIED_PILOT_CONTRACT_NOT_FOUND"])
    if len(matches) != 1:
        return None, _conflict(alias_id, candidate, ["CERTIFIED_PILOT_CONTRACT_AMBIGUOUS"])

    contract = matches[0]
    pilot = dict(contract.get("pilot") or {})
    blockers: list[str] = []
    for marker, field in MARKER_TO_PILOT_FIELD.items():
        actual = str(attrs.get(marker) or "").strip()
        expected = str(pilot.get(field) or "").strip()
        if not actual:
            blockers.append(f"CERTIFIED_PILOT_MARKER_MISSING:{marker}")
        elif not expected or actual != expected:
            blockers.append(f"CERTIFIED_PILOT_MARKER_MISMATCH:{marker}")

    runtime_alias = str(getattr(candidate, "runtime_alias", "") or "")
    if str(attrs.get("data-prisma-surface") or "").strip() != runtime_alias:
        blockers.append("CERTIFIED_PILOT_SURFACE_MARKER_MISMATCH")
    if not str(pilot.get("surfaceId") or "").startswith(f"SURF.{runtime_alias}."):
        blockers.append("CERTIFIED_PILOT_SURFACE_RUNTIME_MISMATCH")
    if candidate_route != str(pilot.get("runtimeRoute") or ""):
        blockers.append("CERTIFIED_PILOT_ROUTE_PATH_MISMATCH")
    if str(getattr(candidate, "route_id", "") or "") != str(pilot.get("routeId") or ""):
        blockers.append("CERTIFIED_PILOT_ROUTE_ID_MISMATCH")
    if str(getattr(candidate, "owner_file", "") or "") != str(pilot.get("sourceOwner") or ""):
        blockers.append("CERTIFIED_PILOT_SOURCE_OWNER_MISMATCH")

    source_owner_marker = str(attrs.get("data-prisma-source-owner") or "").strip()
    if source_owner_marker != Path(str(pilot.get("sourceOwner") or "")).name:
        blockers.append("CERTIFIED_PILOT_SOURCE_OWNER_MARKER_MISMATCH")
    css_owner_marker = str(attrs.get("data-prisma-css-owner") or "").strip()
    if css_owner_marker != Path(str(pilot.get("cssOwner") or "")).name:
        blockers.append("CERTIFIED_PILOT_CSS_OWNER_MARKER_MISMATCH")
    style_sources = {str(getattr(target, "source_file", "") or "") for target in css_targets}
    if str(pilot.get("cssOwner") or "") not in style_sources:
        blockers.append("CERTIFIED_PILOT_CSS_OWNER_NOT_OBSERVED")

    if str(canonical_record.get("runtimeAlias") or "") != runtime_alias:
        blockers.append("CERTIFIED_PILOT_CANONICAL_RUNTIME_MISMATCH")
    if str(canonical_record.get("routeId") or "") != str(pilot.get("routeId") or ""):
        blockers.append("CERTIFIED_PILOT_CANONICAL_ROUTE_MISMATCH")
    if str(canonical_record.get("ownerFile") or "") != str(pilot.get("sourceOwner") or ""):
        blockers.append("CERTIFIED_PILOT_CANONICAL_SOURCE_OWNER_MISMATCH")

    canonical_ui_id = str(canonical_record.get("componentUiId") or "").strip()
    canonical_component_id = str(canonical_record.get("componentId") or "").strip()
    if not canonical_ui_id or not canonical_component_id:
        blockers.append("CERTIFIED_PILOT_CANONICAL_TARGET_INCOMPLETE")
    if alias_id == canonical_ui_id:
        blockers.append("CERTIFIED_PILOT_ALIAS_EQUALS_CANONICAL_ID")

    if blockers:
        return None, _conflict(alias_id, candidate, blockers)

    evidence_refs = [{
        "evidenceType": "CERTIFIED_VISUAL_PILOT_CONTRACT",
        "sourceFile": str(contract["contractPath"]),
        "sourceHash": str(contract["contractHash"]),
    }, {
        "evidenceType": "RENDER_SOURCE",
        "sourceFile": str(getattr(candidate, "render_source_file", "") or ""),
        "sourceHash": str(getattr(candidate, "source_hash", "") or ""),
    }]
    for target in sorted(css_targets, key=lambda item: (str(getattr(item, "source_file", "")), str(getattr(item, "selector", "")))):
        if str(getattr(target, "source_file", "") or "") == str(pilot.get("cssOwner") or ""):
            evidence_refs.append({
                "evidenceType": "STYLE_SOURCE",
                "sourceFile": str(getattr(target, "source_file", "") or ""),
                "sourceHash": str(getattr(target, "source_hash", "") or ""),
                "selector": str(getattr(target, "selector", "") or ""),
            })

    return {
        "aliasId": alias_id,
        "aliasKind": "componentUiId",
        "canonicalComponentUiId": canonical_ui_id,
        "canonicalId": canonical_ui_id,
        "canonicalComponentId": canonical_component_id,
        "canonicalOwnerFile": str(canonical_record.get("ownerFile") or ""),
        "reason": "CERTIFIED_VISUAL_PILOT_CROSSWALK",
        "status": "CERTIFIED",
        "pilotRef": pilot_ref,
        "pilotContractPath": str(contract["contractPath"]),
        "pilotContractHash": str(contract["contractHash"]),
        "evidenceRefs": evidence_refs,
        "pilotTrace": {
            "surfaceId": pilot.get("surfaceId"),
            "routeId": pilot.get("routeId"),
            "runtimeRoute": pilot.get("runtimeRoute"),
            "ownerId": pilot.get("ownerId"),
            "ownerSymbol": pilot.get("ownerSymbol"),
            "regionId": pilot.get("regionId"),
            "slotId": pilot.get("slotId"),
            "componentUiId": pilot.get("componentUiId"),
            "bindingId": pilot.get("bindingId"),
            "layerId": pilot.get("neutralLayerId"),
            "implementationLayerId": pilot.get("implementationLayerId"),
            "adapterId": pilot.get("adapterId"),
            "recipeId": pilot.get("recipeId"),
            "visualStackId": pilot.get("visualStackId"),
            "runtimeSelector": pilot.get("runtimeSelector"),
            "sourceOwner": pilot.get("sourceOwner"),
            "cssOwner": pilot.get("cssOwner"),
        },
        "canonicalTrace": {
            "runtimeAlias": canonical_record.get("runtimeAlias"),
            "surfaceId": canonical_record.get("surfaceId"),
            "routeId": canonical_record.get("routeId"),
            "routePath": canonical_record.get("routePath"),
            "ownerId": canonical_record.get("ownerId"),
            "regionId": canonical_record.get("regionId"),
            "slotId": canonical_record.get("slotId"),
            "componentId": canonical_record.get("componentId"),
            "componentUiId": canonical_record.get("componentUiId"),
            "adapterId": canonical_record.get("adapterId"),
        },
    }, None
