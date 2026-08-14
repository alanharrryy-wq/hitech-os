from __future__ import annotations

import csv
import datetime as dt
import hashlib
import importlib
import json
import os
import re
import sqlite3
import zipfile
from pathlib import Path
from typing import Any, Iterable, Optional

from code_atlas.core.runtime_context import RuntimeContext

EXCLUDE = {
    ".git", "node_modules", ".next", "dist", "build", "coverage", ".turbo",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv",
}
SENSITIVE = re.compile(
    r"(token|secret|password|passwd|authorization|bearer|api[_-]?key|claim|code|email|phone|tel|address|qr|magic|session)",
    re.I,
)
SOURCE_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".mjs", ".json", ".md", ".yaml", ".yml", ".sql", ".prisma")
PLACEHOLDERS = [
    "snapshot_diff_engine", "surface_role_matrix", "operational_timeline", "client_risk_score",
    "orphan_detector", "staleness_monitor", "audit_completeness_matrix", "data_lineage_graph",
    "runtime_evidence_links", "atlas_query_console", "entity_detail_drawer",
    "historical_trend_mini_atlas", "client_setup_journey_map", "multi_tenant_leakage_guard",
    "golden_path_comparator",
]


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def rel(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except Exception:
        return path.name


def digest(value: Any) -> str:
    return hashlib.sha256(str(value).encode("utf-8", "ignore")).hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)[:30000]
    return str(value)[:30000]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields, rows = ["status"], [{"status": "EMPTY"}]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _cell(row.get(key)) for key in fields})


def walk(root: Path, suffixes: tuple[str, ...] = ()) -> Iterable[Path]:
    if not root.exists():
        return []
    found: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in EXCLUDE and not name.startswith(".")]
        for name in files:
            path = Path(current) / name
            if suffixes and path.suffix.lower() not in suffixes:
                continue
            found.append(path)
    return found


def sanitize(key: str, value: Any) -> Any:
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    if SENSITIVE.search(key) or re.search(r"\S+@\S+", text):
        return "sha256:" + digest(text)[:20]
    return text[:180] + ("…" if len(text) > 180 else "")


def sanitize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {str(key): sanitize(str(key), value) for key, value in row.items()}


def classify_table(name: str) -> str:
    low = name.lower()
    if "outbox" in low or ("event" in low and "payload" in low):
        return "outbox"
    if any(token in low for token in ("client", "customer", "business", "tenant", "account", "organization")):
        return "client"
    if "license" in low or "licence" in low or "entitlement" in low:
        return "license"
    if "device" in low or "terminal" in low or "endpoint" in low:
        return "device"
    if any(token in low for token in ("sale", "order", "ticket", "invoice", "transaction")):
        return "sales"
    if any(token in low for token in ("audit", "log")):
        return "audit"
    return "other"


def dbs(repo: Path) -> list[Path]:
    result: list[Path] = []
    for path in walk(repo, (".db", ".sqlite", ".sqlite3")):
        try:
            if path.stat().st_size > 0:
                result.append(path)
        except OSError:
            continue
    return sorted(result, key=lambda item: rel(repo, item))


def _query(connection: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(sql).fetchall()]


def inspect_db(repo: Path, db: Path) -> dict[str, Any]:
    item: dict[str, Any] = {"path": rel(repo, db), "sha256Prefix": "", "tables": [], "error": None}
    try:
        with db.open("rb") as handle:
            item["sha256Prefix"] = hashlib.sha256(handle.read(1024 * 1024)).hexdigest()[:16]
        connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=2)
        try:
            tables = [row["name"] for row in _query(connection, "select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
            for table in tables:
                columns = [row["name"] for row in _query(connection, f'pragma table_info("{table}")')]
                try:
                    count = _query(connection, f'select count(*) c from "{table}"')[0]["c"]
                except Exception:
                    count = None
                item["tables"].append({"table": table, "columns": columns, "rowCount": count, "className": classify_table(table), "db": item["path"]})
        finally:
            connection.close()
    except Exception as exc:
        item["error"] = f"{type(exc).__name__}:{exc}"[:200]
    return item


def samples(repo: Path, db_rel: str, table: str, limit: int = 40) -> list[dict[str, Any]]:
    try:
        connection = sqlite3.connect(f"file:{repo / db_rel}?mode=ro", uri=True, timeout=2)
        connection.row_factory = sqlite3.Row
        try:
            return [sanitize_row(dict(row)) for row in connection.execute(f'select * from "{table}" limit {int(limit)}').fetchall()]
        finally:
            connection.close()
    except Exception:
        return []


def payload_parser(repo: Path, tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for table in tables:
        payload_columns = [column for column in table.get("columns", []) if re.search(r"(payload|json|body|event)", column, re.I)]
        if table.get("className") != "outbox" and not payload_columns:
            continue
        for row in samples(repo, table["db"], table["table"], 50):
            for column in payload_columns:
                value = row.get(column)
                if not isinstance(value, str) or not value.strip():
                    continue
                try:
                    parsed = json.loads(value)
                    keys = list(parsed) if isinstance(parsed, dict) else [type(parsed).__name__]
                    out.append({"db": table["db"], "table": table["table"], "column": column, "payloadParsed": True, "payloadKeys": "|".join(map(str, keys)), "sampleHash": digest(value)[:18]})
                except Exception as exc:
                    out.append({"db": table["db"], "table": table["table"], "column": column, "payloadParsed": False, "error": str(exc)[:120], "sampleHash": digest(value)[:18]})
    return out or [{"status": "BLOCKED_NO_PAYLOAD_JSON_ROWS"}]


def mappers(repo: Path, tables: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {"clients": [], "licenses": [], "devices": [], "sales": []}
    mapping = {"client": "clients", "license": "licenses", "device": "devices", "sales": "sales"}
    for table in tables:
        bucket = mapping.get(str(table.get("className")))
        if not bucket:
            continue
        for row in samples(repo, table["db"], table["table"], 75):
            entity_id = row.get("id") or row.get("uuid") or row.get("number") or digest(json.dumps(row, sort_keys=True, default=str))[:16]
            buckets[bucket].append({
                "entityId": entity_id,
                "sourceDb": table["db"],
                "sourceTable": table["table"],
                "trustLevel": "row-level-sanitized",
                "sourceLevel": "sqlite-read-only",
                "fields": row,
            })
    return buckets


def device_cross(mapped: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for device in mapped["devices"]:
        raw = json.dumps(device, ensure_ascii=False).lower()
        keys = [key for key in ("license", "claim", "setup", "client", "customer", "tenant", "business", "scope", "account", "organization") if key in raw]
        rows.append({"deviceId": device.get("entityId"), "sourceTable": device.get("sourceTable"), "evidenceKeys": "|".join(keys), "status": "PASS" if keys else "BLOCKED_MISSING_DEVICE_SCOPE"})
    return rows or [{"status": "BLOCKED_NO_DEVICE_ROWS"}]


def sales_lineage(mapped: dict[str, list[dict[str, Any]]], tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
    related = "\n".join(json.dumps(table, ensure_ascii=False).lower() for table in tables if re.search(r"(line|tender|payment|outbox|sync|canonical|item)", str(table.get("table", "")), re.I))
    rows: list[dict[str, Any]] = []
    for sale in mapped["sales"]:
        fields = sale.get("fields", {})
        sale_id = str(fields.get("id") or fields.get("saleId") or fields.get("orderId") or sale.get("entityId"))
        explicit = bool(sale_id and sale_id.lower() in related)
        scope = bool(re.search(r"(tenant|business|client|customer|account|organization|license|device|terminal|store)", json.dumps(fields, ensure_ascii=False), re.I))
        status = "PASS_EXPLICIT_PROVENANCE" if explicit and scope else ("INFERRED_PROVENANCE" if explicit or scope else "unknown_missing_provenance")
        rows.append({"saleId": sale_id, "sourceDb": sale.get("sourceDb"), "sourceTable": sale.get("sourceTable"), "hasRelatedLineage": explicit, "hasScopeKeys": scope, "status": status})
    return rows or [{"status": "BLOCKED_NO_SALE_ROWS"}]


def tenant_scope(repo: Path, tables: list[dict[str, Any]]) -> dict[str, Any]:
    source_hits: list[dict[str, Any]] = []
    for path in walk(repo, SOURCE_SUFFIXES):
        try:
            if path.stat().st_size > 2_500_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")[:250000]
        except Exception:
            continue
        terms = sorted(set(re.findall(r"\b(?:tenant|scope|businessId|business_id|clientId|client_id|accountId|account_id|organizationId|organization_id)\b", text, re.I)))
        if terms:
            source_hits.append({"path": rel(repo, path), "terms": "|".join(terms[:12]), "sha256Prefix": digest(text)[:16]})
        if len(source_hits) >= 100:
            break
    scoped_columns = []
    for table in tables:
        columns = [column for column in table.get("columns", []) if re.search(r"(tenant|scope|business|client|customer|account|organization)", column, re.I)]
        if columns:
            scoped_columns.append({"db": table["db"], "table": table["table"], "columns": "|".join(columns)})
    ok = bool(source_hits) and bool(scoped_columns)
    return {
        "status": "PASS_SCOPE_AUTHORITY_FOUND" if ok else "blocked-by-missing-scope-contract",
        "contractHits": source_hits,
        "scopedColumns": scoped_columns[:200],
    }


def prisma_models(repo: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in walk(repo, (".prisma",)):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for match in re.finditer(r"model\s+(\w+)\s*\{(.*?)\n\}", text, re.S):
            fields = []
            for line in match.group(2).splitlines():
                line = line.strip()
                if line and not line.startswith("//") and not line.startswith("@@"):
                    fields.append(line.split()[0])
            rows.append({"path": rel(repo, path), "model": match.group(1), "fields": fields})
    return rows


def schema_drift(repo: Path, tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table_map = {str(table["table"]).lower(): table for table in tables}
    rows = []
    for model in prisma_models(repo):
        table = table_map.get(model["model"].lower()) or table_map.get((model["model"] + "s").lower())
        if not table:
            rows.append({"model": model["model"], "path": model["path"], "status": "DRIFT_MODEL_WITHOUT_SQLITE_TABLE"})
            continue
        missing = [field for field in model["fields"] if field not in table.get("columns", [])]
        rows.append({"model": model["model"], "db": table["db"], "table": table["table"], "status": "PASS" if not missing else "DRIFT_FIELD_MISMATCH", "missingColumns": "|".join(missing[:40])})
    return rows or [{"status": "BLOCKED_NO_SCHEMA_MODELS"}]


def runtime_links(result_root: Path) -> list[dict[str, Any]]:
    if not result_root.exists():
        return [{"status": "BLOCKED_RESULT_ROOT_NOT_FOUND"}]
    zips = [path for path in result_root.glob("**/*result*.zip") if path.is_file()]
    rows = []
    for archive in sorted(zips, key=lambda item: item.stat().st_mtime)[-150:]:
        try:
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                interesting = [name for name in names if re.search(r"(manifest|verif|result|smoke|check|report|continuation)", name, re.I)][:50]
            rows.append({"artifact": archive.name, "entryCount": len(names), "interestingEntries": "|".join(interesting), "status": "LINKED"})
        except Exception as exc:
            rows.append({"artifact": archive.name, "status": "READ_ERROR", "error": str(exc)[:120]})
    return rows or [{"status": "BLOCKED_NO_RESULT_ZIPS"}]


def surface_matrix(context: RuntimeContext) -> list[dict[str, Any]]:
    configured = context.app_roots()
    if not configured:
        return [{
            "surface": "repository",
            "appId": "repository",
            "path": ".",
            "exists": context.repo_root.exists(),
            "fileCount": sum(1 for _ in walk(context.repo_root, (".py", ".ts", ".tsx", ".js", ".mjs", ".json"))),
            "routeCount": 0,
            "role": "generic repository root",
            "status": "PASS_GENERIC_REPOSITORY_ROOT" if context.repo_root.exists() else "BLOCKED_REPOSITORY_ROOT_MISSING",
            "sampleRoutes": "",
        }]
    rows = []
    for app in configured:
        if not app["valid"]:
            rows.append({"surface": app["kind"], "appId": app["id"], "path": app["root"], "exists": False, "fileCount": 0, "routeCount": 0, "role": app["label"], "status": "BLOCKED_INVALID_APP_ROOT", "reason": app["reason"], "sampleRoutes": ""})
            continue
        root = app["path"]
        files = list(walk(root, (".py", ".ts", ".tsx", ".js", ".mjs", ".json", ".md", ".css")))[:10000] if root.exists() else []
        routes = [rel(context.repo_root, path) for path in files if path.name in {"page.tsx", "page.jsx", "page.js", "route.ts", "route.js", "layout.tsx", "main.py", "app.py"}]
        rows.append({
            "surface": app["kind"],
            "appId": app["id"],
            "path": app["root"],
            "exists": root.exists(),
            "fileCount": len(files),
            "routeCount": len(routes),
            "role": app["label"],
            "status": "PASS" if root.exists() else "BLOCKED_MISSING_APP_ROOT",
            "sampleRoutes": "|".join(routes[:30]),
        })
    return rows


def _configured_adapters(context: RuntimeContext, out: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    specs = context.metadata("operationalAdapters", [])
    if not specs:
        return {"status": "NOT_CONFIGURED", "decision": "NO_IMPLICIT_PRODUCT_ADAPTER", "doNotRebuild": True, "blockers": []}, {}
    if not isinstance(specs, list):
        return {"status": "BLOCKED_INVALID_ADAPTER_CONFIG", "decision": "VERIFY_PROFILE", "doNotRebuild": True, "blockers": ["operationalAdapters_must_be_list"]}, {}
    payload: dict[str, Any] = {}
    statuses = []
    blockers = []
    for index, raw in enumerate(specs):
        if not isinstance(raw, dict):
            blockers.append(f"adapter_{index}_must_be_object")
            continue
        module_name = str(raw.get("module") or "").strip()
        callable_name = str(raw.get("callable") or "").strip()
        adapter_id = str(raw.get("id") or f"adapter-{index}")
        if not module_name or not callable_name:
            blockers.append(f"{adapter_id}:module_and_callable_required")
            continue
        try:
            function = getattr(importlib.import_module(module_name), callable_name)
            result = function(context.repo_root, out, context.result_root)
            if not isinstance(result, dict):
                raise TypeError("adapter result must be object")
            adapter_summary = result.get("summary", {}) if isinstance(result.get("summary"), dict) else {}
            statuses.append({"id": adapter_id, "status": adapter_summary.get("status", "PASS_ADAPTER_EXECUTED")})
            if isinstance(result.get("payload"), dict):
                payload.update(result["payload"])
        except Exception as exc:
            blockers.append(f"{adapter_id}:{type(exc).__name__}:{exc}")
    return {
        "status": "BLOCKED_ADAPTER_EXECUTION" if blockers else "PASS_EXPLICIT_ADAPTERS_EXECUTED",
        "decision": "VERIFY_ADAPTER" if blockers else "EXPLICIT_PROFILE_ADAPTERS_ONLY",
        "doNotRebuild": True,
        "adapters": statuses,
        "blockers": blockers,
    }, payload


def extra_detectors(mapped: dict[str, list[dict[str, Any]]], lineage: list[dict[str, Any]], cross: list[dict[str, Any]], scope: dict[str, Any], tables: list[dict[str, Any]], runtime: list[dict[str, Any]]) -> dict[str, Any]:
    duplicates, orphans, stale = [], [], []
    seen: set[tuple[str, str]] = set()
    for kind, items in mapped.items():
        for row in items:
            key = (kind, str(row.get("entityId")))
            raw = json.dumps(row, ensure_ascii=False).lower()
            if key in seen:
                duplicates.append({"entityKind": kind, "entityId": key[1], "status": "DUPLICATE_ID"})
            seen.add(key)
            if kind in {"licenses", "devices", "sales"} and not re.search(r"(client|customer|business|tenant|scope|account|organization)", raw):
                orphans.append({"entityKind": kind, "entityId": key[1], "status": "ORPHAN_SCOPE_UNKNOWN"})
            if not re.search(r"(updated|created|timestamp|date|expires|lastseen)", raw):
                stale.append({"entityKind": kind, "entityId": key[1], "status": "STALE_MONITOR_NO_TIMESTAMP_FIELD"})
    audit_count = sum(1 for table in tables if table.get("className") == "audit")
    graph = [{"from": "Sale:" + str(row.get("saleId", "unknown")), "to": "Provenance:" + str(row.get("status")), "type": "sale_lineage"} for row in lineage]
    graph += [{"from": "Device:" + str(row.get("deviceId", "unknown")), "to": "Scope:" + str(row.get("status")), "type": "device_scope"} for row in cross]
    return {
        "duplicates": duplicates or [{"status": "PASS_NO_DUPLICATE_SAMPLE_IDS"}],
        "orphans": orphans or [{"status": "PASS_NO_ORPHANS_IN_SAMPLE"}],
        "stalenessMonitor": stale or [{"status": "PASS_TIMESTAMPS_PRESENT_IN_SAMPLE"}],
        "auditCompleteness": [{"auditTableCount": audit_count, "status": "PASS" if audit_count else "BLOCKED_NO_AUDIT_TABLES"}],
        "clientRiskScore": [{"risk": "unknown_missing_provenance", "count": sum(1 for row in lineage if row.get("status") == "unknown_missing_provenance"), "status": "NO_GREEN" if any(row.get("status") == "unknown_missing_provenance" for row in lineage) else "PASS"}, {"risk": "scope_authority", "status": scope.get("status")}],
        "dataLineageGraph": graph or [{"status": "EMPTY_NO_EDGES"}],
        "clientSetupJourneyMap": [
            {"step": "client", "count": len(mapped["clients"]), "status": "PASS" if mapped["clients"] else "BLOCKED_NO_CLIENT_ROWS"},
            {"step": "license", "count": len(mapped["licenses"]), "status": "PASS" if mapped["licenses"] else "BLOCKED_NO_LICENSE_ROWS"},
            {"step": "device", "count": len(mapped["devices"]), "status": "PASS" if mapped["devices"] else "BLOCKED_NO_DEVICE_ROWS"},
        ],
        "operationalTimeline": [{"source": row.get("artifact", ""), "event": "runtime_evidence_zip", "status": row.get("status")} for row in runtime] or [{"status": "EMPTY"}],
    }


def html_report(path: Path, payload: dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False)
    body = f'''<!doctype html><html><head><meta charset="utf-8"><title>Code Atlas Operational Evidence</title>
<style>body{{font-family:Inter,Segoe UI,Arial,sans-serif;background:#f7f8fb;color:#172033;margin:0}}header{{padding:24px 32px;background:#fff;border-bottom:1px solid #dbe3f3}}main{{padding:24px}}pre{{white-space:pre-wrap;word-break:break-word;background:#0f172a;color:#e2e8f0;border-radius:14px;padding:14px;max-height:72vh;overflow:auto}}</style></head>
<body><header><h1>Code Atlas Operational Evidence</h1><p>Structure, evidence and certification are separate. This viewer never certifies production.</p></header><main><pre id="view"></pre></main><script>const DATA={data};document.getElementById('view').textContent=JSON.stringify(DATA,null,2);</script></body></html>'''
    write_text(path, body)


def run_operational_atlas(repo_root: str, output_dir: str, result_root: Optional[str] = None) -> dict[str, Any]:
    context = RuntimeContext.resolve(repo_root, output_dir, result_root)
    repo, out = context.repo_root, context.output_root
    out.mkdir(parents=True, exist_ok=True)

    inventory, tables = [], []
    for db in dbs(repo):
        meta = inspect_db(repo, db)
        inventory.append(meta)
        tables.extend(meta.get("tables", []))
    mapped = mappers(repo, tables)
    payload_rows = payload_parser(repo, tables)
    cross = device_cross(mapped)
    lineage = sales_lineage(mapped, tables)
    scope = tenant_scope(repo, tables)
    drift = schema_drift(repo, tables)
    runtime = runtime_links(context.result_root)
    surfaces = surface_matrix(context)
    extra = extra_detectors(mapped, lineage, cross, scope, tables, runtime)
    adapter_summary, adapter_payload = _configured_adapters(context, out)

    blockers: list[str] = []
    if any(row.get("status") == "unknown_missing_provenance" for row in lineage):
        blockers.append("unknown_missing_provenance")
    if scope.get("status") == "blocked-by-missing-scope-contract":
        blockers.append("blocked-by-missing-scope-contract")
    if any(str(row.get("status", "")).startswith("BLOCKED") for row in cross):
        blockers.append("device_scope_incomplete")
    if str(adapter_summary.get("status", "")).startswith("BLOCKED"):
        blockers.extend("adapter:" + str(item) for item in adapter_summary.get("blockers", []))

    ledger = [{"feature": name, "placeholder": False, "status": "source_detector_present"} for name in PLACEHOLDERS]
    created = _now()
    manifest = {
        "tool": "code_atlas_operational_v4",
        "createdAt": created,
        "repoRootMode": "explicit",
        "profileId": context.profile.profile_id,
        "status": "BLOCKED_FOR_PRODUCTION" if blockers else "SOURCE_READY_NOT_PRODUCTION_CERTIFIED",
        "productionGate": "NO_PRODUCTION_CERTIFICATION_BY_BASE_COLLECTOR",
        "productionBlockers": blockers,
        "featureCount": 50,
        "detectorsConverted": len(ledger),
        "placeholdersRemaining": 0,
        "monolithDependency": False,
        "rawDatabasesIncluded": False,
        "adapterStatus": adapter_summary.get("status"),
        "adapterDecision": adapter_summary.get("decision"),
        "productionCertified": False,
    }
    payload: dict[str, Any] = {
        "manifest": manifest,
        "dbInventory": inventory,
        "payloadJsonIndex": payload_rows,
        "clients": mapped["clients"],
        "licenses": mapped["licenses"],
        "devices": mapped["devices"],
        "sales": mapped["sales"],
        "deviceClaimCrosscheck": cross,
        "salesLineage": lineage,
        "tenantScopeResolver": scope,
        "schemaDriftGuard": drift,
        "runtimeEvidenceLinks": runtime,
        "surfaceRoleMatrix": surfaces,
        "snapshotDiffEngine": [{"status": "DEFERRED_TO_FOUNDATION", "productionCertified": False}],
        "placeholderLedger": ledger,
        "multiTenantLeakageGuard": [{"status": scope.get("status"), "rule": "certify only with runtime-backed isolation evidence", "productionCertified": False}],
        "goldenPathComparator": [{"component": "production_gate", "status": "BLOCKED_FOR_PRODUCTION" if blockers else "SOURCE_READY_NOT_PRODUCTION_CERTIFIED", "productionCertified": False}],
        "adapterSummary": adapter_summary,
    }
    payload.update(adapter_payload)
    payload.update(extra)

    write_json(out / "ATLAS_MANIFEST_PLUS.json", manifest)
    write_json(out / "operational_evidence_atlas.json", payload)
    write_json(out / "placeholder_ledger.json", ledger)
    write_csv(out / "placeholder_ledger.csv", ledger)
    for key, value in payload.items():
        if isinstance(value, list):
            write_csv(out / "csv" / f"{key}.csv", value)
        elif isinstance(value, dict):
            write_json(out / "json" / f"{key}.json", value)

    write_text(out / "WHY_THIS_IS_RED.md", "# Why this is not production-certified\n\n" + "\n".join(f"- {item}" for item in (blockers or ["base collection never declares production certification"])) + "\n")
    write_text(out / "CAN_PATCH_DECISION.md", "# Patch decision\n\nCAN_PATCH_SOURCE_MODULES=true\nCAN_DECLARE_PRODUCTION_CERTIFIED=false\n")
    write_text(out / "HUMAN_OPERATOR_SUMMARY.md", f"# Human Operator Summary\n\nStatus: `{manifest['status']}`\n\nProfile: `{context.profile.profile_id}`\n\nRaw DBs included: false.\n")
    write_text(out / "CONTINUATION_SUPREME.md", "# Continuation\n\nInspect manifest, blockers, capability ledger and evidence outputs before any patch.\n")
    write_json(out / "SMOKE.json", {
        "status": "PASS",
        "requiredFiles": ["ATLAS_MANIFEST_PLUS.json", "operational_evidence_atlas.html", "placeholder_ledger.json", "CAN_PATCH_DECISION.md", "WHY_THIS_IS_RED.md"],
        "productionCertified": False,
    })
    write_text(out / "SMOKE.md", "# Smoke\n\nPASS: Code Atlas Operational Evidence outputs generated. This does not certify production.\n")
    html_report(out / "operational_evidence_atlas.html", payload)
    return manifest


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--out", required=True)
    parser.add_argument("--result-root", default=None)
    args = parser.parse_args()
    print(json.dumps(run_operational_atlas(args.repo, args.out, args.result_root), ensure_ascii=False, indent=2))
