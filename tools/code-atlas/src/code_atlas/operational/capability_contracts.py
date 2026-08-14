from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_VERSION = "code_atlas_capability_contract.v1"

MATURITY_ORDER = (
    "HEURISTIC",
    "SOURCE_BACKED",
    "CONTRACT_BACKED",
    "CROSSCHECKED",
    "NEGATIVE_TESTED",
    "REPRODUCIBLE",
    "RUNTIME_BACKED",
    "CERTIFIABLE",
)

FORMER_PLACEHOLDERS = {
    "snapshot_diff_engine",
    "surface_role_matrix",
    "operational_timeline",
    "client_risk_score",
    "orphan_detector",
    "staleness_monitor",
    "audit_completeness_matrix",
    "data_lineage_graph",
    "runtime_evidence_links",
    "atlas_query_console",
    "entity_detail_drawer",
    "historical_trend_mini_atlas",
    "client_setup_journey_map",
    "multi_tenant_leakage_guard",
    "golden_path_comparator",
}

# Runtime keys emitted by the current operational runner. Missing mappings are
# deliberate: a registry entry must not be promoted merely because it has a name.
RUNTIME_OUTPUT_KEYS: Mapping[str, str] = {
    "operational_evidence_atlas_row_level": "sales",
    "client_followup_atlas": "clients",
    "device_claim_crosscheck": "deviceClaimCrosscheck",
    "sales_lineage_matrix": "salesLineage",
    "snapshot_diff_engine": "snapshotDiffEngine",
    "surface_role_matrix": "surfaceRoleMatrix",
    "operational_timeline": "operationalTimeline",
    "client_risk_score": "clientRiskScore",
    "orphan_detector": "orphans",
    "duplicate_detector": "duplicates",
    "staleness_monitor": "stalenessMonitor",
    "schema_drift_guard": "schemaDriftGuard",
    "audit_completeness_matrix": "auditCompleteness",
    "data_lineage_graph": "dataLineageGraph",
    "runtime_evidence_links": "runtimeEvidenceLinks",
    "client_setup_journey_map": "clientSetupJourneyMap",
    "multi_tenant_leakage_guard": "multiTenantLeakageGuard",
    "golden_path_comparator": "goldenPathComparator",
}

DOCUMENT_OUTPUTS: Mapping[str, str] = {
    "why_this_is_red": "WHY_THIS_IS_RED.md",
    "human_operator_summary": "HUMAN_OPERATOR_SUMMARY.md",
    "machine_continuation_pack": "CONTINUATION_SUPREME.md",
    "atlas_manifest_plus": "ATLAS_MANIFEST_PLUS.json",
    "can_patch_decision": "CAN_PATCH_DECISION.md",
}

SPECIFIC_OVERRIDES: Mapping[str, Mapping[str, Any]] = {
    "snapshot_diff_engine": {
        "implementationState": "detector_v3_present",
        "maturity": "SOURCE_BACKED",
        "requiredContracts": ["comparable_snapshot_identity", "semantic_diff_contract"],
        "requiredNegativeTests": ["missing_baseline", "corrupt_archive", "same_file_list_changed_content"],
        "doesNotProve": [
            "Semantic equality of two snapshots.",
            "Row-level or runtime behavioral equivalence.",
        ],
    },
    "surface_role_matrix": {
        "implementationState": "detector_v3_present",
        "maturity": "SOURCE_BACKED",
        "requiredContracts": ["surface_role_authority", "route_owner_binding"],
        "requiredNegativeTests": ["missing_surface_root", "misowned_route"],
        "doesNotProve": ["Runtime role enforcement or authorization."],
    },
    "operational_timeline": {
        "implementationState": "detector_v3_present",
        "maturity": "HEURISTIC",
        "requiredContracts": ["event_time_contract", "event_identity_contract", "evidence_freshness_contract"],
        "requiredNegativeTests": ["out_of_order_events", "duplicate_event", "stale_evidence"],
        "doesNotProve": ["Causal ordering from ZIP discovery alone."],
    },
    "client_risk_score": {
        "implementationState": "detector_v3_present",
        "maturity": "HEURISTIC",
        "requiredContracts": ["risk_signal_schema", "risk_weight_policy", "risk_confidence_policy", "risk_threshold_policy"],
        "requiredNegativeTests": ["missing_signal", "conflicting_signals", "stale_signal"],
        "doesNotProve": ["A calibrated client risk score from two boolean/status signals."],
    },
    "orphan_detector": {
        "implementationState": "detector_v3_present",
        "maturity": "HEURISTIC",
        "requiredContracts": ["entity_parent_contract", "scope_identity_contract"],
        "requiredNegativeTests": ["cross_scope_parent", "missing_parent", "ambiguous_parent"],
        "doesNotProve": ["True referential orphan status from field-name regex presence."],
    },
    "staleness_monitor": {
        "implementationState": "detector_v3_present",
        "maturity": "HEURISTIC",
        "requiredContracts": ["freshness_policy", "evidence_timestamp_contract", "clock_policy"],
        "requiredNegativeTests": ["expired_evidence", "future_timestamp", "missing_timestamp"],
        "doesNotProve": ["Freshness from the mere presence of timestamp-like fields."],
    },
    "audit_completeness_matrix": {
        "implementationState": "detector_v3_present",
        "maturity": "HEURISTIC",
        "requiredContracts": ["auditable_action_catalog", "audit_event_contract", "audit_coverage_policy"],
        "requiredNegativeTests": ["missing_audit_event", "duplicate_audit_event", "wrong_scope_audit_event"],
        "doesNotProve": ["Audit completeness from the existence of an audit table."],
    },
    "data_lineage_graph": {
        "implementationState": "detector_v3_present",
        "maturity": "HEURISTIC",
        "requiredContracts": ["entity_identity_contract", "provenance_edge_contract", "canonical_projection_contract"],
        "requiredNegativeTests": ["broken_edge", "cross_scope_edge", "cycle_or_duplicate_edge"],
        "doesNotProve": ["Complete data lineage from status-derived synthetic edges."],
    },
    "runtime_evidence_links": {
        "implementationState": "detector_v3_present",
        "maturity": "SOURCE_BACKED",
        "requiredContracts": ["evidence_bundle_identity", "artifact_digest_contract", "evidence_freshness_contract"],
        "requiredNegativeTests": ["digest_mismatch", "missing_required_entry", "expired_artifact"],
        "doesNotProve": ["Evidence validity or freshness from archive names and entry names alone."],
    },
    "atlas_query_console": {
        "implementationState": "viewer_filter_present",
        "maturity": "HEURISTIC",
        "requiredContracts": ["typed_query_contract", "query_result_contract", "query_scope_contract"],
        "requiredNegativeTests": ["invalid_field", "cross_scope_query", "ambiguous_entity"],
        "doesNotProve": ["A typed Atlas query engine from text filtering serialized JSON."],
    },
    "entity_detail_drawer": {
        "implementationState": "viewer_preview_present",
        "maturity": "HEURISTIC",
        "requiredContracts": ["entity_identity_contract", "entity_detail_contract", "provenance_link_contract"],
        "requiredNegativeTests": ["missing_entity", "duplicate_identity", "cross_scope_entity"],
        "doesNotProve": ["Entity lookup or provenance-aware detail from displaying the first row."],
    },
    "historical_trend_mini_atlas": {
        "implementationState": "registry_only_no_runtime_output",
        "maturity": "HEURISTIC",
        "requiredContracts": ["historical_snapshot_contract", "metric_identity_contract", "trend_window_contract"],
        "requiredNegativeTests": ["single_snapshot", "non_comparable_metric", "time_gap"],
        "doesNotProve": ["Historical trend capability without a dedicated runtime output."],
    },
    "client_setup_journey_map": {
        "implementationState": "detector_v3_present",
        "maturity": "SOURCE_BACKED",
        "requiredContracts": ["journey_step_contract", "client_license_device_link_contract", "step_order_contract"],
        "requiredNegativeTests": ["missing_step", "out_of_order_step", "cross_client_step"],
        "doesNotProve": ["A completed onboarding journey from aggregate row counts."],
    },
    "multi_tenant_leakage_guard": {
        "implementationState": "scope_presence_detector_blocked",
        "maturity": "HEURISTIC",
        "requiredContracts": ["tenant_scope_contract", "business_scope_contract", "entity_scope_binding", "negative_isolation_test_contract"],
        "requiredNegativeTests": ["cross_tenant_read", "cross_tenant_join", "cross_business_projection", "wrong_scope_runtime_evidence"],
        "doesNotProve": [
            "Tenant isolation from the presence of tenant/scope terms or columns.",
            "Absence of cross-tenant leakage without negative isolation tests.",
        ],
        "hardBlockers": ["negative_cross_tenant_tests_missing", "runtime_isolation_evidence_required"],
    },
    "golden_path_comparator": {
        "implementationState": "detector_v3_present",
        "maturity": "HEURISTIC",
        "requiredContracts": ["golden_path_contract", "step_evidence_contract", "comparison_tolerance_policy"],
        "requiredNegativeTests": ["missing_step", "wrong_order", "evidence_mismatch"],
        "doesNotProve": ["Golden-path equivalence from a single production-gate status row."],
    },
}


def _base_spec(feature: Mapping[str, Any]) -> dict[str, Any]:
    legacy_status = str(feature.get("status", "unknown"))
    was_placeholder = "placeholder" in legacy_status
    return {
        "schemaVersion": SCHEMA_VERSION,
        "capabilityId": str(feature["id"]),
        "title": str(feature.get("title", feature["id"])),
        "legacyRegistryStatus": legacy_status,
        "legacyRegistryNote": str(feature.get("note", "")),
        "legacyPlaceholder": was_placeholder,
        "implementationState": "legacy_v1_heuristic" if not was_placeholder else "legacy_placeholder_reconciled",
        "maturity": "HEURISTIC",
        "runtimeBinding": RUNTIME_OUTPUT_KEYS.get(str(feature["id"])) or DOCUMENT_OUTPUTS.get(str(feature["id"])) or "legacy_or_unbound",
        "requiredContracts": [],
        "requiredNegativeTests": [],
        "hardBlockers": [],
        "doesNotProve": [
            "Production certification.",
            "Runtime correctness outside the evidence explicitly attached to this capability.",
        ],
        "certifiable": False,
        "productionCertified": False,
    }


def build_capability_specs(features: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for feature in features:
        row = _base_spec(feature)
        override = SPECIFIC_OVERRIDES.get(row["capabilityId"])
        if override:
            row.update({key: (list(value) if isinstance(value, tuple) else value) for key, value in override.items()})
        # Conservative rule: current hardening establishes truthfulness, not certification.
        row["certifiable"] = False
        row["productionCertified"] = False
        specs.append(row)
    validate_capability_specs(specs)
    return specs


def validate_capability_specs(specs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    ids = [str(row.get("capabilityId", "")) for row in specs]
    if len(specs) != 50:
        raise ValueError(f"expected 50 capabilities, got {len(specs)}")
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate capabilityId")
    required = {
        "schemaVersion", "capabilityId", "title", "legacyRegistryStatus",
        "implementationState", "maturity", "runtimeBinding",
        "requiredContracts", "requiredNegativeTests", "doesNotProve",
        "certifiable", "productionCertified",
    }
    for row in specs:
        missing = required - set(row)
        if missing:
            raise ValueError(f"{row.get('capabilityId')}: missing {sorted(missing)}")
        if row["maturity"] not in MATURITY_ORDER:
            raise ValueError(f"{row['capabilityId']}: invalid maturity {row['maturity']}")
        if row["certifiable"] or row["productionCertified"]:
            raise ValueError(f"{row['capabilityId']}: hardening v1 may not certify production")
        if not row["doesNotProve"]:
            raise ValueError(f"{row['capabilityId']}: doesNotProve must be explicit")
    return {
        "status": "PASS_CAPABILITY_CONTRACTS_VALID",
        "featureCount": len(specs),
        "uniqueIds": len(set(ids)),
        "formerPlaceholderCount": sum(1 for row in specs if row["capabilityId"] in FORMER_PLACEHOLDERS),
    }


def observe_runtime_bindings(
    specs: Sequence[Mapping[str, Any]],
    payload: Mapping[str, Any],
    output_files: Iterable[str] = (),
) -> list[dict[str, Any]]:
    files = set(output_files)
    out: list[dict[str, Any]] = []
    for spec in specs:
        row = dict(spec)
        cap = row["capabilityId"]
        key = RUNTIME_OUTPUT_KEYS.get(cap)
        doc = DOCUMENT_OUTPUTS.get(cap)
        if key:
            observed = key in payload and payload.get(key) is not None
            observation = f"payload:{key}"
        elif doc:
            observed = doc in files
            observation = f"file:{doc}"
        else:
            observed = False
            observation = "no_primary_runtime_binding_declared"
        row["runtimeOutputObserved"] = bool(observed)
        row["runtimeObservation"] = observation
        if not observed and row["implementationState"] == "detector_v3_present":
            row["implementationState"] = "detector_code_claim_without_observed_runtime_output"
            row["hardBlockers"] = list(dict.fromkeys([*row.get("hardBlockers", []), "runtime_output_not_observed"]))
        out.append(row)
    return out


def summarize_capabilities(specs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    maturity = Counter(str(row["maturity"]) for row in specs)
    observed = sum(bool(row.get("runtimeOutputObserved")) for row in specs)
    blocked = sum(bool(row.get("hardBlockers")) for row in specs)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "SOURCE_HARDENED_NOT_PRODUCTION_CERTIFIED",
        "featureCount": len(specs),
        "runtimeOutputObservedCount": observed,
        "hardBlockedCapabilityCount": blocked,
        "maturityCounts": dict(sorted(maturity.items())),
        "certifiableCount": 0,
        "productionCertifiedCount": 0,
        "rule": "detector existence != contract maturity != certification",
    }


def legacy_placeholder_ledger(specs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in specs:
        if spec["capabilityId"] not in FORMER_PLACEHOLDERS:
            continue
        rows.append({
            "feature": spec["capabilityId"],
            "legacyPlaceholder": True,
            "detectorOrViewerState": spec["implementationState"],
            "runtimeOutputObserved": bool(spec.get("runtimeOutputObserved")),
            "maturity": spec["maturity"],
            "certifiable": False,
            "productionCertified": False,
            "hardBlockers": list(spec.get("hardBlockers", [])),
            "doesNotProve": list(spec.get("doesNotProve", [])),
        })
    return rows


def harden_multi_tenant_guard(existing: Any) -> list[dict[str, Any]]:
    current = existing[0] if isinstance(existing, list) and existing and isinstance(existing[0], dict) else {}
    return [{
        **current,
        "status": "BLOCKED_NEGATIVE_ISOLATION_TESTS_REQUIRED",
        "scopeAuthorityObserved": current.get("status") == "PASS_SCOPE_AUTHORITY_FOUND",
        "certifiable": False,
        "productionCertified": False,
        "requiredNegativeTests": list(SPECIFIC_OVERRIDES["multi_tenant_leakage_guard"]["requiredNegativeTests"]),
        "doesNotProve": list(SPECIFIC_OVERRIDES["multi_tenant_leakage_guard"]["doesNotProve"]),
        "rule": "scope presence is necessary but never sufficient to certify tenant isolation",
    }]
