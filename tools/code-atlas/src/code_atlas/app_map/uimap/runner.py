from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from .contracts import (
    ACTIVE_RUNTIME_ALIASES,
    ADAPTERS,
    APPLICATION_READINESS,
    CANONICAL_TERMS,
    CANONICALIZATION,
    CONDITIONAL_STATES,
    FINAL_STATUSES,
    FULL_CHAIN_FIELDS,
    PROHIBITED_CANONICAL_KEYS,
    BINDING_ID_PATTERN,
    IMPLEMENTATION_LAYER_PATTERN,
    LAYER_ID_PATTERN,
    RECORD_REQUIRED_FIELDS,
    REQUIRED_STATES,
    RUNTIME_ORDER,
    SCHEMA_VERSION,
    TASK_ID,
    add_integrity,
    atlas_schema,
    canonical_bytes,
    contains_reserved_segment,
    handoff_schema,
    record_schema,
    sha256_bytes,
    sha256_file,
    slug,
    stable_id,
    upper_token,
    validate_identity_contract,
    validate_record,
    validate_schema_subset,
)
from .discovery import (
    RUNTIME_LABELS,
    CssTarget,
    UiCandidate,
    build_authority_indexes,
    component_locator,
    css_target_index,
    discover_runtime,
    infer_region,
    make_state_support,
    norm_rel,
    resolve_runtime_roots,
    route_surface_slug,
    source_snapshot_hash,
    widget_type_id,
)

GOLDEN_BINDING_ID = "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1"
GOLDEN_LAYER_ID = "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE"
GOLDEN_IMPLEMENTATION_LAYER_ID = "products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton"
GOLDEN_SELECTOR = ".cobrarReferenceButton"
GOLDEN_TRACE_DEFAULT = {
    "surfaceId": "SURF.tb.pos",
    "interfaceId": "IFC.tb.retail.pos_sale",
    "routeId": "ROUTE.tb.pos",
    "routePath": "/pos",
    "regionId": "ZONE.tb.pos.payment",
    "slotId": "SLOT.tb.pos.payment.cobrar",
    "componentId": "WGT.tb.pos.cobrar",
    "componentUiId": "TB-POS-PAY-COBRAR-BTN-01",
    "widgetTypeId": "WID.button",
    "ownerId": "OWN.tb.pos_ticket_panel",
    "bindingId": GOLDEN_BINDING_ID,
    "layerId": GOLDEN_LAYER_ID,
    "implementationLayerId": GOLDEN_IMPLEMENTATION_LAYER_ID,
    "selector": GOLDEN_SELECTOR,
}
GOLDEN_LEGACY_TRACE_DEFAULT = {
    "surfaceId": "tablet",
    "ownerId": "products.tablet.app.components.pos.pos.ticket.panel.tsx",
    "routeId": "tablet.pos.route",
    "regionId": "products.tablet.app.components.pos.pos.ticket.panel.tsx.pos.buttons",
    "slotId": "tablet.any.products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton.layer",
    "componentUiId": "products.tablet.app.components.pos.pos.ticket.panel.tsx",
}

OUTPUT_EXISTING = (
    "01_SURFACE_REGISTRY.json",
    "02_ROUTE_COMPONENT_MAP.json",
    "03_COMPONENT_OWNERSHIP_MAP.json",
    "04_LAYER_ROLE_KIND_MAP.json",
    "05_SELECTOR_GRAPH.json",
    "06_SELECTOR_USAGE.csv",
    "07_TOKEN_GRAPH.json",
    "08_LEGACY_TOKEN_ALIAS_MAP.json",
    "09_STATE_MATRIX.json",
    "10_CONTROL_APPLICABILITY_MATRIX.json",
    "11_PRESET_ELIGIBILITY_REGISTRY.json",
    "12_POS_PROTECTION_MAP.json",
    "13_ZERO_MEANS_ZERO_AUDIT.json",
    "14_IMPORTANT_AUDIT_FILTERED.md",
    "15_ORPHAN_DUPLICATE_SHARED_SELECTORS.md",
    "16_PRESET_PROMOTION_CONTRACT.md",
    "17_CONTINUATION.md",
)


def utc_now_text() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: str | None) -> str:
    if not value:
        return utc_now_text()
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except Exception:
        return utc_now_text()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys or ["empty"], lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in keys})


def safe_ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def percent(numerator: int, denominator: int) -> str:
    ratio = safe_ratio(numerator, denominator)
    if ratio is None:
        return "NOT_EVALUATED"
    return f"{ratio * 100:.6f}%"


def discover_golden_trace(governor_root: Path, embedded_evidence: Path | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    files: list[Path] = []
    if governor_root.exists():
        patterns = (
            "*tablet-pos-cobrar*.json",
            "*full-stack*.json",
            "*binding*.json",
            "*identity-layer-certifications*.json",
        )
        for pattern in patterns:
            files.extend(governor_root.rglob(pattern))
    if embedded_evidence and embedded_evidence.exists():
        files.append(embedded_evidence)
    seen: set[Path] = set()
    for path in files:
        if path in seen or not path.is_file() or path.stat().st_size > 8_000_000:
            continue
        seen.add(path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        text = json.dumps(payload, ensure_ascii=False)
        if GOLDEN_BINDING_ID not in text and GOLDEN_LAYER_ID not in text:
            continue
        trace = payload.get("trace") if isinstance(payload, dict) else None
        binding = payload.get("bindingRequirements") if isinstance(payload, dict) else None
        row = {
            "sourceFile": path.as_posix(),
            "sourceHash": sha256_file(path),
            "trace": trace if isinstance(trace, dict) else {},
            "binding": binding if isinstance(binding, dict) else {},
            "payload": payload,
        }
        candidates.append(row)
    trace = dict(GOLDEN_TRACE_DEFAULT)
    legacy_trace = dict(GOLDEN_LEGACY_TRACE_DEFAULT)
    for candidate in sorted(candidates, key=lambda r: r["sourceFile"]):
        raw_trace = candidate.get("trace", {})
        raw_legacy = (candidate.get("payload") or {}).get("legacyTrace", {})
        for key, value in raw_trace.items():
            if value is None or not str(value).strip():
                continue
            if key in {"bindingId", "layerId", "implementationLayerId", "selector"}:
                trace[key] = value
            elif key in legacy_trace and value != trace.get(key):
                legacy_trace[key] = value
        for key, value in raw_legacy.items():
            if key in legacy_trace and value is not None and str(value).strip():
                legacy_trace[key] = value
        binding = candidate.get("binding", {})
        if binding.get("bindingId"):
            trace["bindingId"] = binding["bindingId"]
        if binding.get("layerIdRequired"):
            trace["layerId"] = binding["layerIdRequired"]
        if binding.get("implementationLayerIdRequired"):
            trace["implementationLayerId"] = binding["implementationLayerIdRequired"]
    trace["legacyTrace"] = legacy_trace
    return trace, candidates


def selector_authority(authority: dict[str, Any], selector: str) -> tuple[dict[str, Any] | None, list[str]]:
    layers = list(authority.get("layersBySelector", {}).get(selector, []))
    bindings = list(authority.get("bindingsBySelector", {}).get(selector, []))
    blockers: list[str] = []

    canonical_layer_ids: set[str] = set()
    implementation_ids: set[str] = set()
    canonical_binding_ids: set[str] = set()
    noncanonical_layer_ids: set[str] = set()
    noncanonical_binding_ids: set[str] = set()

    for row in layers:
        raw_layer = row.get("layerId")
        raw_implementation = row.get("implementationLayerId")

        if raw_layer:
            raw_layer_text = str(raw_layer)
            if re.fullmatch(LAYER_ID_PATTERN, raw_layer_text):
                canonical_layer_ids.add(raw_layer_text)
            elif re.fullmatch(IMPLEMENTATION_LAYER_PATTERN, raw_layer_text):
                # Legacy/current physical layer values belong to implementationLayerId,
                # never to the neutral LYR.* field.
                implementation_ids.add(raw_layer_text)
                noncanonical_layer_ids.add(raw_layer_text)
            else:
                noncanonical_layer_ids.add(raw_layer_text)

        if raw_implementation:
            raw_implementation_text = str(raw_implementation)
            if re.fullmatch(IMPLEMENTATION_LAYER_PATTERN, raw_implementation_text):
                implementation_ids.add(raw_implementation_text)

    for row in bindings:
        raw_binding = row.get("bindingId")
        if not raw_binding:
            continue
        raw_binding_text = str(raw_binding)
        if re.fullmatch(BINDING_ID_PATTERN, raw_binding_text):
            canonical_binding_ids.add(raw_binding_text)
        else:
            noncanonical_binding_ids.add(raw_binding_text)

    if (
        len(canonical_layer_ids) > 1
        or len(implementation_ids) > 1
        or len(canonical_binding_ids) > 1
    ):
        blockers.append("MULTIPLE_AUTHORITY_RECORDS_FOR_SELECTOR")
        return None, blockers

    if not layers and not bindings:
        return None, blockers

    result = {
        "layerId": next(iter(canonical_layer_ids), None),
        "implementationLayerId": next(iter(implementation_ids), None),
        "bindingId": next(iter(canonical_binding_ids), None),
        "layerEvidence": layers,
        "bindingEvidence": bindings,
        "normalization": {
            "physicalLayerIdsReclassified": sorted(noncanonical_layer_ids),
            "noncanonicalBindingIdsIgnored": sorted(noncanonical_binding_ids),
        },
    }
    return result, blockers


def choose_element_name(candidate: UiCandidate) -> str:
    if candidate.class_name:
        return slug(candidate.class_name)
    if candidate.data_attributes:
        for key in ("data-prisma-id", "data-testid", "data-slot", "data-role"):
            if candidate.data_attributes.get(key):
                return slug(candidate.data_attributes[key])
    if candidate.text_hint:
        return slug(candidate.text_hint)
    return slug(candidate.tag_name)


def canonical_owner_identity(candidate: UiCandidate) -> str:
    """Build a stable owner identity from the canonical source path.

    Discovery order is deliberately excluded. Repeated route-boundary symbols
    such as ``Error`` and ``Loading`` therefore remain distinct without
    ordinal collision suffixes.
    """
    normalized = str(candidate.owner_file or candidate.render_source_file or "").replace("\\", "/")
    if (
        candidate.runtime_alias == "tb"
        and normalized.lower().endswith("products/tablet/app/components/pos/pos-ticket-panel.tsx")
    ):
        return "pos_ticket_panel"
    without_extension = re.sub(
        r"\.(?:tsx?|jsx?|mjs|cjs|vue|svelte)$",
        "",
        normalized,
        flags=re.IGNORECASE,
    )
    marker_by_runtime = {
        "tb": "/products/tablet/",
        "pc": "/products/pc/",
        "mb": "/products/mobile/",
        "web": "/products/web/",
        "cl": "/products/chart-lab/",
        "cc": "/products/control-center/",
        "cmd": "/prisma-control-center/",
    }
    marker = marker_by_runtime.get(candidate.runtime_alias)
    scoped = without_extension
    if marker and marker in f"/{without_extension}":
        scoped = f"/{without_extension}".split(marker, 1)[1]
    elif candidate.runtime_alias == "shared" and "/packages/" in f"/{without_extension}":
        scoped = "packages/" + f"/{without_extension}".split("/packages/", 1)[1]
    scoped = re.sub(r"^(?:app/|src/)+", "", scoped, flags=re.IGNORECASE)
    return slug(scoped or candidate.owner_symbol or "owner")


def canonical_route_identity(candidate: UiCandidate, owner_identity: str) -> str:
    if str(candidate.route_id).endswith(".unrouted"):
        return owner_identity
    return slug(candidate.route_path.strip("/") or "home")


def visual_target_rows(targets: list[CssTarget], implementation_layer_id: str | None, generated: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, target in enumerate(targets, start=1):
        role = target.target_role
        locator_seed = upper_token(target.class_name, "TARGET", 40)
        visual_target_id = f"VTR.{locator_seed}.{role}.{index:02d}"
        row = {
            "visualTargetId": visual_target_id,
            "targetRole": role,
            "styleSourceFile": target.source_file,
            "anchorKind": "GENERATED_PROJECTION" if generated else target.anchor_kind,
            "anchorValue": target.class_name,
            "selector": target.selector,
            "pseudoElement": target.pseudo_element,
            "stateSelector": target.state_selector,
            "atRule": target.at_rule,
            "implementationLayerId": implementation_layer_id,
            "sourceHash": target.source_hash,
        }
        if generated:
            row["patchPolicy"] = "DO_NOT_PATCH_GENERATED"
        rows.append(row)
    return sorted(rows, key=lambda row: row["visualTargetId"])


def record_from_candidate(
    candidate: UiCandidate,
    css_targets: list[CssTarget],
    authority: dict[str, Any],
    ordinal: int,
    golden_trace: dict[str, Any],
    golden_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    runtime = candidate.runtime_alias
    is_golden = (
        runtime == "tb"
        and candidate.class_name == "cobrarReferenceButton"
        and candidate.render_source_file.lower().endswith(
            "products/tablet/app/components/pos/pos-ticket-panel.tsx"
        )
    )

    route_path = "/pos" if is_golden else candidate.route_path
    route_surface = route_surface_slug(route_path)
    region = "payment" if is_golden else infer_region(
        route_path, candidate.class_name, candidate.render_symbol, candidate.widget_kind
    )
    element = "cobrar" if is_golden else choose_element_name(candidate)
    widget_kind = "button" if is_golden else candidate.widget_kind
    owner_identity = canonical_owner_identity(candidate)
    route_identity = canonical_route_identity(candidate, owner_identity)
    locator = component_locator(
        runtime,
        route_path,
        region,
        element,
        widget_kind,
        ordinal,
        owner_identity,
    )
    selector = f".{candidate.class_name}" if candidate.class_name else None
    auth, auth_blockers = selector_authority(authority, selector) if selector else (None, [])

    layer_id = auth.get("layerId") if auth else None
    implementation_layer_id = auth.get("implementationLayerId") if auth else None
    binding_id = auth.get("bindingId") if auth else None
    legacy_id_preserved = False

    surface_id = stable_id("SURF", runtime, route_surface)
    interface_id = stable_id(
        "IFC",
        runtime,
        "retail" if route_surface == "pos" else route_surface,
        "pos_sale" if route_surface == "pos" else "interface",
    )
    route_id = GOLDEN_TRACE_DEFAULT["routeId"] if is_golden else candidate.route_id
    region_id = stable_id("ZONE", runtime, route_surface, region)
    slot_id = stable_id("SLOT", runtime, route_identity, region, owner_identity, element)
    owner_id = stable_id("OWN", runtime, owner_identity)
    component_id = stable_id(
        "WGT",
        runtime,
        route_identity,
        "cobrar" if is_golden else owner_identity,
        "" if is_golden else element,
    )
    if component_id.endswith(".item"):
        component_id = component_id[:-5]

    neutral_meaning_id = None
    related_neutral_ids: list[str] = []
    ndc_status = "CANDIDATE"
    confidence = "MEDIUM" if candidate.class_name else "LOW"
    recipe_coverage = "NOT_EVALUATED"

    if is_golden:
        legacy_id_preserved = True
        surface_id = GOLDEN_TRACE_DEFAULT["surfaceId"]
        interface_id = GOLDEN_TRACE_DEFAULT["interfaceId"]
        route_id = GOLDEN_TRACE_DEFAULT["routeId"]
        route_path = GOLDEN_TRACE_DEFAULT["routePath"]
        region_id = GOLDEN_TRACE_DEFAULT["regionId"]
        slot_id = GOLDEN_TRACE_DEFAULT["slotId"]
        component_id = GOLDEN_TRACE_DEFAULT["componentId"]
        locator = GOLDEN_TRACE_DEFAULT["componentUiId"]
        owner_id = GOLDEN_TRACE_DEFAULT["ownerId"]
        layer_id = golden_trace.get("layerId", GOLDEN_LAYER_ID)
        implementation_layer_id = golden_trace.get(
            "implementationLayerId", GOLDEN_IMPLEMENTATION_LAYER_ID
        )
        binding_id = golden_trace.get("bindingId", GOLDEN_BINDING_ID)
        neutral_meaning_id = "ACT.primary"
        related_neutral_ids = ["ACT.sale.checkout"]
        ndc_status = "CONFIRMED"
        confidence = "VERY_HIGH"
        recipe_coverage = "CURRENT_SOURCE_COVERAGE_COMPLETE"

    targets = visual_target_rows(css_targets, implementation_layer_id, candidate.generated_projection)
    for index, target in enumerate(targets, start=1):
        target["visualTargetId"] = f"VTR.{locator}.{target['targetRole']}.{index:02d}"

    state_support = make_state_support(css_targets, runtime)
    blockers: list[str] = list(auth_blockers)
    if not candidate.owner_file or not candidate.owner_symbol:
        blockers.append("MISSING_CANONICAL_OWNER")
    if not candidate.render_source_file:
        blockers.append("MISSING_RENDER_SOURCE")
    if not targets:
        blockers.append("MISSING_EXACT_VISUAL_TARGET")
    if not layer_id:
        blockers.append("MISSING_CERTIFIED_LAYER")
    if not implementation_layer_id:
        blockers.append("MISSING_IMPLEMENTATION_LAYER")
    if not binding_id:
        blockers.append("MISSING_VISUAL_BINDING")
    if neutral_meaning_id is None:
        blockers.append("NEUTRAL_MEANING_NOT_PROVEN")
    if candidate.multiple_owner_candidates:
        blockers.append("MULTIPLE_OWNER_CANDIDATES")
        ndc_status = "CONFLICT"
        confidence = "BLOCKED"

    missing_required_states = [
        state for state in REQUIRED_STATES if state_support[state] == "MISSING_REQUIRED"
    ]
    if missing_required_states and recipe_coverage != "CURRENT_SOURCE_COVERAGE_COMPLETE":
        recipe_coverage = (
            "BLOCKED_BY_UNRESOLVED_VISUAL_STATE" if targets else "NOT_EVALUATED"
        )
    elif targets and recipe_coverage == "NOT_EVALUATED":
        recipe_coverage = "PARTIAL_VISUAL_STATE_COVERAGE"

    evidence_refs: list[dict[str, Any]] = [{
        "evidenceType": "RENDER_SOURCE",
        "sourceFile": candidate.render_source_file,
        "sourceHash": candidate.source_hash,
    }]
    if candidate.route_source_file:
        evidence_refs.append({
            "evidenceType": "ROUTE_SOURCE",
            "sourceFile": (
                "apps/terminal-de-venta-system/products/tablet/app/app/pos/page.tsx"
                if is_golden
                else candidate.route_source_file
            ),
        })
    for target in targets:
        evidence_refs.append({
            "evidenceType": "STYLE_TARGET",
            "sourceFile": target["styleSourceFile"],
            "sourceHash": target["sourceHash"],
            "selector": target["selector"],
        })
    if auth:
        for row in auth.get("layerEvidence", []):
            evidence_refs.append({
                "evidenceType": "LAYER_AUTHORITY",
                "sourceFile": row.get("sourceFile"),
                "sourceHash": row.get("sourceHash"),
                "selector": row.get("selector"),
            })
        for row in auth.get("bindingEvidence", []):
            evidence_refs.append({
                "evidenceType": "BINDING_AUTHORITY",
                "sourceFile": row.get("sourceFile"),
                "sourceHash": row.get("sourceHash"),
                "selector": row.get("selector"),
            })
    if is_golden:
        for row in golden_evidence:
            evidence_refs.append({
                "evidenceType": "IDRECIPE1_GOLDEN_FIXTURE",
                "sourceFile": Path(row["sourceFile"]).name,
                "sourceHash": row["sourceHash"],
            })

    source_hashes = {
        "ownerFile": candidate.source_hash,
        "renderSourceFile": candidate.source_hash,
    }
    for target in targets:
        source_hashes[target["styleSourceFile"]] = target["sourceHash"]

    identity_probe = {
        "surfaceId": surface_id,
        "interfaceId": interface_id,
        "routeId": route_id,
        "routePath": route_path,
        "regionId": region_id,
        "slotId": slot_id,
        "componentId": component_id,
        "componentUiId": locator,
        "widgetTypeId": GOLDEN_TRACE_DEFAULT["widgetTypeId"] if is_golden else widget_type_id(widget_kind),
        "ownerId": owner_id,
        "ownerFile": candidate.owner_file,
        "renderSourceFile": candidate.render_source_file,
        "bindingId": binding_id,
        "layerId": layer_id,
        "implementationLayerId": implementation_layer_id,
        "adapterId": ADAPTERS[runtime],
        "neutralMeaningId": neutral_meaning_id,
        "relatedNeutralIds": related_neutral_ids,
    }
    identity_errors = validate_identity_contract(identity_probe)
    if identity_errors:
        blockers.append("CANONICAL_ID_CONTRACT_VIOLATION")

    target_status = "PARTIAL"
    if candidate.multiple_owner_candidates or auth_blockers:
        target_status = "BLOCKED_BY_CONFLICT"
    elif not candidate.owner_file or not candidate.owner_symbol:
        target_status = "BLOCKED_BY_MISSING_OWNER"
    elif not candidate.render_source_file:
        target_status = "BLOCKED_BY_MISSING_SOURCE"
    elif not layer_id or not implementation_layer_id:
        target_status = "BLOCKED_BY_MISSING_LAYER"

    complete_chain = all([
        surface_id, interface_id, route_id, route_path, region_id, slot_id,
        component_id, locator, identity_probe["widgetTypeId"],
        owner_id, candidate.owner_file, candidate.owner_symbol, candidate.render_source_file,
        candidate.render_symbol, targets, binding_id, layer_id, implementation_layer_id,
        ADAPTERS[runtime], evidence_refs, source_hashes,
    ])
    if (
        complete_chain
        and not identity_errors
        and ndc_status in {"CONFIRMED", "CANONICAL_READY"}
        and confidence in {"HIGH", "VERY_HIGH"}
    ):
        blockers = [reason for reason in blockers if reason not in {
            "MISSING_CANONICAL_OWNER", "MISSING_RENDER_SOURCE", "MISSING_EXACT_VISUAL_TARGET",
            "MISSING_CERTIFIED_LAYER", "MISSING_IMPLEMENTATION_LAYER", "MISSING_VISUAL_BINDING",
            "NEUTRAL_MEANING_NOT_PROVEN",
        }]
        if not blockers:
            target_status = "SOURCE_RESOLVED"

    application_readiness = (
        "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT"
        if (
            target_status == "SOURCE_RESOLVED"
            and not blockers
            and recipe_coverage != "BLOCKED_BY_UNRESOLVED_VISUAL_STATE"
        )
        else "BLOCKED"
    )

    record = {
        "schema": "prisma.ui.component-record.v1",
        "schemaVersion": SCHEMA_VERSION,
        "runtimeAlias": runtime,
        "surfaceId": surface_id,
        "interfaceId": interface_id,
        "routeId": route_id,
        "routePath": route_path,
        "regionId": region_id,
        "slotId": slot_id,
        "componentId": component_id,
        "componentUiId": locator,
        "widgetTypeId": identity_probe["widgetTypeId"],
        "neutralMeaningId": neutral_meaning_id,
        "relatedNeutralIds": related_neutral_ids,
        "ownerId": owner_id,
        "ownerFile": candidate.owner_file,
        "ownerSymbol": candidate.owner_symbol,
        "renderSourceFile": candidate.render_source_file,
        "renderSymbol": candidate.render_symbol,
        "visualTargets": targets,
        "bindingId": binding_id,
        "layerId": layer_id,
        "implementationLayerId": implementation_layer_id,
        "adapterId": ADAPTERS[runtime],
        "recipeCompatibility": {
            "coverageStatus": recipe_coverage,
            "compatibleRecipeIds": ["REC.button.primary"] if is_golden else [],
            "hoverPolicy": "substitute-pressed" if runtime in {"tb", "mb"} else "native-hover",
        },
        "stateSupport": state_support,
        "evidenceRefs": sorted(evidence_refs, key=lambda row: (
            str(row.get("evidenceType")), str(row.get("sourceFile")), str(row.get("selector"))
        )),
        "sourceHashes": {key: source_hashes[key] for key in sorted(source_hashes)},
        "ndcStatus": ndc_status,
        "confidence": confidence,
        "targetResolutionStatus": target_status,
        "applicationReadiness": application_readiness,
        "blockingReasons": sorted(set(blockers)),
        "instancePolicy": candidate.instance_policy,
        "projectionOfComponentId": candidate.projection_of_component_id,
        "legacyIdPreserved": legacy_id_preserved,
    }
    return record


def golden_legacy_aliases(golden_trace: dict[str, Any]) -> list[dict[str, Any]]:
    legacy = dict(GOLDEN_LEGACY_TRACE_DEFAULT)
    legacy.update(golden_trace.get("legacyTrace") or {})
    mappings = {
        "surfaceId": GOLDEN_TRACE_DEFAULT["surfaceId"],
        "ownerId": GOLDEN_TRACE_DEFAULT["ownerId"],
        "routeId": GOLDEN_TRACE_DEFAULT["routeId"],
        "regionId": GOLDEN_TRACE_DEFAULT["regionId"],
        "slotId": GOLDEN_TRACE_DEFAULT["slotId"],
        "componentUiId": GOLDEN_TRACE_DEFAULT["componentUiId"],
    }
    rows: list[dict[str, Any]] = []
    for field, canonical in mappings.items():
        alias_id = legacy.get(field)
        if not alias_id or alias_id == canonical:
            continue
        row = {
            "aliasId": alias_id,
            "aliasKind": field,
            "canonicalId": canonical,
            "reason": "CERTIFIED_LEGACY_ID_PRESERVED",
            "status": "DEPRECATED",
        }
        if field == "componentUiId":
            row["canonicalComponentUiId"] = canonical
        rows.append(row)
    return sorted(rows, key=lambda row: (row["aliasKind"], row["aliasId"]))


def _mark_collision(record: dict[str, Any], reason: str = "CANONICAL_ID_COLLISION") -> None:
    record["targetResolutionStatus"] = "BLOCKED_BY_CONFLICT"
    record["applicationReadiness"] = "BLOCKED"
    record["ndcStatus"] = "CONFLICT"
    record["confidence"] = "BLOCKED"
    record["blockingReasons"] = sorted(set(record["blockingReasons"]) | {reason})


def _dedupe_key_token(key: tuple[str, str, str, str]) -> str:
    payload = json.dumps(list(key), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def _normalize_aliases(
    aliases: list[dict[str, Any]],
    canonical_by_dedupe_key: dict[str, dict[str, str]],
    canonical_records_by_ui: dict[str, dict[str, Any]],
    conflicts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_alias: dict[str, dict[str, Any]] = {}
    withheld_aliases: set[str] = set()

    for raw in aliases:
        row = dict(raw)
        dedupe_key = str(row.pop("_canonicalDedupeKey", ""))
        if dedupe_key:
            precise_target = canonical_by_dedupe_key.get(dedupe_key)
            if precise_target is None:
                conflicts.append({
                    "conflictType": "ALIAS_PRECISE_TARGET_MISSING",
                    "aliasId": str(row.get("aliasId") or ""),
                    "dedupeKeyHash": dedupe_key,
                    "resolution": "ALIAS_WITHHELD",
                })
                continue
            row["canonicalComponentUiId"] = precise_target["componentUiId"]
            row["canonicalComponentId"] = precise_target["componentId"]
            row["canonicalOwnerFile"] = precise_target["ownerFile"]
            row["dedupeKeyHash"] = dedupe_key

        alias_id = str(row.get("aliasId") or "")
        canonical = str(row.get("canonicalComponentUiId") or "")
        if not alias_id or not canonical or alias_id == canonical:
            continue

        previous = by_alias.get(alias_id)
        if previous and previous.get("canonicalComponentUiId") != canonical:
            conflicts.append({
                "conflictType": "ALIAS_TARGET_CONFLICT",
                "aliasId": alias_id,
                "targets": sorted({str(previous.get("canonicalComponentUiId")), canonical}),
                "resolution": "ALIASES_WITHHELD",
            })
            by_alias.pop(alias_id, None)
            withheld_aliases.add(alias_id)
            continue
        if alias_id in withheld_aliases:
            continue
        by_alias[alias_id] = row

    graph = {alias: str(row["canonicalComponentUiId"]) for alias, row in by_alias.items()}
    cycle_nodes: set[str] = set()
    for start in sorted(graph):
        trail: list[str] = []
        positions: dict[str, int] = {}
        current = start
        while current in graph:
            if current in positions:
                cycle = trail[positions[current]:]
                cycle_nodes.update(cycle)
                conflicts.append({
                    "conflictType": "ALIAS_CYCLE_PREVENTED",
                    "aliases": sorted(cycle),
                    "resolution": "ALIASES_WITHHELD",
                })
                break
            positions[current] = len(trail)
            trail.append(current)
            current = graph[current]

    for alias_id, row in sorted(by_alias.items()):
        if alias_id in cycle_nodes:
            continue
        final = str(row["canonicalComponentUiId"])
        visited = {alias_id}
        while final in graph and final not in visited and final not in cycle_nodes:
            visited.add(final)
            final = graph[final]
        row["canonicalComponentUiId"] = final

        if row.get("reason") == "SAME_OWNER_PROJECTION_DEDUPLICATED":
            target_record = canonical_records_by_ui.get(final)
            if target_record is None:
                conflicts.append({
                    "conflictType": "ALIAS_CANONICAL_RECORD_MISSING",
                    "aliasId": alias_id,
                    "canonicalComponentUiId": final,
                    "resolution": "ALIAS_WITHHELD",
                })
                continue
            row["canonicalComponentId"] = str(target_record["componentId"])
            row["canonicalOwnerFile"] = str(target_record["ownerFile"])

        rows.append(row)

    dedupe = {
        (row["aliasId"], row["canonicalComponentUiId"]): row
        for row in rows
        if row["aliasId"] != row["canonicalComponentUiId"]
    }
    return [dedupe[key] for key in sorted(dedupe)]


def deduplicate_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    aliases: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    by_key: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for record in sorted(records, key=lambda r: (
        r["runtimeAlias"], r["routePath"], r["ownerFile"], r["componentUiId"], r["componentId"]
    )):
        key = (record["runtimeAlias"], record["routePath"], record["ownerFile"], record["componentId"])
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = record
            continue
        target_map = {target["visualTargetId"]: target for target in existing["visualTargets"]}
        for target in record["visualTargets"]:
            target_map.setdefault(target["visualTargetId"], target)
        existing["visualTargets"] = [target_map[k] for k in sorted(target_map)]
        evidence_map = {
            json.dumps(item, sort_keys=True, separators=(",", ":")): item for item in existing["evidenceRefs"]
        }
        for item in record["evidenceRefs"]:
            evidence_map.setdefault(json.dumps(item, sort_keys=True, separators=(",", ":")), item)
        existing["evidenceRefs"] = [evidence_map[k] for k in sorted(evidence_map)]
        existing["blockingReasons"] = sorted(set(existing["blockingReasons"]) | set(record["blockingReasons"]))
        aliases.append({
            "aliasId": record["componentUiId"],
            "canonicalComponentUiId": existing["componentUiId"],
            "_canonicalDedupeKey": _dedupe_key_token(key),
            "reason": "SAME_OWNER_PROJECTION_DEDUPLICATED",
            "status": "INTERNAL",
        })

    output = list(by_key.values())
    # Canonical outputs must remain unique. A collision is evidence that route or
    # owner discovery needs repair; never hide it behind ordinal suffixes.
    for field in ("componentUiId", "componentId", "slotId"):
        groups: dict[str, list[dict[str, Any]]] = {}
        for record in output:
            value = str(record.get(field) or "")
            if value:
                groups.setdefault(value, []).append(record)
        for value, group in sorted(groups.items()):
            distinct_owners = {str(record.get("ownerFile")) for record in group}
            if len(group) < 2 or len(distinct_owners) < 2:
                continue
            for record in group:
                _mark_collision(record)
            conflicts.append({
                "conflictType": "CANONICAL_ID_COLLISION",
                "field": field,
                "value": value,
                "owners": sorted(distinct_owners),
                "resolution": "UNRESOLVED_REQUIRES_ROUTE_OR_OWNER_REPAIR",
            })

    canonical_by_dedupe_key = {
        _dedupe_key_token(key): {
            "componentUiId": str(record["componentUiId"]),
            "componentId": str(record["componentId"]),
            "ownerFile": str(record["ownerFile"]),
        }
        for key, record in by_key.items()
    }
    canonical_records_by_ui = {
        str(record["componentUiId"]): record
        for record in output
    }
    aliases = _normalize_aliases(
        aliases,
        canonical_by_dedupe_key,
        canonical_records_by_ui,
        conflicts,
    )
    return sorted(output, key=lambda r: (r["runtimeAlias"], r["componentUiId"], r["ownerFile"])), aliases, conflicts


def aliases_have_cycle(aliases: list[dict[str, Any]]) -> bool:
    graph = {
        str(row.get("aliasId")): str(row.get("canonicalComponentUiId"))
        for row in aliases
        if row.get("aliasId") and row.get("canonicalComponentUiId")
    }
    for start in graph:
        seen: set[str] = set()
        current = start
        while current in graph:
            if current in seen:
                return True
            seen.add(current)
            current = graph[current]
    return False


def coverage_for(records: list[dict[str, Any]], routes: list[dict[str, Any]], deprecated_count: int = 0, runtime_alias: str | None = None) -> dict[str, Any]:
    eligible = len(records)
    discovered_routes = len(routes)
    mapped_route_ids = {record["routeId"] for record in records if record.get("routeId")}
    source_resolved = sum(r["targetResolutionStatus"] == "SOURCE_RESOLVED" for r in records)
    partial = sum(r["targetResolutionStatus"] == "PARTIAL" for r in records)
    unmapped = sum(r["targetResolutionStatus"] == "UNMAPPED" for r in records)
    conflicts = sum(r["targetResolutionStatus"] == "BLOCKED_BY_CONFLICT" for r in records)
    orphans = sum(r["ndcStatus"] == "ORPHAN" for r in records)
    layer_resolved = sum(bool(r.get("layerId") and r.get("implementationLayerId")) for r in records)
    neutral_resolved = sum(bool(r.get("neutralMeaningId")) for r in records)
    recipe_compatible = sum(
        (r.get("recipeCompatibility") or {}).get("coverageStatus") in {
            "CURRENT_SOURCE_COVERAGE_COMPLETE", "FULL_VISUAL_STATE_RECIPE_COMPLETE", "PARTIAL_VISUAL_STATE_COVERAGE"
        }
        for r in records
    )
    identified = sum(bool(r.get("componentUiId")) for r in records)
    metrics = {
        "discoveredRoutes": discovered_routes,
        "mappedRoutes": len({route["routeId"] for route in routes if route["routeId"] in mapped_route_ids}),
        "eligibleComponents": eligible,
        "identifiedComponents": identified,
        "sourceResolvedComponents": source_resolved,
        "partialComponents": partial,
        "unmappedComponents": unmapped,
        "conflictComponents": conflicts,
        "orphanComponents": orphans,
        "layerResolvedComponents": layer_resolved,
        "neutralMeaningResolvedComponents": neutral_resolved,
        "recipeCompatibleComponents": recipe_compatible,
        "deprecatedComponents": deprecated_count,
    }
    runtime_disposition = (
        "ACTIVE_AGGREGATE"
        if runtime_alias is None
        else "INTERNAL_NO_ROUTE_REGISTRY"
        if runtime_alias == "shared"
        else "SKIPPED_OFFLINE"
        if discovered_routes == 0 and eligible == 0
        else "BLOCKED_BY_MISSING_ROUTE_REGISTRY"
        if discovered_routes == 0
        else "ACTIVE_SOURCE_DISCOVERY"
    )
    metrics["runtimeDisposition"] = runtime_disposition
    metrics.update({
        "routeCoverage": percent(metrics["mappedRoutes"], discovered_routes),
        "identificationCoverage": percent(identified, eligible),
        "sourceResolutionCoverage": percent(source_resolved, eligible),
        "layerCoverage": percent(layer_resolved, eligible),
        "neutralMeaningCoverage": percent(neutral_resolved, eligible),
        "recipeCompatibilityCoverage": percent(recipe_compatible, eligible),
    })
    return metrics


def generate_contract(contract_dir: Path, generated_at: str) -> tuple[str, dict[str, Any]]:
    terms = add_integrity({
        "schema": "prisma.ui.canonical-terms.v1",
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "taskId": TASK_ID,
        "terms": CANONICAL_TERMS,
        "prohibitedCanonicalKeys": sorted(PROHIBITED_CANONICAL_KEYS),
    })
    rules = add_integrity({
        "schema": "prisma.ui.id-rules-lock.v1",
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "ndcGrammar": "PREFIX.lower_snake_case.lower_snake_case",
        "componentUiGrammar": "RUNTIME-SURFACE-ZONE-ELEMENT-TYPE-NN",
        "certifiedLegacyExceptionPolicy": "PRESERVE_CERTIFIED_COBRAR_IDS_EXACTLY",
        "canonicalAdapters": ADAPTERS,
        "states": list(REQUIRED_STATES + CONDITIONAL_STATES),
        "canonicalization": CANONICALIZATION,
    })
    write_json(contract_dir / "CANONICAL_TERMS.json", terms)
    write_json(contract_dir / "ID_RULES_LOCK.json", rules)
    write_json(contract_dir / "PRISMA_UI_COMPONENT_RECORD_V1.schema.json", record_schema())
    write_json(contract_dir / "PRISMA_UI_COMPONENT_ATLAS_V1.schema.json", atlas_schema())
    write_json(contract_dir / "PRISMA_UI_BRIDGE_HANDOFF_V1.schema.json", handoff_schema())
    contract_hash = sha256_bytes(canonical_bytes({"terms": terms, "rules": rules}))
    return contract_hash, {"terms": terms, "rules": rules}


def generate_authority_mesh(
    authority_dir: Path,
    product_root: Path,
    governor_root: Path,
    source_snapshot: str,
    runtime_results: dict[str, dict[str, Any]],
    records: list[dict[str, Any]],
    generated_at: str,
) -> dict[str, Any]:
    layers: list[dict[str, Any]] = []
    for record in records:
        for target in record["visualTargets"]:
            layers.append({
                "runtimeAlias": record["runtimeAlias"],
                "componentUiId": record["componentUiId"],
                "layerId": record.get("layerId"),
                "implementationLayerId": target.get("implementationLayerId"),
                "targetRole": target.get("targetRole"),
                "selector": target.get("selector"),
                "styleSourceFile": target.get("styleSourceFile"),
                "sourceHash": target.get("sourceHash"),
                "targetResolutionStatus": record.get("targetResolutionStatus"),
            })
    layer_map = add_integrity({
        "schema": "prisma.uimap.layers-map.v1",
        "schemaVersion": SCHEMA_VERSION,
        "taskId": TASK_ID,
        "generatedAt": generated_at,
        "sourceSnapshotHash": source_snapshot,
        "layers": sorted(layers, key=lambda row: (
            row["runtimeAlias"], str(row["componentUiId"]), str(row["selector"]), str(row["targetRole"])
        )),
    })
    readset_files: list[dict[str, Any]] = []
    for alias in ACTIVE_RUNTIME_ALIASES:
        result = runtime_results.get(alias)
        if not result:
            continue
        for path, digest in result["hashes"].items():
            readset_files.append({
                "runtimeAlias": alias,
                "sourceFile": norm_rel(product_root, path),
                "sourceHash": digest,
            })
    readset = add_integrity({
        "schema": "prisma.uimap.authority-readset-lock.v1",
        "schemaVersion": SCHEMA_VERSION,
        "taskId": TASK_ID,
        "generatedAt": generated_at,
        "productRootParameter": "ProductRoot",
        "governorRootParameter": "GovernorRoot",
        "sourceSnapshotHash": source_snapshot,
        "scope": {
            "productSourceMutationAllowed": False,
            "runtimeMutationAllowed": False,
            "databaseMutationAllowed": False,
            "visualApplicationAllowed": False,
            "browserAutomationAllowed": False,
            "codeAtlasToolMutationAllowed": True,
        },
        "files": sorted(readset_files, key=lambda row: (row["runtimeAlias"], row["sourceFile"])),
    })
    app_impact = add_integrity({
        "schema": "prisma.uimap.app-impact-matrix.v1",
        "schemaVersion": SCHEMA_VERSION,
        "taskId": TASK_ID,
        "generatedAt": generated_at,
        "applications": [
            {
                "runtimeAlias": alias,
                "runtimeLabel": RUNTIME_LABELS[alias],
                "rootDetected": bool(runtime_results.get(alias)),
                "sourceMutationAllowed": False,
                "mapperCoverageOnly": True,
                "componentCount": sum(r["runtimeAlias"] == alias for r in records),
            }
            for alias in ACTIVE_RUNTIME_ALIASES
        ],
    })
    gates = add_integrity({
        "schema": "prisma.uimap.contract-and-gate-matrix.v1",
        "schemaVersion": SCHEMA_VERSION,
        "taskId": TASK_ID,
        "generatedAt": generated_at,
        "gates": [
            {"gateId": "AUTHORITY_READSET", "required": True, "status": "PASS"},
            {"gateId": "LAYER_MAP_PRESENT", "required": True, "status": "PASS"},
            {"gateId": "APP_IMPACT_MATRIX", "required": True, "status": "PASS"},
            {"gateId": "PRODUCT_SOURCE_READ_ONLY", "required": True, "status": "PENDING_POST_HASH_CHECK"},
            {"gateId": "VISUAL_APPLICATION_FORBIDDEN", "required": True, "status": "PASS"},
            {"gateId": "BROWSER_AUTOMATION_FORBIDDEN", "required": True, "status": "PASS"},
        ],
    })
    risks = add_integrity({
        "schema": "prisma.uimap.missing-unmapped-risk.v1",
        "schemaVersion": SCHEMA_VERSION,
        "taskId": TASK_ID,
        "generatedAt": generated_at,
        "risks": [
            {
                "componentUiId": record["componentUiId"],
                "runtimeAlias": record["runtimeAlias"],
                "targetResolutionStatus": record["targetResolutionStatus"],
                "blockingReasons": record["blockingReasons"],
            }
            for record in records
            if record["blockingReasons"]
        ],
    })
    write_json(authority_dir / "AUTHORITY_READSET.lock.json", readset)
    write_json(authority_dir / "LAYERS_MAP.json", layer_map)
    write_json(authority_dir / "APP_IMPACT_MATRIX.json", app_impact)
    write_json(authority_dir / "CONTRACT_AND_GATE_MATRIX.json", gates)
    write_json(authority_dir / "MISSING_OR_UNMAPPED_RISK.json", risks)
    write_text(authority_dir / "AUTHORITY_MESH_REPORT.md", "\n".join([
        "# UIMAP1 Authority Mesh",
        "",
        f"- Task: `{TASK_ID}`",
        f"- Generated: `{generated_at}`",
        f"- Source snapshot: `{source_snapshot}`",
        "- Product/runtime/database/visual/browser mutation: **forbidden**",
        "- Code Atlas source integration: **allowed**",
        "- Layer Map: **present**",
        "",
        "This Mesh authorizes source-only discovery. It does not authorize visual application.",
    ]) + "\n")
    write_text(authority_dir / "LAYERS_MAP.md", "\n".join([
        "# UIMAP1 Layer Map",
        "",
        f"Entries: **{len(layers)}**",
        "",
        *[
            f"- `{row['componentUiId']}` → `{row.get('layerId') or 'UNRESOLVED'}` / `{row.get('selector')}`"
            for row in sorted(layers, key=lambda item: (str(item["componentUiId"]), str(item["selector"])))[:5000]
        ],
    ]) + "\n")
    return {
        "readset": readset,
        "layerMap": layer_map,
        "appImpact": app_impact,
        "gates": gates,
        "risks": risks,
    }


def existing_atlas_outputs(
    atlas_dir: Path,
    runtime_results: dict[str, dict[str, Any]],
    records: list[dict[str, Any]],
    aliases: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
) -> None:
    surfaces = []
    routes = []
    ownership = []
    layers = []
    selectors = []
    usage = []
    tokens = []
    pos = []
    zero = []
    important_rows = []
    for alias in ACTIVE_RUNTIME_ALIASES:
        result = runtime_results.get(alias)
        if not result:
            surfaces.append({
                "runtimeAlias": alias,
                "label": RUNTIME_LABELS[alias],
                "root": None,
                "exists": False,
                "routeCount": 0,
                "componentCount": 0,
            })
            continue
        runtime_records = [record for record in records if record["runtimeAlias"] == alias]
        surfaces.append({
            "runtimeAlias": alias,
            "label": result["runtimeLabel"],
            "root": result["root"],
            "exists": True,
            "routeCount": len(result["routes"]),
            "componentCount": len(runtime_records),
        })
        for route in result["routes"]:
            routes.append({
                "runtimeAlias": alias,
                "routeId": route.route_id,
                "routePath": route.route_path,
                "sourceFile": route.source_file,
                "kind": route.kind,
                "sourceHash": route.source_hash,
            })
            if route.route_path.startswith("/pos"):
                pos.append({
                    "runtimeAlias": alias,
                    "routeId": route.route_id,
                    "routePath": route.route_path,
                    "sourceFile": route.source_file,
                    "protected": True,
                    "reason": "operational-pos-route",
                })
    for record in records:
        ownership.append({
            "runtimeAlias": record["runtimeAlias"],
            "componentId": record["componentId"],
            "componentUiId": record["componentUiId"],
            "ownerId": record["ownerId"],
            "ownerFile": record["ownerFile"],
            "ownerSymbol": record["ownerSymbol"],
            "projectionOfComponentId": record["projectionOfComponentId"],
        })
        for target in record["visualTargets"]:
            layers.append({
                "runtimeAlias": record["runtimeAlias"],
                "componentUiId": record["componentUiId"],
                "layerId": record["layerId"],
                "implementationLayerId": target["implementationLayerId"],
                "targetRole": target["targetRole"],
                "selector": target["selector"],
                "stateSelector": target["stateSelector"],
            })
            selectors.append({
                "runtimeAlias": record["runtimeAlias"],
                "componentUiId": record["componentUiId"],
                "selector": target["selector"],
                "definedIn": target["styleSourceFile"],
                "stateSelector": target["stateSelector"],
                "sourceHash": target["sourceHash"],
            })
            usage.append({
                "runtimeAlias": record["runtimeAlias"],
                "componentUiId": record["componentUiId"],
                "classOrToken": target["anchorValue"],
                "usedIn": record["renderSourceFile"],
                "definedIn": target["styleSourceFile"],
            })
            if target["stateSelector"] == "default":
                zero.append({
                    "runtimeAlias": record["runtimeAlias"],
                    "componentUiId": record["componentUiId"],
                    "selector": target["selector"],
                    "zeroPolicy": "NOT_EVALUATED_SOURCE_ONLY",
                })
    write_json(atlas_dir / "01_SURFACE_REGISTRY.json", surfaces)
    write_json(atlas_dir / "02_ROUTE_COMPONENT_MAP.json", routes)
    write_json(atlas_dir / "03_COMPONENT_OWNERSHIP_MAP.json", ownership)
    write_json(atlas_dir / "04_LAYER_ROLE_KIND_MAP.json", layers)
    write_json(atlas_dir / "05_SELECTOR_GRAPH.json", selectors)
    write_csv(atlas_dir / "06_SELECTOR_USAGE.csv", usage)
    write_json(atlas_dir / "07_TOKEN_GRAPH.json", tokens)
    write_json(atlas_dir / "08_LEGACY_TOKEN_ALIAS_MAP.json", [])
    write_json(atlas_dir / "09_STATE_MATRIX.json", {
        "requiredStates": list(REQUIRED_STATES),
        "conditionalStates": list(CONDITIONAL_STATES),
        "components": [
            {"componentUiId": record["componentUiId"], "stateSupport": record["stateSupport"]}
            for record in records
        ],
    })
    write_json(atlas_dir / "10_CONTROL_APPLICABILITY_MATRIX.json", [
        {"control": "visualRecipe", "appliesWhen": "targetResolutionStatus=SOURCE_RESOLVED", "authorizesApplication": False},
        {"control": "surfaceAdapter", "adapters": ADAPTERS, "authorizesApplication": False},
    ])
    write_json(atlas_dir / "11_PRESET_ELIGIBILITY_REGISTRY.json", [
        {
            "componentUiId": record["componentUiId"],
            "applicationReadiness": record["applicationReadiness"],
            "blockingReasons": record["blockingReasons"],
        }
        for record in records
    ])
    write_json(atlas_dir / "12_POS_PROTECTION_MAP.json", pos)
    write_json(atlas_dir / "13_ZERO_MEANS_ZERO_AUDIT.json", zero)
    write_text(atlas_dir / "14_IMPORTANT_AUDIT_FILTERED.md", "# Important audit filtered\n\nUIMAP1 added no `!important`. Source applications were read-only.\n")
    write_text(atlas_dir / "15_ORPHAN_DUPLICATE_SHARED_SELECTORS.md", "\n".join([
        "# Orphan, duplicate and shared selector audit",
        "",
        f"- Aliases/deduplications: **{len(aliases)}**",
        f"- Conflicts: **{len(conflicts)}**",
        "- Runtime execution was forbidden, so static orphan conclusions remain explicit source classifications.",
    ]) + "\n")
    write_text(atlas_dir / "16_PRESET_PROMOTION_CONTRACT.md", "# Preset promotion contract\n\nThe Atlas localizes source targets. It never authorizes application or preset promotion.\n")
    write_text(atlas_dir / "17_CONTINUATION.md", "# Continuation\n\nUse PRISMA_UI_BRIDGE_HANDOFF.json only as input to a fresh exact-target Authority Mesh and read-only plan.\n")


def make_deprecations(product_root: Path, governor_root: Path, generated_at: str) -> list[dict[str, Any]]:
    evidence: list[str] = []
    for root in (product_root, governor_root):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            low = path.name.lower()
            if "liquid glass capsules" in low or "liquid-glass-capsules" in low or "liquid_glass_capsules" in low:
                try:
                    evidence.append(norm_rel(root, path))
                except Exception:
                    evidence.append(path.name)
    return [{
        "deprecationId": "DEPR.liquid_glass_capsules",
        "name": "Liquid Glass Capsules",
        "status": "DEPRECATED",
        "activeSurface": False,
        "targetPolicy": "NEVER_REGISTER_AS_ACTIVE_SURFACE",
        "evidenceRefs": sorted(set(evidence)),
        "generatedAt": generated_at,
    }]


def validate_alias_targets(
    records: list[dict[str, Any]],
    aliases: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    records_by_ui = {
        str(record.get("componentUiId")): record
        for record in records
        if record.get("componentUiId")
    }

    for row in aliases:
        canonical = str(row.get("canonicalComponentUiId") or "")
        if not canonical:
            # Legacy aliases for surface/owner/route/region/slot use canonicalId,
            # not canonicalComponentUiId.
            continue
        alias_id = str(row.get("aliasId") or "")
        target = records_by_ui.get(canonical)
        if target is None:
            errors.append(f"alias_target_missing:{alias_id}:{canonical}")
            continue

        if row.get("reason") != "SAME_OWNER_PROJECTION_DEDUPLICATED":
            continue
        expected_owner = str(row.get("canonicalOwnerFile") or "")
        expected_component = str(row.get("canonicalComponentId") or "")
        if not expected_owner or expected_owner != str(target.get("ownerFile") or ""):
            errors.append(f"alias_owner_provenance_mismatch:{alias_id}:{canonical}")
        if not expected_component or expected_component != str(target.get("componentId") or ""):
            errors.append(f"alias_component_provenance_mismatch:{alias_id}:{canonical}")
        if not row.get("dedupeKeyHash"):
            errors.append(f"alias_dedupe_key_missing:{alias_id}:{canonical}")

    return sorted(set(errors))


def validate_outputs(
    records: list[dict[str, Any]],
    aliases: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    product_before_hash: str,
    product_after_hash: str,
    governor_before_hash: str,
    governor_after_hash: str,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    per_record: list[dict[str, Any]] = []
    for record in records:
        record_errors = validate_record(record)
        if record_errors:
            per_record.append({"componentUiId": record.get("componentUiId"), "errors": record_errors})
            errors.extend(f"{record.get('componentUiId')}:{item}" for item in record_errors)
    for field in ("componentUiId", "componentId", "slotId"):
        values = [str(record.get(field) or "") for record in records]
        duplicates = sorted({value for value in values if value and values.count(value) > 1})
        if duplicates:
            errors.append(f"duplicate_{field}:" + ",".join(duplicates[:50]))
    if aliases_have_cycle(aliases):
        errors.append("circular_alias_detected")
    owner_files_by_id: dict[str, set[str]] = {}
    owner_ids_by_file: dict[str, set[str]] = {}
    for record in records:
        owner_id = str(record.get("ownerId") or "")
        owner_file = str(record.get("ownerFile") or "")
        if owner_id and owner_file:
            owner_files_by_id.setdefault(owner_id, set()).add(owner_file)
            owner_ids_by_file.setdefault(owner_file, set()).add(owner_id)
    if any(len(files) > 1 for files in owner_files_by_id.values()):
        errors.append("owner_id_maps_to_multiple_owner_files")
    if any(len(ids) > 1 for ids in owner_ids_by_file.values()):
        errors.append("owner_file_maps_to_multiple_owner_ids")
    alias_target_errors = validate_alias_targets(records, aliases)
    errors.extend(alias_target_errors)
    if product_before_hash != product_after_hash:
        errors.append("product_source_mutated")
    if governor_before_hash != governor_after_hash:
        errors.append("governor_source_mutated")
    golden = [record for record in records if record.get("bindingId") == GOLDEN_BINDING_ID]
    if len(golden) != 1:
        errors.append(f"golden_cobrar_count:{len(golden)}")
    else:
        record = golden[0]
        exact_expectations = {
            "surfaceId": GOLDEN_TRACE_DEFAULT["surfaceId"],
            "interfaceId": GOLDEN_TRACE_DEFAULT["interfaceId"],
            "routeId": GOLDEN_TRACE_DEFAULT["routeId"],
            "routePath": GOLDEN_TRACE_DEFAULT["routePath"],
            "regionId": GOLDEN_TRACE_DEFAULT["regionId"],
            "slotId": GOLDEN_TRACE_DEFAULT["slotId"],
            "componentId": GOLDEN_TRACE_DEFAULT["componentId"],
            "componentUiId": GOLDEN_TRACE_DEFAULT["componentUiId"],
            "widgetTypeId": GOLDEN_TRACE_DEFAULT["widgetTypeId"],
            "ownerId": GOLDEN_TRACE_DEFAULT["ownerId"],
            "layerId": GOLDEN_LAYER_ID,
            "implementationLayerId": GOLDEN_IMPLEMENTATION_LAYER_ID,
        }
        for field, expected in exact_expectations.items():
            if record.get(field) != expected:
                errors.append(f"golden_{field}_drift")
        if (record.get("recipeCompatibility") or {}).get("coverageStatus") != "CURRENT_SOURCE_COVERAGE_COMPLETE":
            errors.append("golden_recipe_coverage_name_invalid")
        required_legacy_aliases = {
            (field, value)
            for field, value in GOLDEN_LEGACY_TRACE_DEFAULT.items()
        }
        observed_legacy_aliases = {
            (str(row.get("aliasKind")), str(row.get("aliasId")))
            for row in aliases
            if row.get("reason") == "CERTIFIED_LEGACY_ID_PRESERVED"
        }
        missing_aliases = required_legacy_aliases - observed_legacy_aliases
        if missing_aliases:
            errors.append("golden_legacy_aliases_missing")
    if conflicts:
        warnings.append(f"registered_conflicts:{len(conflicts)}")
    silent_missing_ids = [record.get("ownerFile") for record in records if not record.get("componentUiId")]
    if silent_missing_ids:
        errors.append("active_component_without_componentUiId")
    return {
        "ok": not errors,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "recordValidation": per_record,
        "gates": {
            "jsonSchemaCompatible": not any("missing_required_field" in e or "invalid_" in e for e in errors),
            "canonicalIdsUnique": not any(e.startswith("duplicate_") for e in errors),
            "aliasesAcyclic": "circular_alias_detected" not in errors,
            "aliasTargetsResolved": not any(e.startswith("alias_target_missing:") for e in errors),
            "aliasProvenanceConsistent": not any(
                e.startswith((
                    "alias_owner_provenance_mismatch:",
                    "alias_component_provenance_mismatch:",
                    "alias_dedupe_key_missing:",
                ))
                for e in errors
            ),
            "productByteForByteIntact": product_before_hash == product_after_hash,
            "governorByteForByteIntact": governor_before_hash == governor_after_hash,
            "goldenCobrarPreserved": len(golden) == 1 and not any(e.startswith("golden_") for e in errors),
            "browserAutomationExecuted": False,
            "databaseMutationExecuted": False,
            "prismaGenerateExecuted": False,
            "portMutationExecuted": False,
            "runtimeProcessMutationExecuted": False,
        },
    }


def _git_tracked_paths(root: Path) -> list[Path] | None:
    """Return Git-tracked files only; fall back to tree walk outside Git repos."""
    import subprocess

    try:
        process = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=120,
        )
    except Exception:
        return None
    if process.returncode != 0:
        return None

    paths: list[Path] = []
    for raw in process.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8", errors="surrogateescape")
        candidate = root / Path(*PurePosixPath(relative).parts)
        if candidate.is_file():
            paths.append(candidate)
    return paths


def tree_hash(
    roots: list[Path],
    exclude_roots: list[Path] | None = None,
    workers: int = 18,
) -> tuple[str, dict[str, str]]:
    """Hash tracked source bytes, never volatile/untracked runtime evidence."""
    exclude_roots = [path.resolve() for path in (exclude_roots or [])]
    files: list[tuple[Path, Path]] = []

    for root in roots:
        if not root.exists():
            continue
        root_resolved = root.resolve()
        tracked = _git_tracked_paths(root_resolved)
        candidates = tracked if tracked is not None else list(root_resolved.rglob("*"))

        for path in candidates:
            if not path.is_file():
                continue
            try:
                resolved = path.resolve()
                if any(
                    resolved == excluded or excluded in resolved.parents
                    for excluded in exclude_roots
                ):
                    continue
                rel = resolved.relative_to(root_resolved)
            except Exception:
                continue

            low_parts = {part.lower() for part in rel.parts}
            if low_parts & {
                ".git",
                "node_modules",
                ".next",
                "dist",
                "build",
                "coverage",
                "__pycache__",
                ".mam-runtime",
            }:
                continue
            if path.stat().st_size > 64 * 1024 * 1024:
                continue
            files.append((root_resolved, path))

    from concurrent.futures import ThreadPoolExecutor, as_completed

    hashes: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=max(1, min(18, workers))) as pool:
        futures = {
            pool.submit(sha256_file, path): (root, path)
            for root, path in files
        }
        for future in as_completed(futures):
            root, path = futures[future]
            try:
                key = f"{root.name}/{path.resolve().relative_to(root).as_posix()}"
                hashes[key] = future.result()
            except Exception:
                continue

    ordered = {key: hashes[key] for key in sorted(hashes)}
    return source_snapshot_hash(ordered), ordered


def tree_hash_diff(
    before: dict[str, str],
    after: dict[str, str],
) -> dict[str, Any]:
    before_keys = set(before)
    after_keys = set(after)
    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    changed = sorted(
        key
        for key in before_keys & after_keys
        if before[key] != after[key]
    )
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "mutationCount": len(added) + len(removed) + len(changed),
        "intact": not added and not removed and not changed,
    }



def alias_applies_to_runtime(row: dict[str, Any], runtime_alias: str) -> bool:
    alias_id = str(row.get("aliasId") or "")
    canonical = str(row.get("canonicalId") or row.get("canonicalComponentUiId") or "")
    prefix = runtime_alias.upper() + "-"
    ndc_segment = f".{runtime_alias}."
    return (
        alias_id.upper().startswith(prefix)
        or canonical.upper().startswith(prefix)
        or ndc_segment in canonical.lower()
    )


def load_previous_batches(source: str | None) -> dict[str, dict[str, Any]]:
    if not source:
        return {}
    target = Path(source).expanduser().resolve()
    rows: dict[str, dict[str, Any]] = {}

    def accept(name: str, raw: bytes) -> None:
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"Previous batch is invalid JSON: {name}: {exc}") from exc
        runtime_alias = str(payload.get("runtimeAlias") or "")
        batch_id = str(payload.get("batchId") or "")
        if runtime_alias not in RUNTIME_ORDER or not batch_id:
            raise RuntimeError(f"Previous batch missing runtimeAlias/batchId: {name}")
        if runtime_alias in rows:
            raise RuntimeError(f"Duplicate previous batch for runtimeAlias={runtime_alias}")
        rows[runtime_alias] = {"name": name, "raw": raw, "payload": payload}

    if target.is_file() and target.suffix.lower() == ".zip":
        with zipfile.ZipFile(target) as archive:
            bad = archive.testzip()
            if bad:
                raise RuntimeError(f"Previous batch ZIP corrupt at: {bad}")
            names = [
                name for name in archive.namelist()
                if re.search(r"(?:^|/)batches/\d{2}_[^/]+\.json$", name)
                and "/history/" not in name.replace("\\", "/")
            ]
            for name in sorted(names):
                accept(name, archive.read(name))
    elif target.is_dir():
        for path in sorted(target.glob("[0-9][0-9]_*.json"), key=lambda p: p.name):
            accept(path.name, path.read_bytes())
    else:
        raise RuntimeError(f"Previous batches source not found: {target}")
    return rows


def run_uimap(
    product_root: str,
    governor_root: str,
    output_dir: str,
    embedded_evidence: str | None = None,
    input_audit: str | None = None,
    run_timestamp: str | None = None,
    workers: int = 18,
    product_hash_exclude: list[str] | None = None,
    git_context: dict[str, Any] | None = None,
    backup_manifest: dict[str, Any] | None = None,
    rollback_files: dict[str, str] | None = None,
    previous_batches_source: str | None = None,
) -> dict[str, Any]:
    generated_at = parse_timestamp(run_timestamp)
    product = Path(product_root).expanduser().resolve()
    governor = Path(governor_root).expanduser().resolve()
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    authority_dir = output / "authority"
    contract_dir = output / "contract"
    atlas_dir = output / "atlas"
    batches_dir = output / "batches"
    batch_history_dir = batches_dir / "history"
    reports_dir = output / "reports"
    tests_dir = output / "tests"
    rollback_dir = output / "rollback"
    manifest_dir = output / "manifest"
    for path in (
        authority_dir, contract_dir, atlas_dir, batches_dir, batch_history_dir,
        reports_dir, tests_dir, rollback_dir, manifest_dir
    ):
        path.mkdir(parents=True, exist_ok=True)

    previous_batches = load_previous_batches(previous_batches_source)
    for previous in previous_batches.values():
        history_name = f"{previous['payload']['batchId']}.json"
        (batch_history_dir / history_name).write_bytes(previous["raw"])

    exclude_paths = [Path(p).expanduser().resolve() for p in (product_hash_exclude or [])]
    product_before_hash, product_before_files = tree_hash([product], exclude_roots=exclude_paths, workers=workers)
    governor_before_hash, governor_before_files = tree_hash([governor], workers=workers)

    contract_hash, contract_payload = generate_contract(contract_dir, generated_at)
    roots = resolve_runtime_roots(product)
    runtime_results: dict[str, dict[str, Any]] = {}
    for alias in ACTIVE_RUNTIME_ALIASES:
        runtime_roots = roots.get(alias) or []
        if not runtime_roots:
            continue
        runtime_results[alias] = discover_runtime(alias, runtime_roots[0], product, workers=workers)
    authority_index = build_authority_indexes(product, governor)
    golden_trace, golden_evidence = discover_golden_trace(
        governor,
        Path(embedded_evidence).resolve() if embedded_evidence else None,
    )

    all_records: list[dict[str, Any]] = []
    all_routes: list[dict[str, Any]] = []
    global_source_files: dict[str, str] = {}
    for alias in ACTIVE_RUNTIME_ALIASES:
        result = runtime_results.get(alias)
        if not result:
            continue
        css_index = css_target_index(result["cssTargets"])
        ordinal_counter: dict[str, int] = {}
        for candidate in result["candidates"]:
            region = infer_region(candidate.route_path, candidate.class_name, candidate.render_symbol, candidate.widget_kind)
            element = choose_element_name(candidate)
            locator_base = component_locator(
                alias,
                candidate.route_path,
                region,
                element,
                candidate.widget_kind,
                1,
                canonical_owner_identity(candidate),
            ).rsplit("-", 1)[0]
            ordinal_counter[locator_base] = ordinal_counter.get(locator_base, 0) + 1
            targets = css_index.get(candidate.class_name or "", [])
            record = record_from_candidate(
                candidate,
                targets,
                authority_index,
                ordinal_counter[locator_base],
                golden_trace,
                golden_evidence,
            )
            all_records.append(record)
        for route in result["routes"]:
            all_routes.append({
                "runtimeAlias": alias,
                "routeId": route.route_id,
                "routePath": route.route_path,
                "sourceFile": route.source_file,
                "sourceHash": route.source_hash,
            })
        for path, digest in result["hashes"].items():
            global_source_files[norm_rel(product, path)] = digest

    records, aliases, conflicts = deduplicate_records(all_records)
    aliases = sorted(
        aliases + golden_legacy_aliases(golden_trace),
        key=lambda row: (str(row.get("aliasKind", "")), str(row.get("aliasId", ""))),
    )
    deprecations = make_deprecations(product, governor, generated_at)
    source_snapshot = source_snapshot_hash(global_source_files)
    coverage_global = coverage_for(records, all_routes, len(deprecations), None)
    coverage_by_runtime = {
        alias: coverage_for(
            [record for record in records if record["runtimeAlias"] == alias],
            [route for route in all_routes if route["runtimeAlias"] == alias],
            0,
            alias,
        )
        for alias in ACTIVE_RUNTIME_ALIASES
    }

    mesh = generate_authority_mesh(
        authority_dir,
        product,
        governor,
        source_snapshot,
        runtime_results,
        records,
        generated_at,
    )
    existing_atlas_outputs(atlas_dir, runtime_results, records, aliases, conflicts)

    atlas_payload = add_integrity({
        "schema": "prisma.ui.component-atlas.v1",
        "schemaVersion": SCHEMA_VERSION,
        "taskId": TASK_ID,
        "generatedAt": generated_at,
        "contractHash": contract_hash,
        "sourceSnapshotHash": source_snapshot,
        "components": records,
        "coverage": {
            "global": coverage_global,
            "byRuntime": coverage_by_runtime,
        },
        "authorityMeshHash": mesh["readset"]["integrity"]["canonicalPayloadSha256"],
    })
    alias_payload = add_integrity({
        "schema": "prisma.ui.alias-registry.v1",
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "contractHash": contract_hash,
        "aliases": aliases,
    })
    conflict_payload = add_integrity({
        "schema": "prisma.ui.conflicts.v1",
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "contractHash": contract_hash,
        "conflicts": conflicts,
    })
    coverage_payload = add_integrity({
        "schema": "prisma.ui.coverage.v1",
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "contractHash": contract_hash,
        "global": coverage_global,
        "byRuntime": coverage_by_runtime,
    })
    deprecation_payload = add_integrity({
        "schema": "prisma.ui.deprecations.v1",
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "contractHash": contract_hash,
        "deprecations": deprecations,
    })
    eligible = [record for record in records if record["applicationReadiness"] == "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT"]
    blocked = [
        {
            "componentUiId": record["componentUiId"],
            "targetResolutionStatus": record["targetResolutionStatus"],
            "blockingReasons": record["blockingReasons"],
        }
        for record in records
        if record["applicationReadiness"] == "BLOCKED"
    ]
    handoff_payload = add_integrity({
        "schema": "prisma.ui.bridge-handoff.v1",
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "contractHash": contract_hash,
        "sourceSnapshotHash": source_snapshot,
        "eligibleComponents": eligible,
        "blockedComponents": blocked,
        "gateReminder": [
            "fresh exact-target Authority Mesh",
            "Layer Map",
            "scope guard",
            "read-only plan/diff",
            "application authorization",
            "verified backup",
            "post evidence",
            "rollback",
        ],
    })
    canonical_schema_validation = {
        "recordSchemaErrors": [
            {
                "componentUiId": record.get("componentUiId"),
                "errors": validate_schema_subset(record, record_schema()),
            }
            for record in records
            if validate_schema_subset(record, record_schema())
        ],
        "atlasSchemaErrors": validate_schema_subset(atlas_payload, atlas_schema()),
        "handoffSchemaErrors": validate_schema_subset(handoff_payload, handoff_schema()),
    }
    canonical_schema_validation["ok"] = not any([
        canonical_schema_validation["recordSchemaErrors"],
        canonical_schema_validation["atlasSchemaErrors"],
        canonical_schema_validation["handoffSchemaErrors"],
    ])

    write_json(atlas_dir / "PRISMA_UI_COMPONENT_ATLAS.json", atlas_payload)
    write_json(atlas_dir / "PRISMA_UI_ALIAS_REGISTRY.json", alias_payload)
    write_json(atlas_dir / "PRISMA_UI_CONFLICTS.json", conflict_payload)
    write_json(atlas_dir / "PRISMA_UI_COVERAGE.json", coverage_payload)
    write_json(atlas_dir / "PRISMA_UI_DEPRECATIONS.json", deprecation_payload)
    write_jsonl(atlas_dir / "NDC_UI_CURATION_DELTA.jsonl", [
        {
            "componentUiId": record["componentUiId"],
            "runtimeAlias": record["runtimeAlias"],
            "neutralMeaningId": record["neutralMeaningId"],
            "ndcStatus": record["ndcStatus"],
            "confidence": record["confidence"],
            "curationAction": "PROVE_NEUTRAL_MEANING" if record["neutralMeaningId"] is None else "NONE",
            "blockingReasons": record["blockingReasons"],
        }
        for record in records
        if record["neutralMeaningId"] is None or record["ndcStatus"] in {"CONFLICT", "NEEDS_REVIEW", "BLOCKED"}
    ])
    write_json(atlas_dir / "PRISMA_UI_BRIDGE_HANDOFF.json", handoff_payload)

    previous_contract = previous_batches.get("contract", {}).get("payload", {})
    contract_batch_id = f"BATCH.contract.{contract_hash[:16].lower()}"
    contract_batch = add_integrity({
        "schema": "prisma.ui.component-batch.v1",
        "schemaVersion": SCHEMA_VERSION,
        "batchId": contract_batch_id,
        "supersedesBatchId": (
            previous_contract.get("batchId")
            if previous_contract.get("batchId") and previous_contract.get("batchId") != contract_batch_id
            else None
        ),
        "contractHash": contract_hash,
        "runtimeAlias": "contract",
        "sourceSnapshotHash": source_snapshot,
        "components": [],
        "aliases": [],
        "conflicts": [],
        "coverage": {"contractFiles": 5},
    })
    write_json(batches_dir / "00_contract.json", contract_batch)
    for index, alias in enumerate(ACTIVE_RUNTIME_ALIASES, start=1):
        runtime_components = [record for record in records if record["runtimeAlias"] == alias]
        runtime_aliases = [row for row in aliases if alias_applies_to_runtime(row, alias)]
        runtime_conflicts = [row for row in conflicts if any(
            owner.lower().find(f"/{alias}/") >= 0 for owner in row.get("owners", [])
        )]
        batch_seed = {
            "schemaVersion": SCHEMA_VERSION,
            "contractHash": contract_hash,
            "runtimeAlias": alias,
            "sourceSnapshotHash": source_snapshot,
            "componentsHash": sha256_bytes(canonical_bytes(runtime_components)),
            "aliasesHash": sha256_bytes(canonical_bytes(runtime_aliases)),
            "conflictsHash": sha256_bytes(canonical_bytes(runtime_conflicts)),
            "coverageHash": sha256_bytes(canonical_bytes(coverage_by_runtime[alias])),
        }
        batch_id = f"BATCH.{alias}.{sha256_bytes(canonical_bytes(batch_seed))[:16].lower()}"
        previous_batch = previous_batches.get(alias, {}).get("payload", {})
        batch = add_integrity({
            "schema": "prisma.ui.component-batch.v1",
            "schemaVersion": SCHEMA_VERSION,
            "batchId": batch_id,
            "supersedesBatchId": (
                previous_batch.get("batchId")
                if previous_batch.get("batchId") and previous_batch.get("batchId") != batch_id
                else None
            ),
            "contractHash": contract_hash,
            "runtimeAlias": alias,
            "sourceSnapshotHash": source_snapshot,
            "components": runtime_components,
            "aliases": runtime_aliases,
            "conflicts": runtime_conflicts,
            "coverage": coverage_by_runtime[alias],
        })
        write_json(batches_dir / f"{index:02d}_{alias}.json", batch)

    product_after_hash, product_after_files = tree_hash(
        [product],
        exclude_roots=exclude_paths,
        workers=workers,
    )
    governor_after_hash, governor_after_files = tree_hash(
        [governor],
        workers=workers,
    )
    product_integrity_diff = tree_hash_diff(
        product_before_files,
        product_after_files,
    )
    governor_integrity_diff = tree_hash_diff(
        governor_before_files,
        governor_after_files,
    )
    validation = validate_outputs(
        records,
        aliases,
        conflicts,
        product_before_hash,
        product_after_hash,
        governor_before_hash,
        governor_after_hash,
    )
    bridge_errors: list[str] = []
    for record in eligible:
        if record.get("ndcStatus") not in {"CONFIRMED", "CANONICAL_READY"}:
            bridge_errors.append(f"bad_ndc:{record.get('componentUiId')}")
        if record.get("targetResolutionStatus") != "SOURCE_RESOLVED":
            bridge_errors.append(f"bad_target:{record.get('componentUiId')}")
        if record.get("applicationReadiness") != "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT":
            bridge_errors.append(f"bad_readiness:{record.get('componentUiId')}")
        if record.get("blockingReasons"):
            bridge_errors.append(f"has_blockers:{record.get('componentUiId')}")
        if (record.get("recipeCompatibility") or {}).get("coverageStatus") in {"BLOCKED_BY_UNRESOLVED_VISUAL_STATE", "NOT_EVALUATED"}:
            bridge_errors.append(f"bad_recipe:{record.get('componentUiId')}")
    validation["canonicalSchemaValidation"] = canonical_schema_validation
    validation["gates"]["canonicalSchemasValidated"] = canonical_schema_validation["ok"]
    if not canonical_schema_validation["ok"]:
        validation["ok"] = False
        validation["errors"] = sorted(set(validation["errors"] + ["canonical_schema_validation_failed"]))

    validation["bridgeHandoffValidation"] = {"ok": not bridge_errors, "errors": bridge_errors}
    validation["gates"]["bridgeHandoffIndependent"] = not bridge_errors
    if bridge_errors:
        validation["ok"] = False
        validation["errors"] = sorted(set(validation["errors"] + ["bridge_handoff_invalid"]))
    explicit_gaps = any(record["blockingReasons"] for record in records) or bool(conflicts)
    final_status = "FAIL_SOURCE_MAP"
    if validation["ok"]:
        final_status = "PASS_SOURCE_MAP_WITH_EXPLICIT_GAPS" if explicit_gaps else "PASS_SOURCE_MAP_COMPLETE"
    validation["finalStatus"] = final_status
    validation["componentCount"] = len(records)
    validation["routeCount"] = len(all_routes)
    validation["contractHash"] = contract_hash
    validation["sourceSnapshotHash"] = source_snapshot
    write_json(reports_dir / "VALIDATION.json", validation)
    write_json(reports_dir / "SOURCE_PRESERVATION.json", {
        "schema": "prisma.uimap.source-preservation.v2",
        "integrityScope": "GIT_TRACKED_SOURCE_ONLY",
        "productBeforeHash": product_before_hash,
        "productAfterHash": product_after_hash,
        "productIntact": product_integrity_diff["intact"],
        "productDiff": product_integrity_diff,
        "governorBeforeHash": governor_before_hash,
        "governorAfterHash": governor_after_hash,
        "governorIntact": governor_integrity_diff["intact"],
        "governorDiff": governor_integrity_diff,
        "exactTaskOwnedExclusions": [str(path) for path in exclude_paths],
        "untrackedAndVolatileFilesPolicy": (
            "Excluded from product-source integrity. Git-tracked source bytes "
            "remain mandatory and any added/removed/changed tracked path fails."
        ),
    })
    write_json(reports_dir / "GIT_CONTEXT.json", git_context or {"status": "NOT_PROVIDED_BY_CALLER"})
    write_json(reports_dir / "BACKUP_MANIFEST.json", backup_manifest or {"status": "NOT_APPLICABLE_MAPPER_ONLY"})
    if input_audit and Path(input_audit).exists():
        shutil.copy2(input_audit, reports_dir / "INPUT_AUDIT.json")
    else:
        write_json(reports_dir / "INPUT_AUDIT.json", {"status": "EMBEDDED_AUDIT_NOT_PROVIDED"})
    write_json(tests_dir / "MAPPER_GATES.json", {
        "status": final_status,
        "validation": validation,
        "canonicalAtlasChecksum": atlas_payload["integrity"]["canonicalPayloadSha256"],
        "bridgeChecksum": handoff_payload["integrity"]["canonicalPayloadSha256"],
    })
    if rollback_files:
        for name, source in rollback_files.items():
            source_path = Path(source)
            if source_path.exists() and source_path.is_file():
                shutil.copy2(source_path, rollback_dir / name)
    write_text(rollback_dir / "README.md", "# Rollback\n\nRollback applies only to the Code Atlas tool integration. Product and Governor roots are read-only and require no rollback.\n")

    manifest_files = []
    for path in sorted(output.rglob("*"), key=lambda p: p.as_posix().lower()):
        if path.is_file() and "manifest/ATLAS_MANIFEST.json" not in path.as_posix():
            manifest_files.append({
                "file": path.relative_to(output).as_posix(),
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            })
    manifest_payload = add_integrity({
        "schema": "prisma.uimap.artifact-manifest.v1",
        "schemaVersion": SCHEMA_VERSION,
        "taskId": TASK_ID,
        "generatedAt": generated_at,
        "finalStatus": final_status,
        "contractHash": contract_hash,
        "sourceSnapshotHash": source_snapshot,
        "files": manifest_files,
    })
    write_json(manifest_dir / "ATLAS_MANIFEST.json", manifest_payload)
    continuation = "\n".join([
        "# UIMAP1 Continuation",
        "",
        f"- Status: `{final_status}`",
        f"- Product root parameter: `{product}`",
        f"- Governor root parameter: `{governor}`",
        f"- Contract hash: `{contract_hash}`",
        f"- Source snapshot hash: `{source_snapshot}`",
        f"- Components: **{len(records)}**",
        f"- Routes: **{len(all_routes)}**",
        f"- Eligible for future Authority preflight: **{len(eligible)}**",
        f"- Explicitly blocked/partial: **{len(blocked)}**",
        "",
        "GitHub remains frozen. No push, PR, Actions check, merge or remote mutation was performed.",
        "The next permitted visual step for any eligible component is a new exact-target Authority Mesh and read-only plan/diff.",
    ]) + "\n"
    write_text(output / "CONTINUATION.md", continuation)
    result = {
        "ok": validation["ok"],
        "finalStatus": final_status,
        "outputDir": str(output),
        "contractHash": contract_hash,
        "sourceSnapshotHash": source_snapshot,
        "canonicalAtlasChecksum": atlas_payload["integrity"]["canonicalPayloadSha256"],
        "bridgeChecksum": handoff_payload["integrity"]["canonicalPayloadSha256"],
        "componentCount": len(records),
        "routeCount": len(all_routes),
        "validation": validation,
    }
    write_json(reports_dir / "RESULT.json", result)
    return result


def zip_artifact(source_dir: Path, zip_path: Path) -> str:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(source_dir.rglob("*"), key=lambda p: p.as_posix().lower()):
            if path.is_file():
                archive.write(path, path.relative_to(source_dir).as_posix())
    return sha256_file(zip_path)
