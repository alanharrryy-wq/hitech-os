from __future__ import annotations

FEATURE_REGISTRY_VERSION = "2.0.0"
LEGACY_STATUS_FIELD = "status"
LEGACY_STATUS_SEMANTICS = (
    "Compatibility-only historical status. It proves neither current runtime "
    "binding nor contract maturity nor production certification."
)

_PLACEHOLDER_IDS = {
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
    "golden_path_comparator",
}
_BLOCKED_ID = "multi_tenant_leakage_guard"
_FEATURE_IDS = (
    "operational_evidence_atlas_row_level",
    "client_followup_atlas",
    "device_claim_crosscheck",
    "sales_lineage_matrix",
    "flow_health_map",
    "breakage_radar",
    "snapshot_diff_engine",
    "contract_coverage_matrix",
    "customer_visible_scanner",
    "surface_role_matrix",
    "operational_timeline",
    "why_this_is_red",
    "client_risk_score",
    "next_best_action_engine",
    "orphan_detector",
    "duplicate_detector",
    "staleness_monitor",
    "schema_drift_guard",
    "fixture_contamination_scanner",
    "audit_completeness_matrix",
    "data_lineage_graph",
    "impact_radius_calculator",
    "safe_fix_recommendation_map",
    "verifier_coverage_map",
    "runtime_evidence_links",
    "api_data_map",
    "secret_exposure_guard",
    "production_gate_readiness",
    "human_operator_summary",
    "machine_continuation_pack",
    "atlas_query_console",
    "entity_detail_drawer",
    "evidence_confidence_score",
    "ownership_map",
    "do_not_touch_map",
    "safe_scope_guard",
    "data_quality_ruleset",
    "reconciliation_recipes",
    "alert_rules_export",
    "evidence_bundle_index",
    "pii_privacy_classifier",
    "support_ticket_generator",
    "release_readiness_matrix",
    "historical_trend_mini_atlas",
    "trust_source_level_per_datum",
    "atlas_manifest_plus",
    "can_patch_decision",
    "client_setup_journey_map",
    "multi_tenant_leakage_guard",
    "golden_path_comparator",
)


def _title(feature_id: str) -> str:
    return " ".join(word.upper() if word in {"api", "pii"} else word.capitalize() for word in feature_id.split("_"))


def _status(feature_id: str) -> str:
    if feature_id == _BLOCKED_ID:
        return "placeholder_blocked"
    if feature_id in _PLACEHOLDER_IDS:
        return "placeholder_v1"
    return "implemented_v1"


FEATURE_SPECS = [
    {
        "id": feature_id,
        "title": _title(feature_id),
        "status": _status(feature_id),
        "note": (
            "Legacy registry placeholder; current implementation and certification state are resolved by the hardening contract."
            if feature_id in _PLACEHOLDER_IDS or feature_id == _BLOCKED_ID
            else "Legacy compatibility entry; current implementation and certification state are resolved by the hardening contract."
        ),
    }
    for feature_id in _FEATURE_IDS
]


def get_hardened_feature_specs():
    from .capability_contracts import build_capability_specs

    return build_capability_specs(FEATURE_SPECS)


def validate_feature_registry():
    from .capability_contracts import validate_capability_specs

    return validate_capability_specs(get_hardened_feature_specs())


__all__ = [
    "FEATURE_REGISTRY_VERSION",
    "FEATURE_SPECS",
    "LEGACY_STATUS_FIELD",
    "LEGACY_STATUS_SEMANTICS",
    "get_hardened_feature_specs",
    "validate_feature_registry",
]
