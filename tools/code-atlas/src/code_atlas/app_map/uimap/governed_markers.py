from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

CERTIFIED_PILOT_STATUSES = {
    "EXACT_TARGET_AUTHORIZED_FOR_GOVERNED_APPLICATION",
}

RUNTIME_MARKER_NAMES = {
    "tb": "tablet",
    "pc": "pc",
    "mb": "mobile",
    "web": "web",
    "cl": "chart-lab",
    "cc": "control-center",
    "cmd": "cloud-command-center",
    "shared": "shared-ui",
}

REQUIRED_PILOT_FIELDS = (
    "surfaceId",
    "routeId",
    "runtimeRoute",
    "ownerId",
    "ownerSymbol",
    "regionId",
    "slotId",
    "componentUiId",
    "recipeId",
    "visualStackId",
    "bindingId",
    "adapterId",
    "neutralLayerId",
    "implementationLayerId",
    "sourceOwner",
    "cssOwner",
)

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
    roots = (
        product_root / "apps/terminal-de-venta-system/products",
        product_root / "products",
    )
    seen: set[Path] = set()
    for products in roots:
        if not products.is_dir():
            continue
        for path in sorted(products.glob("*/app/docs/visual-pilots/*.contract.json")):
            resolved = path.resolve()
            if resolved in seen or not resolved.is_file():
                continue
            seen.add(resolved)
            yield resolved


def load_governed_pilot_contracts(product_root: Path) -> dict[str, list[dict[str, Any]]]:
    """Index certified pilot contracts by exact componentUiId.

    The index is evidence, not authority by path name. Only explicitly
    certified statuses enter the index; malformed certified entries remain
    visible so candidate reconciliation can fail closed on them.
    """
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
        component_ui_id = str(pilot.get("componentUiId") or "").strip()
        if not component_ui_id:
            continue
        index.setdefault(component_ui_id, []).append({
            "contractPath": _repo_rel(root, path),
            "contractHash": _sha256(path),
            "contractSchema": payload.get("schema"),
            "contractStatus": payload.get("status"),
            "taskId": payload.get("taskId"),
            "pilot": pilot,
        })
    for component_ui_id in list(index):
        index[component_ui_id] = sorted(
            index[component_ui_id],
            key=lambda row: (str(row.get("contractPath")), str(row.get("contractHash"))),
        )
    return index


def _governed_marker_present(attrs: dict[str, str]) -> bool:
    return bool(
        attrs.get("data-prisma-component-ui-id")
        or attrs.get("data-prisma-binding")
    )


def reconcile_governed_candidate(
    candidate: Any,
    css_targets: list[Any],
    pilot_index: dict[str, list[dict[str, Any]]],
    existing_selector_authority: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, list[str], list[dict[str, Any]]]:
    """Return an exact visual trace only after certified cross-check.

    Raw data-prisma-* markers never grant authority. A candidate is
    reconciled only when its static markers, route, owner source and CSS
    owner all agree with one certified pilot contract. Neutral meaning is
    intentionally absent from the returned trace.
    """
    attrs = dict(getattr(candidate, "data_attributes", {}) or {})
    if not _governed_marker_present(attrs):
        return None, [], []

    component_ui_id = str(attrs.get("data-prisma-component-ui-id") or "").strip()
    if not component_ui_id:
        return None, ["GOVERNED_MARKER_COMPONENT_UI_ID_MISSING"], []

    matches = list(pilot_index.get(component_ui_id) or [])
    if not matches:
        return None, ["GOVERNED_MARKER_AUTHORITY_NOT_FOUND"], []
    if len(matches) != 1:
        return None, ["GOVERNED_MARKER_AUTHORITY_AMBIGUOUS"], [
            {
                "evidenceType": "CERTIFIED_VISUAL_PILOT_CONTRACT",
                "sourceFile": str(row.get("contractPath") or ""),
                "sourceHash": str(row.get("contractHash") or ""),
            }
            for row in matches
        ]

    contract = matches[0]
    pilot = contract.get("pilot") or {}
    evidence = [{
        "evidenceType": "CERTIFIED_VISUAL_PILOT_CONTRACT",
        "sourceFile": str(contract.get("contractPath") or ""),
        "sourceHash": str(contract.get("contractHash") or ""),
    }]
    blockers: list[str] = []

    for field in REQUIRED_PILOT_FIELDS:
        if not str(pilot.get(field) or "").strip():
            blockers.append(f"GOVERNED_PILOT_CONTRACT_INCOMPLETE:{field}")

    for marker, pilot_field in MARKER_TO_PILOT_FIELD.items():
        actual = str(attrs.get(marker) or "").strip()
        expected = str(pilot.get(pilot_field) or "").strip()
        if not actual:
            blockers.append(f"GOVERNED_MARKER_MISSING:{marker}")
        elif actual != expected:
            blockers.append(f"GOVERNED_MARKER_MISMATCH:{marker}")

    runtime_alias = str(getattr(candidate, "runtime_alias", "") or "")
    expected_surface_marker = RUNTIME_MARKER_NAMES.get(runtime_alias, runtime_alias)
    if str(attrs.get("data-prisma-surface") or "").strip() != expected_surface_marker:
        blockers.append("GOVERNED_MARKER_MISMATCH:data-prisma-surface")
    if not str(pilot.get("surfaceId") or "").startswith(f"SURF.{runtime_alias}."):
        blockers.append("GOVERNED_PILOT_SURFACE_RUNTIME_MISMATCH")

    if str(getattr(candidate, "route_path", "") or "") != str(pilot.get("runtimeRoute") or ""):
        blockers.append("GOVERNED_CANDIDATE_ROUTE_PATH_MISMATCH")
    if str(getattr(candidate, "route_id", "") or "") != str(pilot.get("routeId") or ""):
        blockers.append("GOVERNED_CANDIDATE_ROUTE_ID_MISMATCH")
    if str(getattr(candidate, "owner_file", "") or "") != str(pilot.get("sourceOwner") or ""):
        blockers.append("GOVERNED_CANDIDATE_SOURCE_OWNER_MISMATCH")

    source_owner_marker = str(attrs.get("data-prisma-source-owner") or "").strip()
    if source_owner_marker and source_owner_marker != Path(str(pilot.get("sourceOwner") or "")).name:
        blockers.append("GOVERNED_MARKER_MISMATCH:data-prisma-source-owner")
    css_owner_marker = str(attrs.get("data-prisma-css-owner") or "").strip()
    if css_owner_marker and css_owner_marker != Path(str(pilot.get("cssOwner") or "")).name:
        blockers.append("GOVERNED_MARKER_MISMATCH:data-prisma-css-owner")

    style_sources = {
        str(getattr(target, "source_file", "") or "")
        for target in css_targets
    }
    if str(pilot.get("cssOwner") or "") not in style_sources:
        blockers.append("GOVERNED_CANDIDATE_CSS_OWNER_MISMATCH")

    if existing_selector_authority:
        authority_pairs = {
            "layerId": "neutralLayerId",
            "implementationLayerId": "implementationLayerId",
            "bindingId": "bindingId",
        }
        for authority_field, pilot_field in authority_pairs.items():
            existing = existing_selector_authority.get(authority_field)
            expected = pilot.get(pilot_field)
            if existing and expected and str(existing) != str(expected):
                blockers.append(f"GOVERNED_MARKER_CENTRAL_AUTHORITY_MISMATCH:{authority_field}")

    if blockers:
        return None, sorted(set(blockers)), evidence

    return {
        "surfaceId": str(pilot["surfaceId"]),
        "routeId": str(pilot["routeId"]),
        "ownerId": str(pilot["ownerId"]),
        "ownerSymbol": str(pilot["ownerSymbol"]),
        "regionId": str(pilot["regionId"]),
        "slotId": str(pilot["slotId"]),
        "componentUiId": str(pilot["componentUiId"]),
        "bindingId": str(pilot["bindingId"]),
        "layerId": str(pilot["neutralLayerId"]),
        "implementationLayerId": str(pilot["implementationLayerId"]),
        "adapterId": str(pilot["adapterId"]),
        "recipeId": str(pilot["recipeId"]),
        "visualStackId": str(pilot["visualStackId"]),
        "contractPath": str(contract["contractPath"]),
        "contractHash": str(contract["contractHash"]),
    }, [], evidence
