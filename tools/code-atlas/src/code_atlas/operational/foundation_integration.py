from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .assurance_foundation import (
    build_audit_completeness,
    build_staleness_rows,
    harden_runtime_evidence_links,
)
from .evidence_foundation import make_evidence_record, parse_timestamp
from .lineage_foundation import build_lineage_graph
from .temporal_foundation import (
    build_timeline,
    compare_semantic_snapshots,
    discover_prior_snapshots,
    historical_trend,
    make_semantic_snapshot,
)

FOUNDATION_VERSION = "code_atlas_operational_foundations.v1"

ENTITY_CAPABILITY = {
    "clients": "client_followup_atlas",
    "licenses": "contract_coverage_matrix",
    "devices": "device_claim_crosscheck",
    "sales": "sales_lineage_matrix",
}

AGGREGATE_CAPABILITY = {
    "deviceClaimCrosscheck": "device_claim_crosscheck",
    "salesLineage": "sales_lineage_matrix",
    "tenantScopeResolver": "safe_scope_guard",
    "schemaDriftGuard": "schema_drift_guard",
    "surfaceRoleMatrix": "surface_role_matrix",
    "supportResolverSummary": "support_ticket_generator",
}

TREND_METRICS = (
    "rows.clients",
    "rows.licenses",
    "rows.devices",
    "rows.sales",
)


def _observed_at(manifest: Mapping[str, Any]) -> str:
    for key in ("createdAt", "created_at", "generatedAt", "generated_at"):
        value = manifest.get(key)
        if parse_timestamp(value) is not None:
            return str(value)
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _evidence_records(payload: Mapping[str, Any], manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    observed = _observed_at(manifest)
    records = []
    for section, capability in ENTITY_CAPABILITY.items():
        rows = payload.get(section)
        if not isinstance(rows, list):
            continue
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                continue
            fields = row.get("fields") if isinstance(row.get("fields"), Mapping) else row
            entity_id = row.get("entityId") or row.get("id") or f"row_{index}"
            record = make_evidence_record(
                capability_id=capability,
                source_kind="operational_row",
                source_ref=f"{section}:{entity_id}",
                observed_at=observed,
                trust_level="SOURCE",
                payload=fields,
                scope=fields,
                claims=(f"Operational runner emitted sanitized {section} row evidence.",),
                does_not_prove=(
                    "Production correctness or completeness outside this emitted row.",
                    "Tenant isolation unless negative isolation evidence is attached.",
                ),
            )
            records.append(record.as_dict())
    for section, capability in AGGREGATE_CAPABILITY.items():
        value = payload.get(section)
        if value is None:
            continue
        record = make_evidence_record(
            capability_id=capability,
            source_kind="operational_section",
            source_ref=section,
            observed_at=observed,
            trust_level="SOURCE",
            payload=value,
            claims=(f"Operational runner emitted section {section}.",),
            does_not_prove=("Production certification from section presence alone.",),
        )
        records.append(record.as_dict())
    return sorted(records, key=lambda row: (str(row.get("observedAt")), str(row.get("recordId"))))


def apply_operational_foundations(
    payload: dict[str, Any],
    manifest: Mapping[str, Any],
    *,
    result_root: str | Path | None = None,
) -> dict[str, Any]:
    observed = _observed_at(manifest)
    source_ref = str(manifest.get("tool") or "code_atlas_operational")
    evidence_records = _evidence_records(payload, manifest)

    current_snapshot = make_semantic_snapshot(
        payload,
        observed_at=observed,
        source_ref=source_ref,
    )
    prior_snapshots = discover_prior_snapshots(result_root)
    base_snapshot = prior_snapshots[-1] if prior_snapshots else None
    snapshot_diff = compare_semantic_snapshots(base_snapshot, current_snapshot)
    trend_snapshots = [*prior_snapshots, current_snapshot]
    trend_rows = [historical_trend(trend_snapshots, metric) for metric in TREND_METRICS]

    timeline = build_timeline(evidence_records)
    graph = build_lineage_graph(payload)
    runtime_links = harden_runtime_evidence_links(payload.get("runtimeEvidenceLinks"))

    policies = payload.get("freshnessPolicies")
    if not isinstance(policies, Mapping):
        policies = {}
    typed_policies = {key: value for key, value in policies.items() if hasattr(value, "ttl_seconds")}
    staleness = build_staleness_rows(evidence_records, typed_policies, now=observed)

    required_actions = payload.get("auditActionCatalog")
    if not isinstance(required_actions, list):
        required_actions = None
    audit_events = payload.get("auditEvents")
    if not isinstance(audit_events, list):
        audit_events = []
    audit = build_audit_completeness(required_actions, audit_events)

    payload["evidenceRecords"] = evidence_records
    payload["snapshotDiffEngine"] = [snapshot_diff]
    payload["historicalTrendMiniAtlas"] = trend_rows
    payload["operationalTimeline"] = timeline["events"] or [{
        "status": timeline["status"],
        "invalidEvidence": timeline["invalidEvidence"],
        "duplicateEvidenceIds": timeline["duplicateEvidenceIds"],
        "productionCertified": False,
    }]
    payload["operationalTimelineMeta"] = {key: value for key, value in timeline.items() if key != "events"}
    payload["dataLineageGraph"] = graph["edges"] or [{
        "status": "BLOCKED_NO_EXPLICIT_LINEAGE_EDGES",
        "productionCertified": False,
    }]
    payload["lineageGraphMeta"] = {
        key: value for key, value in graph.items() if key not in {"nodes", "edges", "orphans"}
    }
    payload["lineageNodes"] = graph["nodes"]
    payload["orphans"] = graph["orphans"]
    payload["stalenessMonitor"] = staleness
    payload["auditCompleteness"] = audit
    payload["runtimeEvidenceLinks"] = runtime_links

    outputs = {
        "EVIDENCE_RECORDS.json": evidence_records,
        "SEMANTIC_SNAPSHOT.json": current_snapshot,
        "SNAPSHOT_DIFF_ENGINE.json": snapshot_diff,
        "HISTORICAL_TREND_MINI_ATLAS.json": trend_rows,
        "OPERATIONAL_TIMELINE.json": timeline,
        "DATA_LINEAGE_GRAPH.json": graph,
        "ORPHAN_ENTITY_MATRIX.json": graph["orphans"],
        "STALE_DATA_MATRIX.json": staleness,
        "AUDIT_COMPLETENESS_MATRIX.json": audit,
        "RUNTIME_EVIDENCE_LINKS.json": runtime_links,
    }

    blockers = []
    if snapshot_diff.get("status") == "BLOCKED_MISSING_BASELINE":
        blockers.append("snapshot_baseline_missing")
    if any(str(row.get("status", "")).startswith("BLOCKED") for row in trend_rows):
        blockers.append("historical_trend_insufficient_history")
    if any(str(row.get("status", "")).startswith("BLOCKED") for row in staleness):
        blockers.append("freshness_policy_or_evidence_missing")
    if audit and str(audit[0].get("status", "")).startswith("BLOCKED"):
        blockers.append("audit_catalog_or_events_incomplete")
    if graph.get("blockers"):
        blockers.extend(f"lineage:{item}" for item in graph["blockers"])
    if any(str(row.get("status", "")).startswith("BLOCKED") for row in runtime_links):
        blockers.append("runtime_evidence_links_incomplete")

    summary = {
        "foundationVersion": FOUNDATION_VERSION,
        "status": "SOURCE_FOUNDATIONS_READY_WITH_BLOCKERS" if blockers else "SOURCE_FOUNDATIONS_READY",
        "evidenceRecordCount": len(evidence_records),
        "priorSnapshotCount": len(prior_snapshots),
        "lineageNodeCount": len(graph["nodes"]),
        "lineageEdgeCount": len(graph["edges"]),
        "blockers": sorted(set(blockers)),
        "certifiable": False,
        "productionCertified": False,
        "doesNotProve": [
            "Production readiness from source-only foundation tests.",
            "Tenant isolation without negative cross-tenant runtime evidence.",
        ],
    }
    outputs["FOUNDATION_HARDENING_SUMMARY.json"] = summary
    return {
        "payload": payload,
        "outputs": outputs,
        "summary": summary,
        "currentSnapshot": current_snapshot,
    }
