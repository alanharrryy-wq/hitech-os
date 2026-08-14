from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .assurance_foundation import (
    build_audit_completeness,
    build_staleness_rows,
    harden_runtime_evidence_links,
)
from .evidence_foundation import make_evidence_record, normalize_timestamp, parse_freshness_policies, parse_timestamp
from .lineage_foundation import build_lineage_graph
from .temporal_foundation import (
    SNAPSHOT_SCHEMA_VERSION,
    build_timeline,
    compare_semantic_snapshots,
    discover_prior_snapshots,
    historical_trend,
    make_semantic_snapshot,
    resolve_repository_identity,
)

FOUNDATION_VERSION = "code_atlas_operational_foundations.v1.1"

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


def _observed_at(manifest: Mapping[str, Any]) -> str | None:
    for key in ("observedAt", "observed_at", "createdAt", "created_at", "generatedAt", "generated_at"):
        value = manifest.get(key)
        if parse_timestamp(value) is not None:
            return normalize_timestamp(value)
    return None


def _evidence_records(payload: Mapping[str, Any], observed: str | None) -> list[dict[str, Any]]:
    if observed is None:
        return []
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


def _blocked_snapshot(status: str, *, repository_identity: str | None = None) -> dict[str, Any]:
    return {
        "schemaVersion": SNAPSHOT_SCHEMA_VERSION,
        "status": status,
        "repositoryIdentity": repository_identity,
        "certifiable": False,
        "productionCertified": False,
    }


def apply_operational_foundations(
    payload: dict[str, Any],
    manifest: Mapping[str, Any],
    *,
    repo_root: str | Path | None = None,
    result_root: str | Path | None = None,
) -> dict[str, Any]:
    observed = _observed_at(manifest)
    source_ref = str(manifest.get("tool") or "code_atlas_operational")
    repository = resolve_repository_identity(repo_root, manifest)
    repository_identity = repository.get("repositoryIdentity")
    evidence_records = _evidence_records(payload, observed)

    prior_snapshots: list[dict[str, Any]] = []
    if observed is None:
        current_snapshot = _blocked_snapshot(
            "BLOCKED_MISSING_OBSERVED_AT",
            repository_identity=str(repository_identity) if repository_identity else None,
        )
        snapshot_diff = {
            "status": "BLOCKED_MISSING_OBSERVED_AT",
            "comparable": False,
            "productionCertified": False,
        }
        trend_rows = [
            {
                "status": "BLOCKED_CURRENT_SNAPSHOT_UNAVAILABLE",
                "reason": "MISSING_OBSERVED_AT",
                "metric": metric,
                "points": [],
                "productionCertified": False,
            }
            for metric in TREND_METRICS
        ]
    elif not repository_identity:
        current_snapshot = _blocked_snapshot("BLOCKED_REPOSITORY_IDENTITY_UNAVAILABLE")
        snapshot_diff = {
            "status": "BLOCKED_REPOSITORY_IDENTITY_UNAVAILABLE",
            "comparable": False,
            "productionCertified": False,
        }
        trend_rows = [
            {
                "status": "BLOCKED_REPOSITORY_IDENTITY_UNAVAILABLE",
                "metric": metric,
                "points": [],
                "productionCertified": False,
            }
            for metric in TREND_METRICS
        ]
    else:
        current_snapshot = make_semantic_snapshot(
            payload,
            observed_at=observed,
            source_ref=source_ref,
            repository_identity=str(repository_identity),
        )
        prior_snapshots = discover_prior_snapshots(
            result_root,
            expected_repository_identity=str(repository_identity),
        )
        base_snapshot = prior_snapshots[-1] if prior_snapshots else None
        snapshot_diff = compare_semantic_snapshots(base_snapshot, current_snapshot)
        trend_snapshots = [*prior_snapshots, current_snapshot]
        trend_rows = [historical_trend(trend_snapshots, metric) for metric in TREND_METRICS]

    timeline = build_timeline(evidence_records)
    graph = build_lineage_graph(payload)
    runtime_links = harden_runtime_evidence_links(payload.get("runtimeEvidenceLinks"))

    typed_policies, policy_validation = parse_freshness_policies(payload.get("freshnessPolicies"))
    if observed is None:
        staleness = [{
            "status": "BLOCKED_MISSING_OBSERVED_AT",
            "fresh": False,
            "productionCertified": False,
        }]
    else:
        staleness = build_staleness_rows(evidence_records, typed_policies, now=observed)

    required_actions = payload.get("auditActionCatalog")
    if not isinstance(required_actions, list):
        required_actions = None
    audit_events = payload.get("auditEvents")
    if not isinstance(audit_events, list):
        audit_events = []
    audit_scope = payload.get("auditRequiredScope")
    if not isinstance(audit_scope, Mapping):
        audit_scope = payload.get("auditScope") if isinstance(payload.get("auditScope"), Mapping) else None
    audit = build_audit_completeness(required_actions, audit_events, required_scope=audit_scope)

    payload["repositoryIdentity"] = repository
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
    payload["freshnessPolicyValidation"] = policy_validation
    payload["stalenessMonitor"] = staleness
    payload["auditCompleteness"] = audit
    payload["runtimeEvidenceLinks"] = runtime_links

    outputs = {
        "REPOSITORY_IDENTITY.json": repository,
        "EVIDENCE_RECORDS.json": evidence_records,
        "SEMANTIC_SNAPSHOT.json": current_snapshot,
        "SNAPSHOT_DIFF_ENGINE.json": snapshot_diff,
        "HISTORICAL_TREND_MINI_ATLAS.json": trend_rows,
        "OPERATIONAL_TIMELINE.json": timeline,
        "DATA_LINEAGE_GRAPH.json": graph,
        "ORPHAN_ENTITY_MATRIX.json": graph["orphans"],
        "FRESHNESS_POLICY_VALIDATION.json": policy_validation,
        "STALE_DATA_MATRIX.json": staleness,
        "AUDIT_COMPLETENESS_MATRIX.json": audit,
        "RUNTIME_EVIDENCE_LINKS.json": runtime_links,
    }

    blockers: list[str] = []
    if observed is None:
        blockers.append("evidence_observed_at_missing_or_invalid")
    if not repository_identity:
        blockers.append("snapshot_repository_identity_unavailable")
    snapshot_status = str(snapshot_diff.get("status", ""))
    if snapshot_status == "BLOCKED_MISSING_BASELINE":
        blockers.append("snapshot_baseline_missing")
    elif snapshot_status.startswith("BLOCKED") and snapshot_status not in {
        "BLOCKED_MISSING_OBSERVED_AT",
        "BLOCKED_REPOSITORY_IDENTITY_UNAVAILABLE",
    }:
        blockers.append("snapshot_integrity_blocked")
    trend_statuses = [str(row.get("status", "")) for row in trend_rows]
    if any(status == "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS" for status in trend_statuses):
        blockers.append("historical_trend_insufficient_history")
    if any(status.startswith("BLOCKED") and status != "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS" for status in trend_statuses):
        blockers.append("historical_trend_integrity_blocked")
    if str(timeline.get("status", "")).startswith("BLOCKED"):
        blockers.append("operational_timeline_integrity")
    if any(str(row.get("status", "")).startswith("BLOCKED") for row in policy_validation):
        blockers.append("freshness_policy_contract_invalid")
    if any(str(row.get("status", "")).startswith("BLOCKED") for row in staleness):
        blockers.append("freshness_policy_or_evidence_missing")
    if audit and str(audit[0].get("status", "")) != "PASS_AUDIT_COVERAGE":
        blockers.append("audit_catalog_or_events_incomplete")
    if graph.get("blockers"):
        blockers.extend(f"lineage:{item}" for item in graph["blockers"])
    if any(str(row.get("status", "")).startswith("BLOCKED") for row in runtime_links):
        blockers.append("runtime_evidence_links_incomplete")

    summary = {
        "foundationVersion": FOUNDATION_VERSION,
        "status": "SOURCE_FOUNDATIONS_READY_WITH_BLOCKERS" if blockers else "SOURCE_FOUNDATIONS_READY",
        "repositoryIdentityStatus": repository.get("status"),
        "evidenceObservedAtStatus": "PASS_OBSERVED_AT_VALID" if observed else "BLOCKED_MISSING_OR_INVALID_OBSERVED_AT",
        "evidenceRecordCount": len(evidence_records),
        "priorSnapshotCount": len(prior_snapshots),
        "lineageNodeCount": len(graph["nodes"]),
        "lineageEdgeCount": len(graph["edges"]),
        "timelineStatus": timeline.get("status"),
        "blockers": sorted(set(blockers)),
        "certifiable": False,
        "productionCertified": False,
        "doesNotProve": [
            "Production readiness from source-only foundation tests.",
            "Tenant isolation without negative cross-tenant runtime evidence.",
            "Historical comparability across repositories without a stable repository identity.",
        ],
    }
    outputs["FOUNDATION_HARDENING_SUMMARY.json"] = summary
    return {
        "payload": payload,
        "outputs": outputs,
        "summary": summary,
        "currentSnapshot": current_snapshot,
    }
