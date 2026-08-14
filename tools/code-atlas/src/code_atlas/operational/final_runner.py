from __future__ import annotations

import csv
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .capability_contracts import MATURITY_ORDER
from .evidence_foundation import ScopeIdentity, canonical_digest
from .hardened_runner import run_operational_atlas as _run_hardened_operational_atlas
from .risk_scope_foundation import evaluate_client_risk, evaluate_tenant_isolation

FINAL_HARDENING_VERSION = "code_atlas_source_hardening.v1"
ENTITY_SECTIONS = {"clients": "client", "licenses": "license", "devices": "device", "sales": "sale", "evidenceRecords": "evidence", "lineageNodes": "lineage_node"}
QUERY_FIELDS = {"entityId", "kind", "sourceRef", "scope.tenant_id", "scope.business_id", "scope.client_id", "scope.store_id", "scope.terminal_id", "scope.device_id"}
QUERY_OPERATORS = {"eq", "ne", "in", "prefix"}
GENERIC_CONTRACTS = ("capability_output_shape_contract", "source_provenance_contract", "no_fake_green_contract")
GENERIC_NEGATIVE_TESTS = ("missing_or_invalid_source_evidence", "ambiguous_or_invalid_output", "unexpected_certification_claim")
SOURCE_OVERRIDES = {
    "client_risk_score": ("risk_score_contract_engine_v1", "NEGATIVE_TESTED"),
    "multi_tenant_leakage_guard": ("negative_isolation_evaluator_v1", "NEGATIVE_TESTED"),
    "atlas_query_console": ("typed_scope_aware_query_engine_v1", "NEGATIVE_TESTED"),
    "entity_detail_drawer": ("identity_scope_provenance_detail_engine_v1", "NEGATIVE_TESTED"),
    "client_setup_journey_map": ("relationship_backed_journey_engine_v1", "CONTRACT_BACKED"),
    "golden_path_comparator": ("ordered_evidence_comparator_v1", "NEGATIVE_TESTED"),
}


def _dedupe(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple, set)):
        values = [] if values in (None, "") else [values]
    return list(dict.fromkeys(str(value) for value in values if str(value).strip()))


def _fields(row: Mapping[str, Any]) -> Mapping[str, Any]:
    value = row.get("fields")
    return value if isinstance(value, Mapping) else row


def _identity(section: str, row: Mapping[str, Any]) -> tuple[str, str]:
    for key in ("entityId", "recordId", "nodeId", "eventId", "id", "uuid"):
        if row.get(key) not in (None, ""):
            return str(row[key]), "explicit"
    digest = canonical_digest({"section": section, "row": row})
    return f"synthetic:{digest[:20]}", "synthetic_digest"


def _scope(row: Mapping[str, Any]) -> ScopeIdentity:
    direct = row.get("scope")
    return ScopeIdentity.from_mapping(direct if isinstance(direct, Mapping) else _fields(row))


def build_investigator_index(payload: Mapping[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    duplicates: list[str] = []
    seen: set[tuple[str, str]] = set()
    for section, kind in ENTITY_SECTIONS.items():
        rows = payload.get(section)
        if not isinstance(rows, list):
            continue
        for position, raw in enumerate(rows):
            if not isinstance(raw, Mapping):
                invalid.append({"section": section, "index": position, "reason": "NON_MAPPING_ROW"})
                continue
            entity_id, identity_mode = _identity(section, raw)
            key = (section, entity_id)
            if key in seen:
                duplicates.append(f"{section}:{entity_id}")
            seen.add(key)
            fields = _fields(raw)
            records.append({
                "section": section,
                "kind": str(raw.get("kind") or raw.get("entityKind") or kind),
                "entityId": entity_id,
                "identityMode": identity_mode,
                "scope": _scope(raw).as_dict(),
                "sourceRef": str(raw.get("sourceRef") or raw.get("evidenceRef") or raw.get("sourceDb") or f"{section}:{entity_id}"),
                "dataDigest": canonical_digest(fields),
                "data": dict(fields),
            })
    records.sort(key=lambda row: (row["section"], row["kind"], row["entityId"], row["dataDigest"]))
    edges: list[dict[str, Any]] = []
    for key in ("dataLineageGraph", "lineageEdges"):
        raw = payload.get(key)
        if isinstance(raw, list):
            edges.extend(dict(row) for row in raw if isinstance(row, Mapping) and row.get("from") and row.get("to"))
    edges.sort(key=lambda row: (str(row.get("from")), str(row.get("to")), str(row.get("type"))))
    return {
        "schemaVersion": FINAL_HARDENING_VERSION,
        "status": "INVESTIGATOR_INDEX_CONTRACT_BACKED" if records else "BLOCKED_NO_INDEXABLE_ENTITIES",
        "records": records,
        "sections": sorted({row["section"] for row in records}),
        "queryFields": sorted(QUERY_FIELDS),
        "queryOperators": sorted(QUERY_OPERATORS),
        "duplicateKeys": sorted(set(duplicates)),
        "invalidRows": invalid,
        "provenanceEdges": edges,
        "recordCount": len(records),
        "certifiable": False,
        "productionCertified": False,
    }


def _field(row: Mapping[str, Any], name: str) -> Any:
    if name.startswith("scope."):
        scope = row.get("scope")
        return scope.get(name.split(".", 1)[1]) if isinstance(scope, Mapping) else None
    return row.get(name)


def _matches(row: Mapping[str, Any], condition: Mapping[str, Any]) -> bool:
    field, op, expected = str(condition.get("field") or ""), str(condition.get("op") or ""), condition.get("value")
    if field not in QUERY_FIELDS or op not in QUERY_OPERATORS:
        raise ValueError(f"unsupported_filter:{field}:{op}")
    actual = _field(row, field)
    if op == "eq": return actual == expected
    if op == "ne": return actual != expected
    if op == "prefix": return str(actual or "").startswith(str(expected or ""))
    if not isinstance(expected, list): raise ValueError(f"in_requires_list:{field}")
    return actual in expected


def query_atlas(index: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    section, filters = str(request.get("section") or ""), request.get("filters", [])
    try: limit = int(request.get("limit", 100))
    except (TypeError, ValueError): limit = 0
    if section not in set(index.get("sections") or []): return _query_block("BLOCKED_INVALID_QUERY_SECTION", f"unknown_section:{section or 'missing'}")
    if not isinstance(filters, list): return _query_block("BLOCKED_INVALID_QUERY_FILTERS", "filters_must_be_list")
    if limit <= 0 or limit > 500: return _query_block("BLOCKED_INVALID_QUERY_LIMIT", "limit_must_be_1_to_500")
    if any(not isinstance(item, Mapping) for item in filters): return _query_block("BLOCKED_INVALID_QUERY_FILTER", "filter_not_mapping")
    try:
        rows = [row for row in index.get("records", []) if row.get("section") == section and all(_matches(row, item) for item in filters)]
    except ValueError as exc:
        return _query_block("BLOCKED_INVALID_QUERY_FILTER", str(exc))
    requested = ScopeIdentity.from_mapping(request.get("scope") if isinstance(request.get("scope"), Mapping) else {})
    if any(row.get("scope") for row in rows) and not requested.as_dict(): return _query_block("BLOCKED_QUERY_SCOPE_REQUIRED", "scoped_section_requires_explicit_query_scope")
    for row in rows:
        row_scope = ScopeIdentity.from_mapping(row.get("scope") if isinstance(row.get("scope"), Mapping) else {})
        if requested.as_dict() and row_scope.as_dict():
            relation = row_scope.relation(requested)
            if relation != "MATCH": return _query_block("BLOCKED_CROSS_SCOPE_QUERY" if relation == "CONFLICT" else "BLOCKED_UNPROVEN_QUERY_SCOPE", f"scope_{relation.lower()}:{row['entityId']}")
    return {"schemaVersion": FINAL_HARDENING_VERSION, "status": "QUERY_CONTRACT_BACKED", "rows": rows[:limit], "rowCount": min(len(rows), limit), "scope": requested.as_dict(), "certifiable": False, "productionCertified": False}


def _query_block(status: str, blocker: str) -> dict[str, Any]:
    return {"schemaVersion": FINAL_HARDENING_VERSION, "status": status, "rows": [], "blockers": [blocker], "certifiable": False, "productionCertified": False}


def entity_detail(index: Mapping[str, Any], section: str, entity_id: str, scope: Mapping[str, Any] | None = None) -> dict[str, Any]:
    rows = [row for row in index.get("records", []) if row.get("section") == section and row.get("entityId") == entity_id]
    if not rows: return _detail_block("BLOCKED_ENTITY_NOT_FOUND", f"missing_entity:{section}:{entity_id}")
    if len(rows) != 1 or f"{section}:{entity_id}" in set(index.get("duplicateKeys") or []): return _detail_block("BLOCKED_DUPLICATE_ENTITY_IDENTITY", f"duplicate_entity:{section}:{entity_id}")
    row, requested = rows[0], ScopeIdentity.from_mapping(scope or {})
    row_scope = ScopeIdentity.from_mapping(row.get("scope") if isinstance(row.get("scope"), Mapping) else {})
    if row_scope.as_dict() and not requested.as_dict(): return _detail_block("BLOCKED_ENTITY_SCOPE_REQUIRED", "scoped_entity_requires_explicit_scope")
    if row_scope.as_dict() and requested.as_dict():
        relation = row_scope.relation(requested)
        if relation != "MATCH": return _detail_block("BLOCKED_CROSS_SCOPE_ENTITY" if relation == "CONFLICT" else "BLOCKED_UNPROVEN_ENTITY_SCOPE", f"entity_scope_{relation.lower()}:{section}:{entity_id}")
    node = f"{row.get('kind')}:{entity_id}"
    provenance = [edge for edge in index.get("provenanceEdges", []) if str(edge.get("from")) == node or str(edge.get("to")) == node]
    return {"schemaVersion": FINAL_HARDENING_VERSION, "status": "ENTITY_DETAIL_CONTRACT_BACKED", "entity": row, "provenance": provenance, "certifiable": False, "productionCertified": False}


def _detail_block(status: str, blocker: str) -> dict[str, Any]:
    return {"schemaVersion": FINAL_HARDENING_VERSION, "status": status, "entity": None, "blockers": [blocker], "certifiable": False, "productionCertified": False}


def build_client_setup_journey(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    clients = [row for row in payload.get("clients", []) if isinstance(row, Mapping)]
    licenses = [row for row in payload.get("licenses", []) if isinstance(row, Mapping)]
    devices = [row for row in payload.get("devices", []) if isinstance(row, Mapping)]
    if not clients: return [{"status": "BLOCKED_NO_CLIENT_ROWS", "productionCertified": False}]
    result = []
    for client in clients:
        fields, blockers = _fields(client), []
        client_id = str(client.get("entityId") or fields.get("id") or "")
        if not client_id:
            result.append({"status": "BLOCKED_CLIENT_IDENTITY_MISSING", "productionCertified": False}); continue
        client_scope = ScopeIdentity.from_mapping(fields)
        linked_licenses = [row for row in licenses if str(_fields(row).get("clientId") or _fields(row).get("client_id") or "") == client_id]
        linked_devices = [row for row in devices if str(_fields(row).get("clientId") or _fields(row).get("client_id") or "") == client_id]
        if not linked_licenses: blockers.append("license_step_missing")
        if not linked_devices: blockers.append("device_step_missing")
        for kind, rows in (("license", linked_licenses), ("device", linked_devices)):
            if any(client_scope.relation(ScopeIdentity.from_mapping(_fields(row))) == "CONFLICT" for row in rows): blockers.append(f"cross_scope_{kind}")
        result.append({"schemaVersion": FINAL_HARDENING_VERSION, "clientId": client_id, "scope": client_scope.as_dict(), "status": "BLOCKED_CLIENT_SETUP_JOURNEY" if blockers else "CLIENT_SETUP_JOURNEY_CONTRACT_BACKED", "steps": [{"step": "client", "count": 1}, {"step": "license", "count": len(linked_licenses)}, {"step": "device", "count": len(linked_devices)}], "blockers": sorted(set(blockers)), "certifiable": False, "productionCertified": False})
    return sorted(result, key=lambda row: str(row.get("clientId") or row.get("status")))


def compare_golden_path(policy: Mapping[str, Any] | None, evidence: Sequence[Mapping[str, Any]] | None) -> dict[str, Any]:
    if not isinstance(policy, Mapping): return _golden_block("BLOCKED_GOLDEN_PATH_POLICY_MISSING", "golden_path_policy_required")
    steps = policy.get("steps")
    if not isinstance(steps, list) or not steps or len(set(map(str, steps))) != len(steps) or any(not str(step).strip() for step in steps): return _golden_block("BLOCKED_INVALID_GOLDEN_PATH_POLICY", "steps_must_be_unique_non_empty_ordered_ids")
    rows = [row for row in (evidence or []) if isinstance(row, Mapping)]
    observed, blockers = [str(row.get("stepId") or "") for row in rows], []
    if observed != list(map(str, steps)): blockers.append("step_order_or_membership_mismatch")
    for row in rows:
        if str(row.get("status") or "") != "PASS": blockers.append(f"step_not_pass:{row.get('stepId')}")
        if not str(row.get("evidenceRef") or ""): blockers.append(f"step_evidence_missing:{row.get('stepId')}")
    return {"schemaVersion": FINAL_HARDENING_VERSION, "status": "BLOCKED_GOLDEN_PATH_EVIDENCE" if blockers else "GOLDEN_PATH_CONTRACT_BACKED", "expectedSteps": list(map(str, steps)), "observedSteps": observed, "blockers": sorted(set(blockers)), "certifiable": False, "productionCertified": False}


def _golden_block(status: str, blocker: str) -> dict[str, Any]:
    return {"schemaVersion": FINAL_HARDENING_VERSION, "status": status, "blockers": [blocker], "certifiable": False, "productionCertified": False}


def _max_maturity(left: str, right: str) -> str:
    try: return MATURITY_ORDER[max(MATURITY_ORDER.index(left), MATURITY_ORDER.index(right))]
    except ValueError: return left


def harden_capability_ledger(rows: list[dict[str, Any]], payload: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if len(rows) != 50 or len({str(row.get("capabilityId") or "") for row in rows}) != 50: raise ValueError("final hardening requires exactly 50 unique capabilities")
    out = []
    for raw in rows:
        row, cap = dict(raw), str(raw.get("capabilityId") or "")
        row["sourceOwner"] = str(row.get("sourceOwner") or "code_atlas.operational")
        row["requiredContracts"] = _dedupe([*GENERIC_CONTRACTS, *list(row.get("requiredContracts") or [])])
        row["requiredNegativeTests"] = _dedupe([*GENERIC_NEGATIVE_TESTS, *list(row.get("requiredNegativeTests") or [])])
        row["doesNotProve"] = _dedupe(row.get("doesNotProve")) or ["Production certification or runtime correctness beyond attached evidence."]
        row["sourceHardeningVersion"], row["sourceHardeningComplete"] = FINAL_HARDENING_VERSION, True
        row["sourceImplementationMaturity"] = str(row.get("maturity") or "HEURISTIC")
        if cap in SOURCE_OVERRIDES:
            state, maturity = SOURCE_OVERRIDES[cap]
            row["implementationState"], row["sourceImplementationMaturity"] = state, maturity
            row["maturity"] = _max_maturity(str(row.get("maturity") or "HEURISTIC"), maturity)
        row["certifiable"], row["productionCertified"] = False, False
        if cap == "multi_tenant_leakage_guard":
            isolation = payload.get("tenantIsolationEvaluation")
            row["runtimeBacked"] = bool(isinstance(isolation, Mapping) and isolation.get("runtimeBacked"))
            if not row["runtimeBacked"]: row["hardBlockers"] = _dedupe([*list(row.get("hardBlockers") or []), "runtime_isolation_evidence_required"])
        row["nextGate"] = "RUNTIME_EVIDENCE_OR_POLICY" if row.get("hardBlockers") else "VERIFY_REPRODUCIBILITY_OR_RUNTIME_BACKING"
        out.append(row)
    summary = {"schemaVersion": FINAL_HARDENING_VERSION, "status": "SOURCE_HARDENING_COMPLETE_NOT_PRODUCTION_CERTIFIED", "featureCount": 50, "sourceHardeningCompleteCount": 50, "hardBlockedCapabilityCount": sum(bool(row.get("hardBlockers")) for row in out), "maturityCounts": dict(sorted(Counter(str(row.get("maturity")) for row in out).items())), "certifiableCount": 0, "productionCertifiedCount": 0, "sourceHardeningComplete": True, "productionCertified": False, "rule": "source hardening complete != runtime evidence complete != production certification"}
    return out, summary


def _read_json(path: Path, fallback: Any) -> Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return fallback


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_ledger_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for row in rows: writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False, sort_keys=True) if isinstance(row.get(key), (dict, list)) else row.get(key, "") for key in fields})


def _render_html(index: Mapping[str, Any]) -> str:
    data = html.escape(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True))
    return f'<!doctype html><meta charset="utf-8"><title>Code Atlas Hardened Investigator</title><h1>Code Atlas Hardened Investigator</h1><p>Typed scope-aware engine source is active. This static evidence view does not certify production or tenant isolation.</p><pre>{data}</pre>'


def run_operational_atlas(repo_root: str, output_dir: str, result_root: Optional[str] = None) -> dict[str, Any]:
    manifest = dict(_run_hardened_operational_atlas(repo_root, output_dir, result_root))
    out = Path(output_dir).resolve(); payload_path = out / "operational_evidence_atlas.json"
    payload = _read_json(payload_path, {})
    if not isinstance(payload, dict): raise ValueError("operational_evidence_atlas.json must be a JSON object")
    risk = evaluate_client_risk(payload.get("clientRiskSignals"), payload.get("clientRiskPolicy"), now=manifest.get("createdAt") or manifest.get("generatedAt"))
    isolation = evaluate_tenant_isolation(payload.get("tenantScopeResolver"), payload.get("tenantIsolationEvidence"))
    index = build_investigator_index(payload); journey = build_client_setup_journey(payload); golden = compare_golden_path(payload.get("goldenPathPolicy"), payload.get("goldenPathEvidence"))
    payload.update({"clientRiskScoreContract": risk, "clientRiskScore": [risk], "tenantIsolationEvaluation": isolation, "multiTenantLeakageGuard": [isolation], "atlasQueryIndex": index, "atlasQueryConsole": [{"status": "TYPED_SCOPE_AWARE_QUERY_ENGINE_SOURCE_READY", "queryFields": index["queryFields"], "queryOperators": index["queryOperators"], "productionCertified": False}], "atlasEntityDetailContract": {"status": "IDENTITY_SCOPE_PROVENANCE_DETAIL_ENGINE_SOURCE_READY", "productionCertified": False}, "entityDetailDrawer": [{"status": "IDENTITY_SCOPE_PROVENANCE_DETAIL_ENGINE_SOURCE_READY", "productionCertified": False}], "clientSetupJourneyMap": journey, "goldenPathComparator": [golden]})
    ledger = payload.get("capabilityHardeningLedger")
    if not isinstance(ledger, list): raise ValueError("CAPABILITY_HARDENING_LEDGER is required before final hardening")
    ledger, closure = harden_capability_ledger(ledger, payload); payload["capabilityHardeningLedger"], payload["sourceHardeningClosure"] = ledger, closure
    manifest.update({"sourceHardeningVersion": FINAL_HARDENING_VERSION, "sourceHardeningStatus": closure["status"], "sourceHardeningComplete": True, "sourceHardeningFeatureCount": 50, "hardeningCertifiableCount": 0, "productionCertified": False, "sourceHardeningRule": closure["rule"]}); payload["manifest"] = manifest
    outputs = {"CLIENT_RISK_SCORE_CONTRACT.json": risk, "TENANT_ISOLATION_EVALUATION.json": isolation, "ATLAS_QUERY_INDEX.json": index, "ENTITY_DETAIL_INDEX.json": index, "CLIENT_SETUP_JOURNEY_MAP.json": journey, "GOLDEN_PATH_COMPARATOR.json": golden, "SOURCE_HARDENING_CLOSURE.json": closure, "CAPABILITY_HARDENING_LEDGER.json": ledger}
    for name, value in outputs.items(): _write_json(out / name, value)
    _write_ledger_csv(out / "CAPABILITY_HARDENING_LEDGER.csv", ledger); _write_json(payload_path, payload); _write_json(out / "ATLAS_MANIFEST_PLUS.json", manifest)
    (out / "SOURCE_HARDENING_CLOSURE.md").write_text(f"# Code Atlas Source Hardening Closure\n\nStatus: `{closure['status']}`\n\nCapabilities: `50/50`\n\nProduction certified: `false`\n\n`{closure['rule']}`\n", encoding="utf-8", newline="\n")
    (out / "HARDENED_INVESTIGATOR.html").write_text(_render_html(index), encoding="utf-8", newline="\n")
    legacy = out / "operational_evidence_atlas.html"
    if legacy.exists():
        text = legacy.read_text(encoding="utf-8", errors="replace").replace('placeholder="Atlas Query Console"', 'placeholder="Legacy payload text filter (not typed Atlas Query Console)"').replace('<h2>Entity Detail Drawer</h2>', '<h2>Legacy first-row preview (not hardened Entity Detail)</h2>')
        if "HARDENED_INVESTIGATOR.html" not in text:
            text = text.replace("<body>", '<body><p>Legacy viewer only. Use <a href="HARDENED_INVESTIGATOR.html">HARDENED_INVESTIGATOR.html</a> for the hardened evidence view.</p>', 1)
        legacy.write_text(text, encoding="utf-8", newline="\n")
    smoke_path = out / "SMOKE.json"; smoke = _read_json(smoke_path, {})
    if isinstance(smoke, dict): smoke.update({"sourceHardeningStatus": closure["status"], "sourceHardeningComplete": True, "productionCertified": False}); _write_json(smoke_path, smoke)
    return manifest


__all__ = ["build_client_setup_journey", "build_investigator_index", "compare_golden_path", "entity_detail", "harden_capability_ledger", "query_atlas", "run_operational_atlas"]
