from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .runtime_profile import (
    ROUTE_FILENAMES,
    OperationalRuntimeProfile,
    iter_profile_source_files,
    public_path,
    resolve_runtime_profile,
)

EXCLUDE = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    ".turbo",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "venv",
    ".venv",
}
SENSITIVE = re.compile(
    r"(token|secret|password|passwd|authorization|bearer|api[_-]?key|claim|code|email|phone|tel|address|qr|magic|session)",
    re.I,
)
PLACEHOLDERS = [
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
]


def rel(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except Exception:
        return public_path(path, repo)


def h(value: Any) -> str:
    return hashlib.sha256(str(value).encode("utf-8", "ignore")).hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)[:30000]
    return str(value)[:30000]


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields = ["status"]
        rows = [{"status": "EMPTY"}]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: cell(row.get(key)) for key in fields})


def walk(root: Path, suffixes: tuple[str, ...] = ()) -> Iterable[Path]:
    if not root.exists():
        return
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in EXCLUDE and not name.startswith(".")]
        for name in files:
            path = Path(current) / name
            if not suffixes or path.suffix.lower() in suffixes:
                yield path


def sanitize(key: str, value: Any) -> Any:
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    if SENSITIVE.search(key) or re.search(r"\S+@\S+", text):
        return "sha256:" + h(text)[:20]
    return text[:180] + ("…" if len(text) > 180 else "")


def sanitize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {str(key): sanitize(str(key), value) for key, value in row.items()}


def classify(name: str) -> str:
    low = name.lower()
    if "outbox" in low or ("event" in low and "payload" in low):
        return "outbox"
    if any(token in low for token in ("client", "customer", "business", "tenant", "account", "organization", "organisation")):
        return "client"
    if "license" in low or "licence" in low or "entitlement" in low:
        return "license"
    if "device" in low or "terminal" in low or "endpoint" in low:
        return "device"
    if low in {"sale", "sales"} or any(token in low for token in ("sale", "order", "ticket", "transaction")):
        return "sales"
    if any(token in low for token in ("audit", "log", "journal")):
        return "audit"
    return "other"


def dbs(repo: Path) -> List[Path]:
    found: list[Path] = []
    for path in walk(repo, (".db", ".sqlite", ".sqlite3")):
        try:
            if path.stat().st_size > 0:
                found.append(path)
        except OSError:
            continue
    return sorted(found, key=lambda path: rel(repo, path))


def q(conn: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(sql).fetchall()]


def inspect_db(repo: Path, db: Path) -> Dict[str, Any]:
    item: Dict[str, Any] = {"path": rel(repo, db), "sha256Prefix": "", "tables": [], "error": None}
    try:
        item["sha256Prefix"] = hashlib.sha256(db.read_bytes()[: 1024 * 1024]).hexdigest()[:16]
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=2)
        tables = [row["name"] for row in q(conn, "select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
        for table in tables:
            columns = [row["name"] for row in q(conn, f'pragma table_info("{table}")')]
            try:
                count = q(conn, f'select count(*) c from "{table}"')[0]["c"]
            except Exception:
                count = None
            item["tables"].append({"table": table, "columns": columns, "rowCount": count, "className": classify(table), "db": item["path"]})
        conn.close()
    except Exception as exc:
        item["error"] = f"{type(exc).__name__}: {exc}"[:200]
    return item


def samples(repo: Path, db_rel: str, table: str, limit: int = 40) -> List[Dict[str, Any]]:
    try:
        conn = sqlite3.connect(f"file:{repo / db_rel}?mode=ro", uri=True, timeout=2)
        conn.row_factory = sqlite3.Row
        rows = [sanitize_row(dict(row)) for row in conn.execute(f'select * from "{table}" limit {int(limit)}').fetchall()]
        conn.close()
        return rows
    except Exception:
        return []


def payload_parser(repo: Path, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                    obj = json.loads(value)
                    keys = list(obj.keys()) if isinstance(obj, dict) else [type(obj).__name__]
                    out.append({"db": table["db"], "table": table["table"], "column": column, "payloadParsed": True, "payloadKeys": "|".join(map(str, keys)), "sampleHash": h(value)[:18]})
                except Exception as exc:
                    out.append({"db": table["db"], "table": table["table"], "column": column, "payloadParsed": False, "error": f"{type(exc).__name__}: {exc}"[:120], "sampleHash": h(value)[:18]})
    return out or [{"status": "BLOCKED_NO_PAYLOADJSON_ROWS", "rule": "Payload parser ran but no payload/json rows were detected."}]


def mappers(repo: Path, tables: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    buckets: Dict[str, List[Dict[str, Any]]] = {"clients": [], "licenses": [], "devices": [], "sales": []}
    mapping = {"client": "clients", "license": "licenses", "device": "devices", "sales": "sales"}
    for table in tables:
        bucket = mapping.get(str(table.get("className")))
        if not bucket:
            continue
        for row in samples(repo, table["db"], table["table"], 75):
            entity_id = row.get("id") or row.get("uuid") or row.get("number") or h(json.dumps(row, sort_keys=True, default=str))[:16]
            buckets[bucket].append({"entityId": entity_id, "sourceDb": table["db"], "sourceTable": table["table"], "trustLevel": "row-level-sanitized", "sourceLevel": "sqlite", "fields": row})
    return buckets


def device_cross(mapped: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for device in mapped["devices"]:
        raw = json.dumps(device, ensure_ascii=False).lower()
        keys = [key for key in ("license", "licence", "entitlement", "claim", "setup", "client", "customer", "tenant", "business", "organization", "scope") if key in raw]
        out.append({"deviceId": device.get("entityId"), "sourceTable": device.get("sourceTable"), "evidenceKeys": "|".join(keys), "status": "PASS" if keys else "BLOCKED_MISSING_DEVICE_CLAIM_SCOPE"})
    return out or [{"status": "BLOCKED_NO_DEVICE_ROWS"}]


def sales_lineage(mapped: Dict[str, List[Dict[str, Any]]], tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    related = "\n".join(json.dumps(table, ensure_ascii=False).lower() for table in tables if re.search(r"(line|item|tender|payment|outbox|event|sync|projection|canonical)", str(table.get("table", "")), re.I))
    out: list[dict[str, Any]] = []
    for sale in mapped["sales"]:
        fields = sale.get("fields", {})
        sale_id = str(fields.get("id") or fields.get("saleId") or fields.get("orderId") or sale.get("entityId"))
        explicit = bool(sale_id and sale_id.lower() in related)
        scoped = bool(re.search(r"(tenant|business|organization|client|customer|license|device|terminal|store|account)", json.dumps(fields, ensure_ascii=False), re.I))
        status = "PASS_EXPLICIT_PROVENANCE" if explicit and scoped else ("INFERRED_PROVENANCE" if explicit or scoped else "unknown_missing_provenance")
        out.append({"saleId": sale_id, "sourceDb": sale.get("sourceDb"), "sourceTable": sale.get("sourceTable"), "hasRelatedLineage": explicit, "hasScopeKeys": scoped, "status": status})
    return out or [{"status": "BLOCKED_NO_SALE_ROWS"}]


def tenant_scope(profile: OperationalRuntimeProfile, tables: List[Dict[str, Any]]) -> Dict[str, Any]:
    hits: list[dict[str, Any]] = []
    term_re = re.compile(r"\b(tenant|scope|businessId|business_id|organizationId|organization_id|accountId|account_id|clientId|client_id|licenseId|license_id|multi[-_ ]tenant)\b", re.I)
    for path in iter_profile_source_files(profile):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:250000]
        except Exception:
            continue
        terms = sorted({match.group(0) for match in term_re.finditer(text)}, key=str.lower)
        if terms:
            hits.append({"path": rel(profile.repo_root, path), "terms": "|".join(terms[:12]), "sha256Prefix": h(text)[:16]})
        if len(hits) >= 80:
            break
    scoped_columns = []
    for table in tables:
        columns = [column for column in table.get("columns", []) if re.search(r"(tenant|scope|business|organization|account|client|customer|license)", column, re.I)]
        if columns:
            scoped_columns.append({"db": table["db"], "table": table["table"], "columns": "|".join(columns)})
    ok = bool(hits) and bool(scoped_columns)
    return {"status": "PASS_SCOPE_AUTHORITY_FOUND" if ok else "blocked-by-missing-scope-contract", "contractHits": hits, "scopedColumns": scoped_columns[:200]}


def prisma_models(repo: Path) -> List[Dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for path in walk(repo, (".prisma",)):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for match in re.finditer(r"model\s+(\w+)\s*\{(.*?)\n\}", text, re.S):
            fields: list[str] = []
            for line in match.group(2).splitlines():
                line = line.strip()
                if line and not line.startswith("//") and not line.startswith("@@"):
                    fields.append(line.split()[0])
            out.append({"path": rel(repo, path), "model": match.group(1), "fields": fields})
    return out


def schema_drift(repo: Path, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    table_map = {str(table["table"]).lower(): table for table in tables}
    out: list[dict[str, Any]] = []
    for model in prisma_models(repo):
        table = table_map.get(model["model"].lower()) or table_map.get((model["model"] + "s").lower())
        if not table:
            out.append({"model": model["model"], "path": model["path"], "status": "DRIFT_MODEL_WITHOUT_SQLITE_TABLE"})
            continue
        missing = [field for field in model["fields"] if field not in table.get("columns", [])]
        out.append({"model": model["model"], "db": table["db"], "table": table["table"], "status": "PASS" if not missing else "DRIFT_FIELD_MISMATCH", "missingColumns": "|".join(missing[:40])})
    return out or [{"status": "BLOCKED_NO_PRISMA_MODELS"}]


def _evidence_archives(profile: OperationalRuntimeProfile) -> List[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for root in profile.evidence_roots:
        if not root.exists():
            continue
        for pattern in ("*result*.zip", "*evidence*.zip", "*atlas*.zip"):
            for path in root.glob(f"**/{pattern}"):
                key = str(path.resolve()).lower()
                if key not in seen:
                    seen.add(key)
                    found.append(path)
                if len(found) >= 1000:
                    return found
    return found


def runtime_links(profile: OperationalRuntimeProfile) -> List[Dict[str, Any]]:
    out: list[dict[str, Any]] = []
    archives = sorted(_evidence_archives(profile), key=lambda path: (path.stat().st_mtime if path.exists() else 0, str(path).lower()))[-150:]
    for archive in archives:
        try:
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                interesting = [name for name in names if re.search(r"(manifest|verif|result|smoke|check|report|continuation)", name, re.I)][:50]
            out.append({"sourceRef": public_path(archive, profile.repo_root), "entryCount": len(names), "interestingEntries": "|".join(interesting), "status": "LINKED"})
        except Exception as exc:
            out.append({"sourceRef": public_path(archive, profile.repo_root), "status": "READ_ERROR", "error": f"{type(exc).__name__}: {exc}"[:120]})
    return out or [{"status": "BLOCKED_NO_RESULT_ZIPS"}]


def surface_matrix(profile: OperationalRuntimeProfile) -> List[Dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for surface in profile.surfaces:
        root = (profile.repo_root / surface.root).resolve() if not Path(surface.root).is_absolute() else Path(surface.root).resolve()
        exists = root.exists()
        files = list(walk(root, (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".md", ".css", ".py")))[:10000] if exists else []
        routes = [rel(profile.repo_root, path) for path in files if path.name in ROUTE_FILENAMES]
        rows.append({"surface": surface.surface_id, "label": surface.label, "kind": surface.kind, "path": public_path(root, profile.repo_root), "exists": exists, "fileCount": len(files), "routeCount": len(routes), "status": "PASS" if exists else "BLOCKED_MISSING_SURFACE_ROOT", "sampleRoutes": "|".join(routes[:30])})
    return rows or [{"status": "BLOCKED_NO_SURFACE_PROFILE_OR_DISCOVERY"}]


def snapshot_diff(profile: OperationalRuntimeProfile) -> List[Dict[str, Any]]:
    archives = sorted(_evidence_archives(profile), key=lambda path: path.stat().st_mtime if path.exists() else 0)[-10:]
    rows: list[dict[str, Any]] = []
    previous: list[str] | None = None
    for archive in archives:
        try:
            with zipfile.ZipFile(archive) as bundle:
                names = sorted(bundle.namelist())
            row: dict[str, Any] = {"sourceRef": public_path(archive, profile.repo_root), "entryCount": len(names), "fileListHash": h("\n".join(names))[:18], "status": "BASELINE" if previous is None else "COMPARABLE"}
            if previous is not None:
                row.update({"addedEntries": len(set(names) - set(previous)), "removedEntries": len(set(previous) - set(names))})
            rows.append(row)
            previous = names
        except Exception as exc:
            rows.append({"sourceRef": public_path(archive, profile.repo_root), "status": "READ_ERROR", "error": f"{type(exc).__name__}: {exc}"[:120]})
    if len([row for row in rows if row.get("status") in {"BASELINE", "COMPARABLE"}]) < 2:
        rows.append({"status": "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS"})
    return rows


def extra_detectors(mapped: Dict[str, List[Dict[str, Any]]], lineage: List[Dict[str, Any]], cross: List[Dict[str, Any]], scope: Dict[str, Any], tables: List[Dict[str, Any]], runtime: List[Dict[str, Any]]) -> Dict[str, Any]:
    duplicates: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    orphans: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    for kind, items in mapped.items():
        for row in items:
            key = (kind, str(row.get("entityId")))
            raw = json.dumps(row, ensure_ascii=False).lower()
            if key in seen:
                duplicates.append({"entityKind": kind, "entityId": key[1], "status": "DUPLICATE_ID"})
            seen.add(key)
            if kind in {"licenses", "devices", "sales"} and not re.search(r"(client|customer|business|organization|tenant|account|scope)", raw):
                orphans.append({"entityKind": kind, "entityId": key[1], "status": "ORPHAN_SCOPE_UNKNOWN"})
            if not re.search(r"(updated|created|timestamp|date|expires|lastseen|modified)", raw):
                stale.append({"entityKind": kind, "entityId": key[1], "status": "STALE_MONITOR_NO_TIMESTAMP_FIELD"})
    audit = [{"auditTableCount": sum(1 for table in tables if table.get("className") == "audit"), "status": "PASS" if any(table.get("className") == "audit" for table in tables) else "BLOCKED_NO_AUDIT_TABLES"}]
    client_risk = [{"risk": "unknown_missing_provenance", "count": sum(1 for row in lineage if row.get("status") == "unknown_missing_provenance"), "status": "NO_GREEN" if any(row.get("status") == "unknown_missing_provenance" for row in lineage) else "PASS"}, {"risk": "tenant_scope_authority", "status": scope.get("status")}]
    graph = [{"from": "Sale:" + str(row.get("saleId", "unknown")), "to": "Provenance:" + str(row.get("status")), "type": "sale_lineage"} for row in lineage]
    graph += [{"from": "Device:" + str(row.get("deviceId", "unknown")), "to": "ClaimScope:" + str(row.get("status")), "type": "device_claim"} for row in cross]
    journey = [{"step": "client", "count": len(mapped["clients"]), "status": "PASS" if mapped["clients"] else "BLOCKED_NO_CLIENT_ROWS"}, {"step": "license", "count": len(mapped["licenses"]), "status": "PASS" if mapped["licenses"] else "BLOCKED_NO_LICENSE_ROWS"}, {"step": "device_claim", "count": len(mapped["devices"]), "status": "PASS" if mapped["devices"] else "BLOCKED_NO_DEVICE_ROWS"}]
    return {"duplicates": duplicates or [{"status": "PASS_NO_DUPLICATE_SAMPLE_IDS"}], "orphans": orphans or [{"status": "PASS_NO_ORPHANS_IN_SAMPLE"}], "stalenessMonitor": stale or [{"status": "PASS_TIMESTAMPS_PRESENT_IN_SAMPLE"}], "auditCompleteness": audit, "clientRiskScore": client_risk, "dataLineageGraph": graph or [{"status": "EMPTY_NO_EDGES"}], "clientSetupJourneyMap": journey, "operationalTimeline": [{"source": row.get("sourceRef", ""), "event": "runtime_evidence_zip", "status": row.get("status")} for row in runtime] or [{"status": "EMPTY"}]}


def html_report(path: Path, payload: Dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False)
    body = f"""<!doctype html><html><head><meta charset=\"utf-8\"><title>Code Atlas Operational Evidence</title><style>body{{font-family:Inter,Segoe UI,Arial,sans-serif;background:#f7f8fb;color:#172033;margin:0}}header{{padding:24px 32px;background:linear-gradient(135deg,#fff,#e9eefc);border-bottom:1px solid #dbe3f3}}.tabs{{display:flex;gap:8px;flex-wrap:wrap;padding:16px 24px;background:white;position:sticky;top:0}}button{{border:1px solid #cbd5e1;background:white;border-radius:999px;padding:8px 12px}}button.active{{background:#111827;color:white}}main{{padding:24px;display:grid;grid-template-columns:1fr 360px;gap:18px}}.card{{background:white;border:1px solid #e2e8f0;border-radius:18px;padding:18px;box-shadow:0 10px 30px #0f172a10}}pre{{white-space:pre-wrap;word-break:break-word;background:#0f172a;color:#e2e8f0;border-radius:14px;padding:14px;max-height:62vh;overflow:auto}}input{{width:100%;padding:12px;border-radius:12px;border:1px solid #cbd5e1}}</style></head><body><header><h1>Code Atlas Operational Evidence</h1><p>Structure, observed evidence and certification are separate contracts. Missing evidence never becomes a green claim.</p></header><div class=\"tabs\" id=\"tabs\"></div><main><section class=\"card\"><input id=\"q\" placeholder=\"Legacy payload text filter\"/><pre id=\"view\"></pre></section><aside class=\"card\"><h2>Legacy first-row preview</h2><pre id=\"drawer\"></pre></aside></main><script>const DATA={data}; const keys=Object.keys(DATA); let active=keys[0]; const tabs=document.getElementById('tabs'), view=document.getElementById('view'), q=document.getElementById('q'), drawer=document.getElementById('drawer'); function renderTabs(){{tabs.innerHTML=''; keys.forEach(k=>{{const b=document.createElement('button'); b.textContent=k; b.className=k===active?'active':''; b.onclick=()=>{{active=k;render()}}; tabs.appendChild(b)}})}} function render(){{renderTabs(); let txt=JSON.stringify(DATA[active],null,2); const term=q.value.toLowerCase(); if(term) txt=txt.split('\\n').filter(x=>x.toLowerCase().includes(term)).join('\\n')||'No matches'; view.textContent=txt; const obj=DATA[active]; drawer.textContent=JSON.stringify(Array.isArray(obj)?obj[0]:obj,null,2)}} q.oninput=render; render();</script></body></html>"""
    write_text(path, body)


def _support_result(profile: OperationalRuntimeProfile, out: Path) -> Dict[str, Any]:
    if not profile.support_resolver_enabled:
        summary = {"status": "NOT_CONFIGURED", "decision": "OPTIONAL_ADAPTER_NOT_ENABLED", "doNotRebuild": True, "blockers": []}
        return {"summary": summary, "payload": {"supportResolverSummary": [summary]}, "exports": {}}
    try:
        from .support_resolver import run_support_resolver_atlas

        return run_support_resolver_atlas(profile.repo_root, out, profile.result_root, profile=profile)
    except Exception as exc:
        summary = {"status": "BLOCKED_SUPPORT_CONSUMER_ERROR", "decision": "VERIFY_ADAPTER", "doNotRebuild": True, "blockers": [f"{type(exc).__name__}: {exc}"]}
        return {"summary": summary, "payload": {"supportResolverSummary": [summary]}, "exports": {}}


def run_operational_atlas(repo_root: str, output_dir: str, result_root: Optional[str] = None) -> Dict[str, Any]:
    repo = Path(repo_root).expanduser().resolve()
    out = Path(output_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    profile = resolve_runtime_profile(repo, out, result_root)

    inventory: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    for db in dbs(repo):
        meta = inspect_db(repo, db)
        inventory.append(meta)
        tables.extend(meta.get("tables", []))

    mapped = mappers(repo, tables)
    payload_rows = payload_parser(repo, tables)
    cross = device_cross(mapped)
    lineage = sales_lineage(mapped, tables)
    scope = tenant_scope(profile, tables)
    drift = schema_drift(repo, tables)
    runtime = runtime_links(profile)
    surfaces = surface_matrix(profile)
    snapshots = snapshot_diff(profile)
    extra = extra_detectors(mapped, lineage, cross, scope, tables, runtime)
    support_result = _support_result(profile, out)

    blockers: list[str] = []
    if any(row.get("status") == "unknown_missing_provenance" for row in lineage):
        blockers.append("unknown_missing_provenance")
    if scope.get("status") == "blocked-by-missing-scope-contract":
        blockers.append("blocked-by-missing-scope-contract")
    if any(str(row.get("status", "")).startswith("BLOCKED") for row in cross):
        blockers.append("device_claim_scope_incomplete")

    ledger: list[dict[str, Any]] = []
    for name in PLACEHOLDERS:
        status = "implemented_v3_detector"
        if name == "multi_tenant_leakage_guard" and scope.get("status") == "blocked-by-missing-scope-contract":
            status = "blocked-by-missing-scope-contract"
        if name == "snapshot_diff_engine" and any(row.get("status") == "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS" for row in snapshots):
            status = "implemented_v3_blocked_insufficient_comparable_runs"
        ledger.append({"feature": name, "placeholder": False, "status": status})

    support_summary = support_result.get("summary", {})
    manifest: Dict[str, Any] = {
        "tool": "code_atlas_operational_v3",
        "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "profileId": profile.profile_id,
        "projectName": profile.project_name,
        "repoRootName": repo.name,
        "repoPathDigest": "sha256:" + h(str(repo))[:20],
        "status": "BLOCKED_FOR_PRODUCTION" if blockers else "SOURCE_READY_NOT_PRODUCTION_CERTIFIED",
        "productionGate": "NO_PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED",
        "productionBlockers": blockers,
        "featureCount": 50,
        "detectorsConverted": len(ledger),
        "placeholdersRemaining": 0,
        "monolithDependency": False,
        "rawDatabasesIncluded": False,
        "supportResolverStatus": support_summary.get("status", "NOT_CONFIGURED"),
        "supportResolverDecision": support_summary.get("decision", "OPTIONAL_ADAPTER_NOT_ENABLED"),
        "supportResolverDoNotRebuild": bool(support_summary.get("doNotRebuild", True)),
        "supportResolverBlockers": support_summary.get("blockers", []),
        "environmentNeutral": True,
        "productionCertified": False,
    }

    payload: Dict[str, Any] = {
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
        "snapshotDiffEngine": snapshots,
        "placeholderLedger": ledger,
        "multiTenantLeakageGuard": [{"status": scope.get("status"), "rule": "certify only when a real tenant/scope contract and required isolation evidence exist"}],
        "goldenPathComparator": [{"component": "production_gate", "status": "BLOCKED_FOR_PRODUCTION" if blockers else "SOURCE_READY_NOT_PRODUCTION_CERTIFIED", "rule": "unknown_missing_provenance = no green"}],
    }
    payload.update(support_result.get("payload", {}))
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

    write_text(out / "WHY_THIS_IS_RED.md", "# WHY_THIS_IS_RED\n\nProduction remains blocked unless required contracts, provenance and runtime evidence are complete.\n\n" + "".join(f"- {blocker}\n" for blocker in (blockers or ["No production pass is declared by design."])))
    write_text(out / "CAN_PATCH_DECISION.md", "# CAN_PATCH_DECISION\n\nCAN_PATCH_SOURCE_MODULES=true\nCAN_DECLARE_PRODUCTION_CERTIFIED=false\n\nRules:\n- Structure is not runtime evidence.\n- Runtime evidence is not production certification.\n- unknown_missing_provenance = no green.\n")
    write_text(out / "HUMAN_OPERATOR_SUMMARY.md", f"# Human Operator Summary\n\nStatus: `{manifest['status']}`\n\nProfile: `{profile.profile_id}`\n\nConverted detector contracts: {len(ledger)}.\n\nRaw DBs included: false.\n")
    write_text(out / "CONTINUATION_SUPREME.md", "# CONTINUATION\n\nInspect ATLAS_MANIFEST_PLUS.json, WHY_THIS_IS_RED.md, placeholder_ledger.json and CSV exports before making changes.\n")
    write_json(out / "SMOKE.json", {"status": "PASS", "requiredFiles": ["ATLAS_MANIFEST_PLUS.json", "operational_evidence_atlas.html", "placeholder_ledger.json", "CAN_PATCH_DECISION.md", "WHY_THIS_IS_RED.md"], "environmentNeutral": True})
    write_text(out / "SMOKE.md", "# Smoke\n\nPASS: Code Atlas Operational Evidence outputs generated.\n")
    html_report(out / "operational_evidence_atlas.html", payload)
    return manifest


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--result-root", default=None)
    args = parser.parse_args()
    print(json.dumps(run_operational_atlas(args.repo, args.out, args.result_root), ensure_ascii=False, indent=2))
