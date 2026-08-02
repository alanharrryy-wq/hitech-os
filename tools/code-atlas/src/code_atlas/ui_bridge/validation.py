from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from code_atlas.app_map.uimap.contracts import (
    SCHEMA_VERSION as UIMAP_SCHEMA_VERSION,
    add_integrity,
    record_schema,
    validate_record as validate_uimap_record,
    validate_schema_subset,
)
from code_atlas.app_map.uimap.runner import validate_alias_targets

from .canonical import canonical_sha256
from .contracts import (
    APPLICATION_READINESS_VALUES, ANCHOR_KINDS, CANONICAL_ADAPTERS, COMPONENT_UI_ID_RE,
    CONDITIONAL_STATES, CONFIDENCE_VALUES, FORBIDDEN_CANONICAL_KEYS, INTERACTIVE_STATES,
    NDC_ID_RE, NDC_STATUSES, RECIPE_COVERAGE_VALUES, REQUIRED_BATCH_FIELDS,
    RESERVED_SEGMENTS, RUNTIME_ALIASES, SOURCE_RESOLVED_FIELDS, STATE_VALUES,
    TARGET_RESOLUTION_VALUES, TARGET_ROLES,
)


def _issue(code: str, message: str, **context: Any) -> dict[str, Any]:
    return {"code": code, "message": message, "context": context}


def _reserved_segment(value: str) -> str | None:
    for segment in value.lower().replace("-", ".").split("."):
        if segment in RESERVED_SEGMENTS:
            return segment
    return None


def validate_visual_target(target: dict[str, Any], component_ref: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    required = {
        "visualTargetId", "targetRole", "styleSourceFile", "anchorKind", "anchorValue",
        "selector", "pseudoElement", "stateSelector", "atRule", "implementationLayerId", "sourceHash",
    }
    nullable = {"pseudoElement", "atRule", "implementationLayerId"}
    missing = sorted(
        {key for key in required if key not in target}
        | {key for key in required - nullable if target.get(key) in (None, "")}
    )
    if missing:
        issues.append(_issue("VISUAL_TARGET_MISSING_FIELDS", "Visual target is incomplete", component=component_ref, missing=missing))
    if target.get("anchorKind") not in ANCHOR_KINDS:
        issues.append(_issue("INVALID_ANCHOR_KIND", "Unknown anchorKind", component=component_ref, value=target.get("anchorKind")))
    if target.get("targetRole") not in TARGET_ROLES:
        issues.append(_issue("INVALID_TARGET_ROLE", "Unknown targetRole", component=component_ref, value=target.get("targetRole")))
    source_file = str(target.get("styleSourceFile", ""))
    if Path(source_file).is_absolute() or ":\\" in source_file or source_file.startswith("/"):
        issues.append(_issue("ABSOLUTE_PATH_FORBIDDEN", "Atlas paths must be relative", component=component_ref, path=source_file))
    if target.get("anchorKind") == "GENERATED_PROJECTION" and target.get("patchPolicy") != "DO_NOT_PATCH_GENERATED":
        issues.append(_issue("GENERATED_PATCH_POLICY_REQUIRED", "Generated projections must be protected", component=component_ref))
    return issues


def validate_component(component: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    ref = str(component.get("componentUiId") or component.get("componentId") or "<unidentified>")
    for error in validate_uimap_record(component):
        issues.append(_issue(
            "UIMAP_COMPONENT_CONTRACT_ERROR",
            "Component does not satisfy its canonical UIMAP contract",
            component=ref,
            error=error,
        ))
    for error in validate_schema_subset(component, record_schema()):
        issues.append(_issue(
            "UIMAP_COMPONENT_SCHEMA_ERROR",
            "Component does not satisfy the canonical UIMAP record schema",
            component=ref,
            error=error,
        ))
    forbidden = sorted(FORBIDDEN_CANONICAL_KEYS.intersection(component.keys()))
    if forbidden:
        issues.append(_issue("FORBIDDEN_CANONICAL_KEYS", "Legacy aliases leaked into canonical record", component=ref, keys=forbidden))
    runtime = component.get("runtimeAlias")
    if runtime not in RUNTIME_ALIASES:
        issues.append(_issue("INVALID_RUNTIME_ALIAS", "runtimeAlias is not canonical", component=ref, value=runtime))
    ui_id = component.get("componentUiId")
    if not ui_id or not COMPONENT_UI_ID_RE.fullmatch(str(ui_id)):
        issues.append(_issue("INVALID_COMPONENT_UI_ID", "componentUiId must use uppercase hyphen grammar", component=ref, value=ui_id))
    for field in ("surfaceId", "interfaceId", "routeId", "regionId", "componentId", "widgetTypeId", "neutralMeaningId"):
        value = component.get(field)
        if value is not None and value != "" and not NDC_ID_RE.fullmatch(str(value)):
            issues.append(_issue("INVALID_NDC_ID", "ID does not follow canonical NDC grammar", component=ref, field=field, value=value))
        if isinstance(value, str):
            reserved = _reserved_segment(value)
            if reserved:
                issues.append(_issue("RESERVED_ID_SEGMENT", "Reserved segment used in ID", component=ref, field=field, segment=reserved))
    if component.get("ndcStatus") not in NDC_STATUSES:
        issues.append(_issue("INVALID_NDC_STATUS", "ndcStatus is not canonical", component=ref, value=component.get("ndcStatus")))
    if component.get("confidence") not in CONFIDENCE_VALUES:
        issues.append(_issue("INVALID_CONFIDENCE", "confidence is not canonical", component=ref, value=component.get("confidence")))
    target_status = component.get("targetResolutionStatus")
    if target_status not in TARGET_RESOLUTION_VALUES:
        issues.append(_issue("INVALID_TARGET_RESOLUTION", "targetResolutionStatus is not canonical", component=ref, value=target_status))
    readiness = component.get("applicationReadiness")
    if readiness not in APPLICATION_READINESS_VALUES:
        issues.append(_issue("INVALID_APPLICATION_READINESS", "applicationReadiness is not canonical", component=ref, value=readiness))
    adapter = component.get("adapterId")
    if runtime in CANONICAL_ADAPTERS and adapter not in (None, "", CANONICAL_ADAPTERS[runtime]):
        issues.append(_issue("NONCANONICAL_ADAPTER", "Adapter does not match runtimeAlias", component=ref, expected=CANONICAL_ADAPTERS[runtime], actual=adapter))
    state_support = component.get("stateSupport", {})
    if not isinstance(state_support, dict):
        issues.append(_issue("INVALID_STATE_SUPPORT", "stateSupport must be an object", component=ref))
    else:
        for state in (*INTERACTIVE_STATES, *CONDITIONAL_STATES):
            value = state_support.get(state, "NOT_EVALUATED")
            if value not in STATE_VALUES:
                issues.append(_issue("INVALID_STATE_VALUE", "State value is not canonical", component=ref, state=state, value=value))
        if runtime in {"tb", "mb"} and state_support.get("hover") == "NOT_APPLICABLE":
            compatibility = component.get("recipeCompatibility")
            hover_policy = (
                component.get("hoverPolicy")
                or component.get("adapterPolicy", {}).get("hoverPolicy")
                or (compatibility.get("hoverPolicy") if isinstance(compatibility, dict) else None)
            )
            if hover_policy != "substitute-pressed" or state_support.get("pressed") in {None, "MISSING_REQUIRED", "NOT_EVALUATED"}:
                issues.append(_issue("TOUCH_HOVER_SUBSTITUTION_INVALID", "Touch hover omission requires substitute-pressed and pressed coverage", component=ref))
    compatibility = component.get("recipeCompatibility")
    coverage = (
        compatibility.get("coverageStatus", "NOT_EVALUATED")
        if isinstance(compatibility, dict)
        else component.get("recipeCoverageStatus", component.get("recipeCoverage", "NOT_EVALUATED"))
    )
    if isinstance(coverage, str) and coverage not in RECIPE_COVERAGE_VALUES:
        issues.append(_issue("INVALID_RECIPE_COVERAGE", "Recipe coverage status is ambiguous or noncanonical", component=ref, value=coverage))
    visual_targets = component.get("visualTargets", [])
    if visual_targets is not None and not isinstance(visual_targets, list):
        issues.append(_issue("INVALID_VISUAL_TARGETS", "visualTargets must be an array", component=ref))
    elif isinstance(visual_targets, list):
        for target in visual_targets:
            if not isinstance(target, dict):
                issues.append(_issue("INVALID_VISUAL_TARGET", "visualTarget entry must be object", component=ref))
            else:
                issues.extend(validate_visual_target(target, ref))
    if target_status == "SOURCE_RESOLVED":
        missing = sorted(field for field in SOURCE_RESOLVED_FIELDS if component.get(field) in (None, "", []))
        if missing:
            issues.append(_issue("SOURCE_RESOLVED_CHAIN_INCOMPLETE", "SOURCE_RESOLVED requires the complete authority chain", component=ref, missing=missing))
        if component.get("ndcStatus") not in {"CONFIRMED", "CANONICAL_READY"}:
            issues.append(_issue("SOURCE_RESOLVED_NDC_NOT_PROMOTED", "SOURCE_RESOLVED requires confirmed NDC status", component=ref))
        if component.get("confidence") not in {"HIGH", "VERY_HIGH"}:
            issues.append(_issue("SOURCE_RESOLVED_CONFIDENCE_LOW", "SOURCE_RESOLVED requires high confidence", component=ref))
        if component.get("blockingReasons") not in ([], None):
            issues.append(_issue("SOURCE_RESOLVED_HAS_BLOCKERS", "SOURCE_RESOLVED cannot retain blockers", component=ref, blockers=component.get("blockingReasons")))
    if readiness == "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT" and target_status != "SOURCE_RESOLVED":
        issues.append(_issue("READINESS_WITHOUT_SOURCE_RESOLUTION", "Preflight eligibility requires SOURCE_RESOLVED", component=ref))
    if component.get("instancePolicy") == "REPEATED_BY_DATA" and component.get("instanceIdPattern"):
        issues.append(_issue("DATA_INSTANCE_IDS_FORBIDDEN", "Repeated-by-data components must not mint per-row IDs", component=ref))
    return issues


def _alias_target(alias: dict[str, Any]) -> str | None:
    value = alias.get("canonicalComponentUiId") or alias.get("canonicalId") or alias.get("to")
    return str(value) if value else None


def _is_component_alias(alias: dict[str, Any]) -> bool:
    return bool(alias.get("canonicalComponentUiId")) or alias.get("aliasKind") in (None, "componentUiId")


def _alias_edges(aliases: Iterable[dict[str, Any]]) -> dict[str, str]:
    edges: dict[str, str] = {}
    for alias in aliases:
        if not _is_component_alias(alias):
            continue
        source = alias.get("aliasId") or alias.get("legacyId") or alias.get("from")
        target = _alias_target(alias)
        if source and target:
            edges[str(source)] = str(target)
    return edges


def _alias_cycles(edges: dict[str, str]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visited: set[str] = set()
    for start in sorted(edges):
        if start in visited: continue
        path: list[str] = []
        index: dict[str, int] = {}
        cur = start
        while cur in edges:
            if cur in index:
                cycles.append(path[index[cur]:] + [cur])
                break
            if cur in visited: break
            index[cur] = len(path)
            path.append(cur)
            cur = edges[cur]
        visited.update(path)
    return cycles


def validate_batches(batches: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    contract_hashes: set[str] = set()
    ids: dict[tuple[str, str], str] = {}
    all_aliases: list[dict[str, Any]] = []
    all_components: list[dict[str, Any]] = []
    aliases_by_id: dict[str, str] = {}
    batch_ids: set[str] = set()
    component_count = 0
    for index, batch in enumerate(batches):
        missing = sorted(REQUIRED_BATCH_FIELDS.difference(batch.keys()))
        if missing:
            issues.append(_issue("BATCH_MISSING_FIELDS", "Batch contract is incomplete", batch=index, missing=missing))
        runtime = batch.get("runtimeAlias")
        if runtime not in (*RUNTIME_ALIASES, "contract"):
            issues.append(_issue("BATCH_INVALID_RUNTIME", "Batch runtimeAlias is not canonical", batch=index, value=runtime))
        schema_version = batch.get("schemaVersion")
        if batch.get("schema") == "prisma.ui.component-batch.v1" and schema_version != UIMAP_SCHEMA_VERSION:
            issues.append(_issue(
                "BATCH_SCHEMA_VERSION_MISMATCH",
                "Bridge only consumes the current canonical UIMAP batch schema",
                batch=index,
                expected=UIMAP_SCHEMA_VERSION,
                actual=schema_version,
            ))
        batch_id = str(batch.get("batchId") or "")
        if batch_id:
            if batch_id in batch_ids:
                issues.append(_issue("DUPLICATE_BATCH_ID", "batchId must be unique", batch=index, value=batch_id))
            batch_ids.add(batch_id)
            if batch.get("supersedesBatchId") == batch_id:
                issues.append(_issue("BATCH_SELF_SUPERSEDES", "A batch cannot supersede itself", batch=index, value=batch_id))
        integrity = batch.get("integrity")
        if batch.get("schema") == "prisma.ui.component-batch.v1" and isinstance(integrity, dict):
            expected_integrity = integrity.get("canonicalPayloadSha256")
            unsigned_batch = dict(batch)
            unsigned_batch.pop("integrity", None)
            actual_integrity = add_integrity(unsigned_batch)["integrity"]["canonicalPayloadSha256"]
            if expected_integrity != actual_integrity:
                issues.append(_issue(
                    "BATCH_INTEGRITY_MISMATCH",
                    "Immutable UIMAP batch payload hash does not match",
                    batch=index,
                    batchId=batch_id,
                    expected=expected_integrity,
                    actual=actual_integrity,
                ))
        contract_hash = batch.get("contractHash")
        if contract_hash: contract_hashes.add(str(contract_hash))
        components = batch.get("components", [])
        if not isinstance(components, list):
            issues.append(_issue("BATCH_COMPONENTS_NOT_ARRAY", "components must be an array", batch=index))
            continue
        component_count += len(components)
        for component in components:
            if not isinstance(component, dict):
                issues.append(_issue("COMPONENT_NOT_OBJECT", "Component record must be an object", batch=index))
                continue
            all_components.append(component)
            issues.extend(validate_component(component))
            fingerprint = canonical_sha256(component)
            for kind in ("componentId", "componentUiId"):
                value = component.get(kind)
                if not value: continue
                key = (kind, str(value))
                if key in ids and ids[key] != fingerprint:
                    issues.append(_issue("DUPLICATE_CANONICAL_ID", "Canonical ID resolves to different records", kind=kind, value=value))
                ids[key] = fingerprint
        aliases = batch.get("aliases", [])
        if isinstance(aliases, list):
            for alias in aliases:
                if not isinstance(alias, dict):
                    issues.append(_issue("ALIAS_NOT_OBJECT", "Alias record must be an object", batch=index))
                    continue
                all_aliases.append(alias)
                alias_id = alias.get("aliasId") or alias.get("legacyId") or alias.get("from")
                target = _alias_target(alias)
                if alias_id and target and _is_component_alias(alias):
                    previous = aliases_by_id.get(str(alias_id))
                    if previous is not None and previous != target:
                        issues.append(_issue(
                            "ALIAS_TARGET_CONFLICT",
                            "One alias resolves to multiple canonical targets",
                            aliasId=str(alias_id),
                            targets=sorted({previous, target}),
                        ))
                    aliases_by_id[str(alias_id)] = target
    if len(contract_hashes) > 1:
        issues.append(_issue("CONTRACT_HASH_MISMATCH", "Batches do not share one immutable contractHash", values=sorted(contract_hashes)))
    edges = _alias_edges(all_aliases)
    for cycle in _alias_cycles(edges):
        issues.append(_issue("ALIAS_CYCLE", "Alias registry contains a cycle", cycle=cycle))
    for error in validate_alias_targets(all_components, all_aliases):
        issues.append(_issue(
            "ALIAS_TARGET_INVALID",
            "Alias target or provenance does not match its canonical UIMAP component",
            error=error,
        ))
    status = "PASS_BRIDGE_CONTRACT_VALIDATION" if not issues else "FAIL_BRIDGE_CONTRACT_VALIDATION"
    return {
        "schema": "prisma.ui.bridge.validation.v1",
        "status": status,
        "ok": not issues,
        "batchCount": len(batches),
        "componentCount": component_count,
        "contractHashes": sorted(contract_hashes),
        "issues": issues,
        "warnings": warnings,
    }
