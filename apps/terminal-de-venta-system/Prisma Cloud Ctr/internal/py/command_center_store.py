# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import hashlib
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from commercial_contracts import (
    CommercialContractError,
    count_commercial_contracts,
    ensure_commercial_schema,
    insert_commercial_contract,
    list_commercial_contracts,
    resolve_commercial_terms,
)

from commercial_billing import (
    BillingError,
    billing_command,
    billing_snapshot,
    ensure_billing_schema,
)

LAB_ROOT = Path(__file__).resolve().parents[2]
TERMINAL_ROOT = LAB_ROOT.parent
DATA_DIR = LAB_ROOT / "internal" / "data"
DB_PATH = Path(os.environ.get("PRISMA_COMMAND_CENTER_DB_PATH") or (DATA_DIR / "prisma-command-center.db"))
PLAN_CATALOG_PATH = TERMINAL_ROOT / "shared" / "licensing" / "plan-catalog.canonical.json"

PREFIX = {"client":"CLI","device":"DEV","license":"LIC","contract":"CTR","charge":"COB","payment":"PAY","fiscal":"CFD","provisioning":"ALT","deactivation":"BAJ","note":"NTE","receipt":"RCP","case":"CAS","evidence":"EVD","backup":"BKP","rollback":"RBK","item":"ID"}
FIRST_CUSTOMER = {
    "displayName": "Prisma Original Customer",
    "tenantSlug": "prisma-original-customer",
    "customerId": "cust_prisma_original_customer",
    "licenseId": "lic_prisma_original_customer_001",
    "businessId": "biz_78b3c840796a4a4dad",
    "storeId": "store_00728649f3804a9e82",
    "tabletTerminalId": "term_49103c7382d84663a3",
    "pcDeviceId": "pc_prisma_original_customer_001",
    "tabletDeviceId": "tablet_prisma_original_customer_001",
    "mobileDeviceId": "mobile_prisma_original_customer_001",
}

def _canonical_license_plan_options():
    fallback = [
        (
            "TABLET_PC_MANAGED",
            "Tablet + PC Managed",
            {
                "maxDevices": 4,
                "maxBranches": 1,
                "maxStores": 1,
                "modules": ["pos.open", "event.outbox.view", "pc.open", "sync.managed"],
                "features": ["pos.open", "event.outbox.view", "pc.open", "sync.managed"],
                "canonicalPlan": "TABLET_PC_MANAGED",
                "source": "shared/licensing/plan-catalog.canonical.json",
            },
        )
    ]
    try:
        payload = json.loads(PLAN_CATALOG_PATH.read_text(encoding="utf-8"))
        plans = payload.get("plans") if isinstance(payload, dict) else []
        options = []
        for plan in plans if isinstance(plans, list) else []:
            if not isinstance(plan, dict) or not plan.get("vendible"):
                continue
            code = str(plan.get("plan") or "").strip()
            if not code:
                continue
            limits = plan.get("limits") if isinstance(plan.get("limits"), dict) else {}
            features = plan.get("features") if isinstance(plan.get("features"), list) else []
            commercial = plan.get("commercial") if isinstance(plan.get("commercial"), dict) else {}
            policy = payload.get("commercialPolicy") if isinstance(payload.get("commercialPolicy"), dict) else {}
            options.append(
                (
                    code,
                    str(plan.get("label") or code),
                    {
                        "maxDevices": limits.get("maxDevices"),
                        "maxBranches": limits.get("maxBranches"),
                        "maxStores": limits.get("maxStores"),
                        "modules": features,
                        "features": features,
                        "canonicalPlan": code,
                        "source": "shared/licensing/plan-catalog.canonical.json",
                        "tier": int(plan.get("rank") or 100),
                        "commercial": commercial,
                        "commercialPolicy": {
                            "effectiveFrom": policy.get("effectiveFrom"),
                            "market": policy.get("market"),
                            "currency": policy.get("currency"),
                            "taxTreatment": policy.get("taxTreatment"),
                            "billingScope": policy.get("billingScope"),
                            "periods": policy.get("periods") if isinstance(policy.get("periods"), dict) else {},
                            "grandfathering": policy.get("grandfathering") if isinstance(policy.get("grandfathering"), dict) else {},
                        },
                    },
                )
            )
        return options or fallback
    except Exception:
        return fallback

CATALOGS = {
 "vertical": ("Giro / vertical", True, [("retail","Retail",{"suggestedPlan":"starter","modules":["pos","inventory","tickets","cash_cuts"]}),("abarrotes","Abarrotes / minisuper",{"suggestedPlan":"starter","modules":["pos","inventory","tickets","cash_cuts"]}),("restaurant","Restaurante / food service",{"suggestedPlan":"business","modules":["pos","tables","tickets","cash_cuts"]}),("bar","Bar",{"suggestedPlan":"business","modules":["pos","tables","tickets","cash_cuts"]}),("pharmacy","Farmacia",{"suggestedPlan":"business","modules":["pos","inventory","batch_tracking","tickets"]}),("hardware","Ferretería",{"suggestedPlan":"business","modules":["pos","inventory","quotes","tickets"]}),("fashion","Moda / boutique",{"suggestedPlan":"starter","modules":["pos","inventory","tickets"]}),("butcher","Carnicería",{"suggestedPlan":"business","modules":["pos","scale_support","inventory","tickets"]}),("tortilla","Tortillería",{"suggestedPlan":"starter","modules":["pos","tickets","cash_cuts"]}),("services","Servicios",{"suggestedPlan":"starter","modules":["pos","tickets","appointments"]}),("multi_branch","Multi-sucursal",{"suggestedPlan":"enterprise","modules":["pos","inventory","multi_branch","reports"]}),("other","Otro",{"requiresManualText":True})]),
 "subvertical": ("Subvertical", True, [("minisuper","Minisuper",{}),("specialty_store","Tienda especializada",{}),("restaurant_tables","Restaurante con mesas",{}),("quick_service","Comida rápida",{}),("coffee_shop","Cafetería",{}),("workshop","Taller",{}),("clinic","Consultorio",{}),("rental","Renta / servicios",{}),("other","Otro",{"requiresManualText":True})]),
 "business_size": ("Tamaño", False, [("small","Pequeño",{}),("medium","Mediano",{}),("multi_branch","Multi-sucursal",{}),("enterprise","Enterprise",{})]),
 "operation_mode": ("Tipo de operación", True, [("counter","Mostrador",{}),("tables","Mesas",{}),("inventory","Inventario fuerte",{}),("services","Servicios/citas",{}),("mixed","Mixto",{}),("other","Otro",{"requiresManualText":True})]),
 "license_plan": ("Tipo de licencia", False, _canonical_license_plan_options()),
 "device_type": ("Tipo de dispositivo", True, [("tablet_pos","Tablet POS",{"prefix":"TAB"}),("pc_register","Caja PC",{"prefix":"PC"}),("mobile","Terminal móvil",{"prefix":"MOB"}),("backoffice","Backoffice",{"prefix":"BO"}),("kiosk","Kiosko",{"prefix":"KSK"}),("peripheral","Periférico",{"prefix":"PER"}),("other","Otro",{"requiresManualText":True,"prefix":"OTH"})]),
 "deactivation_reason": ("Motivo de baja", True, [("cancellation","Cancelación",{}),("non_payment","Falta de pago",{}),("demo_ended","Fin de piloto",{}),("device_replacement","Cambio de dispositivo",{}),("duplicate_client","Cliente duplicado",{}),("migration","Migración",{}),("fraud_abuse","Fraude / abuso",{}),("support","Soporte técnico",{}),("other","Otro",{"requiresManualText":True})]),
 "city_zone": ("Ciudad / zona", True, [("mexico_city","CDMX",{}),("edomex","Estado de México",{}),("guadalajara","Guadalajara",{}),("monterrey","Monterrey",{}),("queretaro","Querétaro",{}),("other","Otro",{"requiresManualText":True})])
}

def uid():
    return uuid.uuid4().hex

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def jd(value):
    return json.dumps(value if value is not None else {}, ensure_ascii=False, sort_keys=True)

def jl(value):
    if value is None:
        return {}
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return {}

def norm_code(value, fallback="item"):
    value = re.sub(r"[^a-zA-Z0-9_-]", "", str(value or fallback)).lower()
    return value or fallback

def db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def _exec_schema(con):
    statements = [
        "CREATE TABLE IF NOT EXISTS Catalog(id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, label TEXT NOT NULL, description TEXT, mode TEXT DEFAULT 'governed', allowOther INTEGER DEFAULT 0, sortOrder INTEGER DEFAULT 100, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS CatalogOption(id TEXT PRIMARY KEY, catalogId TEXT NOT NULL, code TEXT NOT NULL, label TEXT NOT NULL, description TEXT, metadata TEXT, active INTEGER DEFAULT 1, sortOrder INTEGER DEFAULT 100, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(catalogId,code))",
        "CREATE INDEX IF NOT EXISTS CatalogOption_catalogId_active_idx ON CatalogOption(catalogId,active)",
        "CREATE TABLE IF NOT EXISTS CatalogOtherSubmission(id TEXT PRIMARY KEY, catalogId TEXT NOT NULL, manualText TEXT NOT NULL, normalized TEXT, status TEXT DEFAULT 'pending_catalog_review', context TEXT, createdBy TEXT DEFAULT 'local_operator', createdAt TEXT DEFAULT CURRENT_TIMESTAMP, reviewedAt TEXT, reviewedBy TEXT)",
        "CREATE INDEX IF NOT EXISTS CatalogOtherSubmission_catalogId_status_idx ON CatalogOtherSubmission(catalogId,status)",
        "CREATE TABLE IF NOT EXISTS IdentitySequence(id TEXT PRIMARY KEY, kind TEXT NOT NULL, year INTEGER NOT NULL, prefix TEXT NOT NULL, lastNumber INTEGER DEFAULT 0, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(kind,year))",
        "CREATE TABLE IF NOT EXISTS GeneratedIdentity(id TEXT PRIMARY KEY, kind TEXT NOT NULL, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, prefix TEXT NOT NULL, year INTEGER NOT NULL, sequence INTEGER NOT NULL, metadata TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS CommandClient(id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, displayName TEXT NOT NULL, legalName TEXT, status TEXT DEFAULT 'prepared', verticalCode TEXT, subverticalCode TEXT, sizeCode TEXT, operationCode TEXT, cityZoneCode TEXT, catalogOther TEXT, cloudTenantId TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS ClientContact(id TEXT PRIMARY KEY, clientId TEXT NOT NULL, role TEXT DEFAULT 'primary', name TEXT, phone TEXT, email TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS ClientNote(id TEXT PRIMARY KEY, clientId TEXT NOT NULL, noteType TEXT DEFAULT 'internal', text TEXT NOT NULL, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS LicensePlan(id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, label TEXT NOT NULL, tier INTEGER DEFAULT 100, description TEXT, maxDevices INTEGER, maxBranches INTEGER, active INTEGER DEFAULT 1, modules TEXT, rules TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS LicenseAssignment(id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, clientId TEXT NOT NULL, planId TEXT NOT NULL, status TEXT DEFAULT 'prepared', validFrom TEXT, validUntil TEXT, modules TEXT, limits TEXT, cloudLicenseId TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS ManagedDevice(id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, clientId TEXT, deviceType TEXT NOT NULL, roleCode TEXT, status TEXT DEFAULT 'pending_registration', registerCode TEXT UNIQUE, cloudDeviceId TEXT, lastSeenAt TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS ProvisioningDraft(id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, clientId TEXT, kind TEXT NOT NULL, status TEXT DEFAULT 'prepared', payload TEXT NOT NULL, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS DeactivationRequest(id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, targetKind TEXT NOT NULL, targetCode TEXT, reasonCode TEXT NOT NULL, reasonOther TEXT, status TEXT DEFAULT 'prepared', impact TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS CommandAuditEvent(id TEXT PRIMARY KEY, eventType TEXT NOT NULL, actor TEXT DEFAULT 'local_operator', entityKind TEXT, entityCode TEXT, summary TEXT NOT NULL, payload TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS CommandCenterSettings(id TEXT PRIMARY KEY, key TEXT NOT NULL UNIQUE, value TEXT NOT NULL, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS CloudBridgeStatus(id TEXT PRIMARY KEY, mode TEXT DEFAULT 'local_prepared', cloudOrigin TEXT DEFAULT 'https://app.hitechrts.com', tokenState TEXT DEFAULT 'unknown', lastCheckedAt TEXT, payload TEXT)"
        ,"CREATE TABLE IF NOT EXISTS SupportCase(id TEXT PRIMARY KEY, caseCode TEXT NOT NULL UNIQUE, clientRequestId TEXT UNIQUE, title TEXT NOT NULL, supportCode TEXT, severity TEXT NOT NULL DEFAULT 'warning', status TEXT NOT NULL DEFAULT 'CASE_OPEN', stage TEXT NOT NULL DEFAULT 'SCOPE_RESOLVING', assignedTo TEXT, scope TEXT NOT NULL DEFAULT '{}', expectedSourceRevision TEXT, revision INTEGER NOT NULL DEFAULT 1, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP, closedAt TEXT)"
        ,"CREATE TABLE IF NOT EXISTS SupportCaseEvent(id TEXT PRIMARY KEY, caseId TEXT NOT NULL, eventType TEXT NOT NULL, fromState TEXT, toState TEXT, correlationId TEXT NOT NULL, summary TEXT NOT NULL, payload TEXT NOT NULL DEFAULT '{}', createdAt TEXT DEFAULT CURRENT_TIMESTAMP)"
        ,"CREATE INDEX IF NOT EXISTS idx_support_case_status_updated ON SupportCase(status, updatedAt DESC)"
        ,"CREATE INDEX IF NOT EXISTS idx_support_case_event_case_created ON SupportCaseEvent(caseId, createdAt DESC)"
        ,"CREATE TABLE IF NOT EXISTS SupportCommandRun(id TEXT PRIMARY KEY, caseId TEXT, commandId TEXT NOT NULL, idempotencyKey TEXT NOT NULL UNIQUE, expectedRevision INTEGER, beforeRevision INTEGER, afterRevision INTEGER, status TEXT NOT NULL, backupId TEXT, rollbackId TEXT, correlationId TEXT NOT NULL, payload TEXT NOT NULL DEFAULT '{}', result TEXT NOT NULL DEFAULT '{}', createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)"
        ,"CREATE INDEX IF NOT EXISTS idx_support_command_case_created ON SupportCommandRun(caseId, createdAt DESC)"
        ,"CREATE TABLE IF NOT EXISTS SupportEvidence(id TEXT PRIMARY KEY, evidenceCode TEXT NOT NULL UNIQUE, caseId TEXT, evidenceType TEXT NOT NULL, source TEXT NOT NULL, sourceRevision TEXT, correlationId TEXT NOT NULL, sha256 TEXT NOT NULL, redacted INTEGER NOT NULL DEFAULT 1, payload TEXT NOT NULL DEFAULT '{}', observedAt TEXT NOT NULL, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)"
        ,"CREATE INDEX IF NOT EXISTS idx_support_evidence_case_created ON SupportEvidence(caseId, createdAt DESC)"
        ,"CREATE TABLE IF NOT EXISTS SupportRollbackSnapshot(id TEXT PRIMARY KEY, backupCode TEXT NOT NULL UNIQUE, caseId TEXT, commandId TEXT NOT NULL, correlationId TEXT NOT NULL, sourceRevision INTEGER, sha256 TEXT NOT NULL, snapshot TEXT NOT NULL, restoredAt TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)"
    ]
    for sql in statements:
        con.execute(sql)
    ensure_commercial_schema(con)
    ensure_billing_schema(con)

def _seed_first_customer(con):
    payload = {
        "customer": FIRST_CUSTOMER,
        "license": {
            "plan": "TABLET_PC_MANAGED",
            "status": "active_local_signed",
            "source": "adlant4_local_signed_license",
        },
        "devices": [
            {"surface": "pc", "deviceId": FIRST_CUSTOMER["pcDeviceId"], "status": "pending_registration"},
            {"surface": "tablet", "deviceId": FIRST_CUSTOMER["tabletDeviceId"], "status": "pending_registration", "terminalId": FIRST_CUSTOMER["tabletTerminalId"]},
            {"surface": "mobile", "deviceId": FIRST_CUSTOMER["mobileDeviceId"], "status": "pending_registration"},
        ],
    }
    con.execute(
        "INSERT OR IGNORE INTO CommandClient(id,internalId,humanCode,displayName,legalName,status,verticalCode,subverticalCode,sizeCode,operationCode,cityZoneCode,catalogOther,cloudTenantId) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "client_prisma_original_customer",
            "client_prisma_original_customer",
            "CLI-PRISMA-ORIGINAL",
            FIRST_CUSTOMER["displayName"],
            FIRST_CUSTOMER["displayName"],
            "active_local_signed",
            "abarrotes",
            "minisuper",
            "small",
            "counter",
            "mexico_city",
            jd({"businessId": FIRST_CUSTOMER["businessId"], "storeId": FIRST_CUSTOMER["storeId"]}),
            FIRST_CUSTOMER["tenantSlug"],
        ),
    )
    con.execute(
        "UPDATE CommandClient SET displayName=?, legalName=?, status=?, verticalCode=?, subverticalCode=?, sizeCode=?, operationCode=?, cityZoneCode=?, catalogOther=?, cloudTenantId=?, updatedAt=CURRENT_TIMESTAMP WHERE id=?",
        (
            FIRST_CUSTOMER["displayName"],
            FIRST_CUSTOMER["displayName"],
            "active_local_signed",
            "abarrotes",
            "minisuper",
            "small",
            "counter",
            "mexico_city",
            jd({"businessId": FIRST_CUSTOMER["businessId"], "storeId": FIRST_CUSTOMER["storeId"]}),
            FIRST_CUSTOMER["tenantSlug"],
            "client_prisma_original_customer",
        ),
    )
    con.execute(
        "INSERT OR IGNORE INTO LicenseAssignment(id,internalId,humanCode,clientId,planId,status,modules,limits,cloudLicenseId) VALUES(?,?,?,?,?,?,?,?,?)",
        (
            "license_prisma_original_customer",
            "license_prisma_original_customer",
            "LIC-PRISMA-ORIGINAL",
            "client_prisma_original_customer",
            "plan_TABLET_PC_MANAGED",
            "active_local_signed",
            jd(["pos.open", "event.outbox.view", "pc.open", "sync.managed"]),
            jd({"maxDevices": 4, "maxBranches": 1, "maxStores": 1}),
            FIRST_CUSTOMER["licenseId"],
        ),
    )
    con.execute(
        "UPDATE LicenseAssignment SET planId=?, status=?, modules=?, limits=?, cloudLicenseId=?, updatedAt=CURRENT_TIMESTAMP WHERE id=?",
        (
            "plan_TABLET_PC_MANAGED",
            "active_local_signed",
            jd(["pos.open", "event.outbox.view", "pc.open", "sync.managed"]),
            jd({"maxDevices": 4, "maxBranches": 1, "maxStores": 1}),
            FIRST_CUSTOMER["licenseId"],
            "license_prisma_original_customer",
        ),
    )
    for row in [
        ("managed_pc_prisma_original_customer_001", "DEV-PRISMA-PC-001", "pc_register", "pc_backoffice", "REG-PRISMA-PC-001", FIRST_CUSTOMER["pcDeviceId"]),
        ("managed_tablet_prisma_original_customer_001", "DEV-PRISMA-TAB-001", "tablet_pos", "tablet_pos", "REG-PRISMA-TAB-001", FIRST_CUSTOMER["tabletDeviceId"]),
        ("managed_mobile_prisma_original_customer_001", "DEV-PRISMA-MOB-001", "mobile", "mobile_supervisor", "REG-PRISMA-MOB-001", FIRST_CUSTOMER["mobileDeviceId"]),
    ]:
        device_id, human_code, device_type, role_code, register_code, cloud_device_id = row
        con.execute(
            "INSERT OR IGNORE INTO ManagedDevice(id,internalId,humanCode,clientId,deviceType,roleCode,status,registerCode,cloudDeviceId) VALUES(?,?,?,?,?,?,?,?,?)",
            (device_id, device_id, human_code, "client_prisma_original_customer", device_type, role_code, "pending_registration", register_code, cloud_device_id),
        )
        con.execute(
            "UPDATE ManagedDevice SET clientId=?, deviceType=?, roleCode=?, status=?, registerCode=?, cloudDeviceId=?, updatedAt=CURRENT_TIMESTAMP WHERE id=?",
            ("client_prisma_original_customer", device_type, role_code, "pending_registration", register_code, cloud_device_id, device_id),
        )
    con.execute(
        "INSERT OR IGNORE INTO ProvisioningDraft(id,internalId,humanCode,clientId,kind,status,payload) VALUES(?,?,?,?,?,?,?)",
        (
            "draft_prisma_original_customer_registration",
            "draft_prisma_original_customer_registration",
            "ALT-PRISMA-ORIGINAL",
            "client_prisma_original_customer",
            "first_customer_registration",
            "prepared",
            jd(payload),
        ),
    )
    con.execute(
        "UPDATE ProvisioningDraft SET status=?, payload=?, updatedAt=CURRENT_TIMESTAMP WHERE id=?",
        ("prepared", jd(payload), "draft_prisma_original_customer_registration"),
    )
    con.execute(
        "INSERT OR IGNORE INTO CommandAuditEvent(id,eventType,actor,entityKind,entityCode,summary,payload) VALUES(?,?,?,?,?,?,?)",
        (
            "audit_prisma_original_customer_seed",
            "first_customer_prepared",
            "local_operator",
            "client",
            "CLI-PRISMA-ORIGINAL",
            f"Primer cliente preparado: {FIRST_CUSTOMER['displayName']}",
            jd(payload),
        ),
    )

def ensure_initialized():
    with db() as con:
        _exec_schema(con)
        # Seed static catalogs/options idempotently.
        for idx, (code, spec) in enumerate(CATALOGS.items(), start=1):
            label, allow_other, options = spec
            catalog_id = f"cat_{code}"
            con.execute(
                "INSERT OR IGNORE INTO Catalog(id,code,label,allowOther,sortOrder) VALUES(?,?,?,?,?)",
                (catalog_id, code, label, 1 if allow_other else 0, idx * 10),
            )
            con.execute("UPDATE Catalog SET label=?, allowOther=? WHERE id=?", (label, 1 if allow_other else 0, catalog_id))
            for pos, (opt_code, opt_label, metadata) in enumerate(options, start=1):
                con.execute(
                    "INSERT OR IGNORE INTO CatalogOption(id,catalogId,code,label,metadata,active,sortOrder) VALUES(?,?,?,?,?,?,?)",
                    (f"opt_{code}_{opt_code}", catalog_id, opt_code, opt_label, jd(metadata or {}), 1, pos * 10),
                )
                con.execute(
                    "UPDATE CatalogOption SET label=?, metadata=?, active=1, sortOrder=? WHERE catalogId=? AND code=?",
                    (opt_label, jd(metadata or {}), pos * 10, catalog_id, opt_code),
                )
        # Seed LicensePlan from license_plan catalog options so LicenseAssignment can reference real rows.
        for opt_code, opt_label, metadata in CATALOGS.get("license_plan", ("", False, []))[2]:
            if opt_code in ("suspended", "expired"):
                active = 0
            else:
                active = 1
            con.execute(
                "INSERT OR IGNORE INTO LicensePlan(id,code,label,tier,maxDevices,maxBranches,modules,rules,active) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    f"plan_{opt_code}",
                    opt_code,
                    opt_label,
                    int(metadata.get("tier") or 100),
                    metadata.get("maxDevices"),
                    metadata.get("maxBranches"),
                    jd(metadata.get("modules") or []),
                    jd(metadata),
                    active,
                ),
            )
            con.execute(
                "UPDATE LicensePlan SET label=?, maxDevices=?, maxBranches=?, modules=?, rules=?, active=? WHERE code=?",
                (opt_label, metadata.get("maxDevices"), metadata.get("maxBranches"), jd(metadata.get("modules") or []), jd(metadata), active, opt_code),
            )
        con.execute(
            "INSERT OR IGNORE INTO CloudBridgeStatus(id,mode,cloudOrigin,tokenState,lastCheckedAt,payload) VALUES(?,?,?,?,?,?)",
            ("bridge_local", "local_prepared", "https://app.hitechrts.com", "server_side_or_absent", now_iso(), jd({"note":"Command Center local workflow DB"})),
        )
        _seed_first_customer(con)
        con.commit()

def catalogs(con):
    out = {}
    for row in con.execute("SELECT * FROM Catalog ORDER BY sortOrder, label"):
        item = dict(row)
        item["allowOther"] = bool(item.get("allowOther"))
        item["options"] = []
        out[item["code"]] = item
    for row in con.execute("SELECT * FROM CatalogOption WHERE active=1 ORDER BY catalogId, sortOrder, label"):
        opt = dict(row)
        opt["active"] = bool(opt.get("active"))
        opt["metadata"] = jl(opt.get("metadata"))
        cat = next((c for c in out.values() if c["id"] == opt["catalogId"]), None)
        if cat:
            cat["options"].append(opt)
    # Dynamic client catalog so device/license/baja can select a prepared client.
    client_options = []
    for row in con.execute("SELECT id,humanCode,displayName,status,verticalCode,operationCode,createdAt FROM CommandClient ORDER BY createdAt DESC LIMIT 100"):
        r = dict(row)
        client_options.append({
            "id": r["id"],
            "code": r["humanCode"],
            "label": f"{r['displayName']} · {r['humanCode']}",
            "active": True,
            "metadata": {"dbId": r["id"], "status": r.get("status"), "vertical": r.get("verticalCode"), "operation": r.get("operationCode")},
        })
    out["client"] = {
        "id": "dynamic_client",
        "code": "client",
        "label": "Cliente destino",
        "description": "Clientes preparados localmente",
        "allowOther": False,
        "mode": "dynamic",
        "options": client_options,
    }
    return out

def gen(con, kind, meta=None):
    kind = norm_code(kind)
    prefix = PREFIX.get(kind, kind[:3].upper() or "ID")
    year = datetime.now().year
    row = con.execute("SELECT * FROM IdentitySequence WHERE kind=? AND year=?", (kind, year)).fetchone()
    seq = int(row["lastNumber"]) + 1 if row else 1
    if row:
        con.execute("UPDATE IdentitySequence SET lastNumber=?, updatedAt=CURRENT_TIMESTAMP WHERE id=?", (seq, row["id"]))
    else:
        con.execute("INSERT INTO IdentitySequence(id,kind,year,prefix,lastNumber) VALUES(?,?,?,?,?)", (uid(), kind, year, prefix, seq))
    internal = f"{kind}_{uuid.uuid4().hex}"
    human = f"{prefix}-{year}-{seq:06d}"
    con.execute(
        "INSERT INTO GeneratedIdentity(id,kind,internalId,humanCode,prefix,year,sequence,metadata) VALUES(?,?,?,?,?,?,?,?)",
        (uid(), kind, internal, human, prefix, year, seq, jd(meta or {})),
    )
    return {"kind": kind, "internalId": internal, "humanCode": human, "prefix": prefix, "year": year, "sequence": seq}

def reco(cats, b):
    vertical = b.get("vertical") or "abarrotes"
    size = b.get("businessSize") or "small"
    op = b.get("operationMode") or "counter"
    opts = {o["code"]: o for o in cats.get("vertical", {}).get("options", [])}
    meta = (opts.get(vertical) or {}).get("metadata") or {}
    available_plans = {code for code, _label, _metadata in CATALOGS.get("license_plan", ("", False, []))[2]}
    plan = meta.get("suggestedPlan") or "TABLET_PC_MANAGED"
    if plan not in available_plans:
        plan = "TABLET_PC_MANAGED"
    mods = list(meta.get("modules") or ["pos", "tickets", "cash_cuts"])
    if op == "inventory" and "inventory" not in mods:
        mods.append("inventory")
    if op in ("tables", "mixed") and "tables" not in mods and vertical in ("restaurant", "bar"):
        mods.append("tables")
    if size in ("multi_branch", "enterprise"):
        plan = "TABLET_PC_MANAGED"
        if "multi_branch" not in mods:
            mods.append("multi_branch")
    device = "pc_register" if op == "tables" else "tablet_pos"
    return {"suggestedPlan": plan, "suggestedModules": mods, "suggestedDeviceType": device, "contractTemplate": f"contract_{vertical}"}

def add_event(con, typ, kind, code, summary, payload):
    con.execute(
        "INSERT INTO CommandAuditEvent(id,eventType,entityKind,entityCode,summary,payload) VALUES(?,?,?,?,?,?)",
        (uid(), typ, kind, code, summary, jd(payload)),
    )

def _counts(con):
    return {
        "clients": con.execute("SELECT COUNT(*) FROM CommandClient").fetchone()[0],
        "activeClients": con.execute("SELECT COUNT(*) FROM CommandClient WHERE status IN ('active','prepared','pending_cloud_activation','active_local_signed')").fetchone()[0],
        "preparedDrafts": con.execute("SELECT COUNT(*) FROM ProvisioningDraft WHERE status='prepared'").fetchone()[0],
        "licenses": con.execute("SELECT COUNT(*) FROM LicenseAssignment").fetchone()[0],
        "devices": con.execute("SELECT COUNT(*) FROM ManagedDevice").fetchone()[0],
        "deactivations": con.execute("SELECT COUNT(*) FROM DeactivationRequest").fetchone()[0],
        "othersPending": con.execute("SELECT COUNT(*) FROM CatalogOtherSubmission WHERE status='pending_catalog_review'").fetchone()[0],
        "identities": con.execute("SELECT COUNT(*) FROM GeneratedIdentity").fetchone()[0],
        "auditEvents": con.execute("SELECT COUNT(*) FROM CommandAuditEvent").fetchone()[0],
        "contracts": count_commercial_contracts(con),
    }

def _rows(con, sql, args=()):
    return [dict(r) for r in con.execute(sql, args)]

def _local_payload(con):
    clients = _rows(con, "SELECT id,internalId,humanCode,displayName,status,verticalCode,subverticalCode,sizeCode,operationCode,cityZoneCode,createdAt FROM CommandClient ORDER BY createdAt DESC LIMIT 50")
    licenses = _rows(con, """SELECT la.id,la.internalId,la.humanCode,la.status,la.modules,la.limits,la.createdAt,c.humanCode AS clientCode,c.displayName AS clientName,lp.code AS planCode,lp.label AS planLabel
                              FROM LicenseAssignment la
                              LEFT JOIN CommandClient c ON c.id=la.clientId
                              LEFT JOIN LicensePlan lp ON lp.id=la.planId
                              ORDER BY la.createdAt DESC LIMIT 50""")
    devices = _rows(con, """SELECT d.id,d.internalId,d.humanCode,d.deviceType,d.roleCode,d.status,d.registerCode,d.createdAt,c.humanCode AS clientCode,c.displayName AS clientName
                            FROM ManagedDevice d LEFT JOIN CommandClient c ON c.id=d.clientId ORDER BY d.createdAt DESC LIMIT 50""")
    deactivations = _rows(con, "SELECT id,internalId,humanCode,targetKind,targetCode,reasonCode,reasonOther,status,createdAt FROM DeactivationRequest ORDER BY createdAt DESC LIMIT 50")
    drafts = _rows(con, "SELECT id,internalId,humanCode,clientId,kind,status,createdAt FROM ProvisioningDraft ORDER BY createdAt DESC LIMIT 50")
    contracts = list_commercial_contracts(con)
    others = _rows(con, """SELECT o.id,c.code AS catalogKey,c.label AS catalogLabel,o.manualText,o.status,o.createdAt
                           FROM CatalogOtherSubmission o LEFT JOIN Catalog c ON c.id=o.catalogId
                           ORDER BY o.createdAt DESC LIMIT 50""")
    events = _rows(con, "SELECT eventType,entityKind,entityCode,summary,createdAt FROM CommandAuditEvent ORDER BY createdAt DESC LIMIT 24")
    return {"clients": clients, "licenses": licenses, "contracts": contracts, "devices": devices, "deactivations": deactivations, "drafts": drafts, "othersPending": others, "events": events}

def _plan_by_code(con, plan_code):
    plan_code = plan_code or "TABLET_PC_MANAGED"
    row = con.execute("SELECT * FROM LicensePlan WHERE code=?", (plan_code,)).fetchone()
    if row:
        return dict(row)
    row = con.execute("SELECT * FROM LicensePlan WHERE code='TABLET_PC_MANAGED'").fetchone()
    return dict(row) if row else {"id":"plan_TABLET_PC_MANAGED","code":"TABLET_PC_MANAGED","label":"Tablet + PC Managed","modules":jd(["pos.open","event.outbox.view","pc.open","sync.managed"]),"rules":jd({"canonicalPlan":"TABLET_PC_MANAGED"})}

def _client_by_code(con, client_code=None):
    if client_code:
        row = con.execute("SELECT * FROM CommandClient WHERE humanCode=? OR id=?", (client_code, client_code)).fetchone()
        if row:
            return dict(row)
    row = con.execute("SELECT * FROM CommandClient ORDER BY createdAt DESC LIMIT 1").fetchone()
    return dict(row) if row else None

def bootstrap(con):
    cats = catalogs(con)
    plans = []
    for row in con.execute("SELECT * FROM LicensePlan ORDER BY tier, label"):
        r = dict(row)
        plans.append({
            "id": r["id"],
            "code": r["code"],
            "label": r["label"],
            "maxDevices": r.get("maxDevices"),
            "maxBranches": r.get("maxBranches"),
            "modules": jl(r.get("modules")),
            "rules": jl(r.get("rules")),
            "commercial": (jl(r.get("rules")) or {}).get("commercial") or {},
            "commercialPolicy": (jl(r.get("rules")) or {}).get("commercialPolicy") or {},
            "active": bool(r.get("active")),
        })
    bridge = con.execute("SELECT * FROM CloudBridgeStatus WHERE id='bridge_local'").fetchone()
    return {
        "ok": True,
        "mode": "local_catalogs",
        "workflowMode": "local_prepared_not_cloud_created",
        "dbPath": str(DB_PATH),
        "schemaVersion": 4,
        "catalogs": cats,
        "licensePlans": plans,
        "billing": billing_snapshot(con),
        "counts": _counts(con),
        "local": _local_payload(con),
        "cloudBridge": dict(bridge) if bridge else None,
        "lastEvents": _local_payload(con)["events"],
    }

def other(con, b):
    cats = catalogs(con)
    code = str(b.get("catalog") or "").strip()
    txt = str(b.get("manualText") or "").strip()
    if code not in cats:
        return {"ok": False, "error": "Catálogo inválido", "catalog": code}
    if not cats[code].get("allowOther"):
        return {"ok": False, "error": "Catálogo no permite Otro", "catalog": code}
    if len(txt) < 2:
        return {"ok": False, "error": "Texto Otro obligatorio"}
    iid = uid()
    con.execute(
        "INSERT INTO CatalogOtherSubmission(id,catalogId,manualText,normalized,status,context) VALUES(?,?,?,?,?,?)",
        (iid, cats[code]["id"], txt[:160], txt.lower()[:160], "pending_catalog_review", jd(b.get("context") or {})),
    )
    payload = {"id": iid, "catalog": code, "manualText": txt[:160], "status": "pending_catalog_review"}
    add_event(con, "catalog_other_submitted", "catalog", code, f"Otro pendiente en {code}: {txt[:60]}", payload)
    return {"ok": True, **payload}

def draft_client(con, b):
    cats = catalogs(con)
    ids = {"client": gen(con, "client"), "contract": gen(con, "contract"), "provisioning": gen(con, "provisioning")}
    rec = reco(cats, b)
    name = str(b.get("displayName") or "Cliente preparado").strip()[:90] or "Cliente preparado"
    cid = uid()
    status = "pending_cloud_activation"
    con.execute(
        "INSERT INTO CommandClient(id,internalId,humanCode,displayName,legalName,status,verticalCode,subverticalCode,sizeCode,operationCode,cityZoneCode,catalogOther) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (cid, ids["client"]["internalId"], ids["client"]["humanCode"], name, b.get("legalName"), status, b.get("vertical"), b.get("subvertical"), b.get("businessSize"), b.get("operationMode"), b.get("cityZone"), jd(b.get("other") or {})),
    )
    if b.get("contactName") or b.get("phone") or b.get("email"):
        con.execute(
            "INSERT INTO ClientContact(id,clientId,role,name,phone,email) VALUES(?,?,?,?,?,?)",
            (uid(), cid, "primary", b.get("contactName"), b.get("phone"), b.get("email")),
        )
    con.execute(
        "INSERT INTO ClientNote(id,clientId,noteType,text) VALUES(?,?,?,?)",
        (uid(), cid, "system", "Alta preparada localmente desde Prisma Cloud Ctr. Pendiente activación cloud."),
    )
    payload = {"client": {"dbId": cid, "displayName": name, "status": status, **ids["client"]}, "contract": ids["contract"], "provisioning": ids["provisioning"], "recommendation": rec, "source": "local_prepared_not_cloud_created"}
    con.execute(
        "INSERT INTO ProvisioningDraft(id,internalId,humanCode,clientId,kind,status,payload) VALUES(?,?,?,?,?,?,?)",
        (uid(), ids["provisioning"]["internalId"], ids["provisioning"]["humanCode"], cid, "client_onboarding", "prepared", jd(payload)),
    )
    add_event(con, "client_prepared", "client", ids["client"]["humanCode"], f"Cliente preparado: {name}", payload)
    return {"ok": True, "mode": "prepared", "message": "Cliente preparado localmente; pendiente endpoint cloud de creación real.", **payload, "counts": _counts(con)}

def draft_device(con, b):
    client = _client_by_code(con, b.get("clientCode"))
    if not client:
        return {"ok": False, "error": "Primero prepara o selecciona un cliente para vincular el dispositivo."}
    device_type = b.get("deviceType") or reco(catalogs(con), b)["suggestedDeviceType"]
    ids = {"device": gen(con, "device", {"deviceType": device_type, "clientCode": client["humanCode"]}), "provisioning": gen(con, "provisioning")}
    reg = f"REG-{uuid.uuid4().hex[:6].upper()}-{uuid.uuid4().hex[:6].upper()}"
    con.execute(
        "INSERT INTO ManagedDevice(id,internalId,humanCode,clientId,deviceType,roleCode,status,registerCode) VALUES(?,?,?,?,?,?,?,?)",
        (uid(), ids["device"]["internalId"], ids["device"]["humanCode"], client["id"], device_type, b.get("operationMode") or b.get("roleCode"), "pending_registration", reg),
    )
    payload = {"client": {"dbId": client["id"], "humanCode": client["humanCode"], "displayName": client["displayName"]}, "device": {**ids["device"], "deviceType": device_type, "registerCode": reg, "status": "pending_registration"}, "provisioning": ids["provisioning"], "source": "local_prepared_not_cloud_registered"}
    con.execute(
        "INSERT INTO ProvisioningDraft(id,internalId,humanCode,clientId,kind,status,payload) VALUES(?,?,?,?,?,?,?)",
        (uid(), ids["provisioning"]["internalId"], ids["provisioning"]["humanCode"], client["id"], "device_registration", "prepared", jd(payload)),
    )
    add_event(con, "device_prepared", "device", ids["device"]["humanCode"], f"Dispositivo preparado para {client['displayName']}", payload)
    return {"ok": True, "mode": "prepared", "message": "Dispositivo preparado localmente con código de registro.", **payload, "counts": _counts(con)}

def draft_license(con, b):
    client = _client_by_code(con, b.get("clientCode"))
    if not client:
        return {"ok": False, "error": "Primero prepara o selecciona un cliente para asignar licencia."}
    rec = reco(catalogs(con), b)
    plan_code = b.get("plan") or rec["suggestedPlan"]
    plan = _plan_by_code(con, plan_code)
    modules = b.get("modules") or jl(plan.get("modules")) or rec["suggestedModules"]
    ids = {"license": gen(con, "license", {"plan": plan["code"], "clientCode": client["humanCode"]}), "contract": gen(con, "contract", {"clientCode": client["humanCode"], "plan": plan["code"]})}
    try:
        terms = resolve_commercial_terms(
  PLAN_CATALOG_PATH,
  plan["code"],
  billing_period=b.get("billingPeriod") or "monthly",
  agreed_price_mxn=b.get("agreedPriceMxn"),
  price_treatment=b.get("priceTreatment") or "canonical_list",
  price_evidence_ref=b.get("priceEvidenceRef"),
  commercial_note=b.get("commercialNote"),
  valid_from=b.get("validFrom"),
        )
    except CommercialContractError as exc:
        return {"ok": False, "resultCode": exc.code, "error": str(exc), "commercial": {"plan": plan["code"]}}
    plan_rules = jl(plan.get("rules")) or {}
    limits = {
        "maxDevices": plan.get("maxDevices"),
        "maxBranches": plan.get("maxBranches"),
        "maxStores": plan_rules.get("maxStores"),
    }
    license_assignment_id = uid()
    con.execute(
        "INSERT INTO LicenseAssignment(id,internalId,humanCode,clientId,planId,status,validFrom,validUntil,modules,limits) VALUES(?,?,?,?,?,?,?,?,?,?)",
        (license_assignment_id, ids["license"]["internalId"], ids["license"]["humanCode"], client["id"], plan["id"], "prepared", terms["validFrom"], terms["validUntil"], jd(modules), jd(limits)),
    )
    contract = insert_commercial_contract(
        con,
        identity=ids["contract"],
        client_id=client["id"],
        license_assignment_id=license_assignment_id,
        terms=terms,
    )
    payload = {
        "client": {"dbId": client["id"], "humanCode": client["humanCode"], "displayName": client["displayName"]},
        "license": {**ids["license"], "dbId": license_assignment_id, "plan": plan["code"], "planLabel": plan["label"], "modules": modules, "limits": limits, "status": "prepared", "validFrom": terms["validFrom"], "validUntil": terms["validUntil"]},
        "contract": contract,
        "source": "local_prepared_not_cloud_licensed",
    }
    con.execute(
        "INSERT INTO ProvisioningDraft(id,internalId,humanCode,clientId,kind,status,payload) VALUES(?,?,?,?,?,?,?)",
        (uid(), ids["contract"]["internalId"], ids["contract"]["humanCode"], client["id"], "license_assignment", "prepared", jd(payload)),
    )
    add_event(
        con,
        "license_prepared",
        "license",
        ids["license"]["humanCode"],
        f"Licencia {plan['label']} {terms['billingPeriod']} por ${terms['agreedPriceMxn']} MXN + IVA preparada para {client['displayName']}",
        payload,
    )
    return {"ok": True, "mode": "prepared", "message": "Licencia y contrato comercial preparados localmente; pendiente activación cloud real.", **payload, "counts": _counts(con)}

def draft_deactivation(con, b):
    target_kind = norm_code(b.get("targetKind") or "client", "client")
    target_code = b.get("targetCode") or b.get("clientCode")
    client = _client_by_code(con, target_code) if target_kind == "client" else None
    if client and not target_code:
        target_code = client["humanCode"]
    reason = b.get("reason") or "cancellation"
    other_map = b.get("other") or {}
    reason_other = b.get("reasonOther") or other_map.get("reason") or other_map.get("deactivation_reason")
    if reason == "other" and not reason_other:
        return {"ok": False, "error": "Motivo Otro requiere texto manual."}
    ids = {"deactivation": gen(con, "deactivation", {"targetKind": target_kind, "targetCode": target_code, "reason": reason})}
    impact = {"keepsHistory": True, "cloudNotTouched": True, "requiresManualReview": True, "targetKind": target_kind}
    con.execute(
        "INSERT INTO DeactivationRequest(id,internalId,humanCode,targetKind,targetCode,reasonCode,reasonOther,status,impact) VALUES(?,?,?,?,?,?,?,?,?)",
        (uid(), ids["deactivation"]["internalId"], ids["deactivation"]["humanCode"], target_kind, target_code, reason, reason_other, "prepared", jd(impact)),
    )
    payload = {"deactivation": {**ids["deactivation"], "targetKind": target_kind, "targetCode": target_code, "reason": reason, "reasonOther": reason_other, "status": "prepared"}, "impact": impact, "source": "local_prepared_not_cloud_deactivated"}
    add_event(con, "deactivation_prepared", "deactivation", ids["deactivation"]["humanCode"], f"Baja preparada: {target_kind} {target_code or ''}", payload)
    return {"ok": True, "mode": "prepared", "message": "Baja preparada localmente; no ejecuta cloud real todavía.", **payload, "counts": _counts(con)}


def _support_case_dict(row):
    if not row:
        return None
    item = dict(row)
    item["scope"] = jl(item.get("scope"))
    item["revision"] = int(item.get("revision") or 0)
    return item


def _support_command_dict(row):
    if not row:
        return None
    item = dict(row)
    item["payload"] = jl(item.get("payload"))
    item["result"] = jl(item.get("result"))
    return item


def support_case_snapshot(con, case_id=None):
    cases = [_support_case_dict(row) for row in con.execute(
        "SELECT * FROM SupportCase ORDER BY updatedAt DESC LIMIT 100"
    ).fetchall()]
    current = None
    if case_id:
        current = _support_case_dict(con.execute(
            "SELECT * FROM SupportCase WHERE id=? OR caseCode=?",
            (case_id, case_id),
        ).fetchone())
    if current is None:
        current = next((item for item in cases if item.get("status") not in {"RESOLVED", "CLOSED"}), cases[0] if cases else None)
    events = []
    evidence = []
    commands = []
    if current:
        current_id = current["id"]
        events = [
            {**dict(row), "payload": jl(row["payload"])}
            for row in con.execute(
                "SELECT * FROM SupportCaseEvent WHERE caseId=? ORDER BY createdAt DESC LIMIT 200",
                (current_id,),
            ).fetchall()
        ]
        evidence = [
            {**dict(row), "payload": jl(row["payload"]), "redacted": bool(row["redacted"])}
            for row in con.execute(
                "SELECT * FROM SupportEvidence WHERE caseId=? ORDER BY createdAt DESC LIMIT 200",
                (current_id,),
            ).fetchall()
        ]
        commands = [
            _support_command_dict(row)
            for row in con.execute(
                "SELECT * FROM SupportCommandRun WHERE caseId=? ORDER BY createdAt DESC LIMIT 100",
                (current_id,),
            ).fetchall()
        ]
    return {
        "currentCase": current,
        "cases": cases,
        "events": events,
        "evidence": evidence,
        "commands": commands,
        "counts": {
            "all": len(cases),
            "critical": sum(1 for item in cases if item.get("severity") == "critical"),
            "blocked": sum(1 for item in cases if item.get("status") == "BLOCKED"),
            "resolvedToday": sum(1 for item in cases if item.get("status") in {"RESOLVED", "CLOSED"} and str(item.get("updatedAt") or "")[:10] == datetime.now(timezone.utc).date().isoformat()),
        },
    }


def create_support_case(con, body):
    client_request_id = str(body.get("clientRequestId") or body.get("idempotencyKey") or "").strip() or None
    if client_request_id:
        existing = con.execute("SELECT * FROM SupportCase WHERE clientRequestId=?", (client_request_id,)).fetchone()
        if existing:
            return {"ok": True, "idempotent": True, "case": _support_case_dict(existing)}
    title = str(body.get("title") or body.get("summary") or body.get("query") or "").strip()
    if not title:
        return {"ok": False, "resultCode": "SUPPORT_CASE_TITLE_REQUIRED", "message": "El caso necesita un título humano."}
    title = title[:240]
    code = gen(con, "case", {"title": title})
    case_id = uid()
    correlation_id = str(body.get("correlationId") or f"support-{uid()}")
    scope = body.get("scope") if isinstance(body.get("scope"), dict) else {}
    con.execute(
        "INSERT INTO SupportCase(id,caseCode,clientRequestId,title,supportCode,severity,status,stage,assignedTo,scope,expectedSourceRevision,revision) VALUES(?,?,?,?,?,?,?,?,?,?,?,1)",
        (
            case_id,
            code["humanCode"],
            client_request_id,
            title,
            body.get("supportCode"),
            body.get("severity") if body.get("severity") in {"info", "warning", "blocked", "critical"} else "warning",
            "CASE_OPEN",
            "SCOPE_RESOLVING",
            body.get("assignedTo"),
            jd(scope),
            body.get("expectedSourceRevision"),
        ),
    )
    con.execute(
        "INSERT INTO SupportCaseEvent(id,caseId,eventType,fromState,toState,correlationId,summary,payload) VALUES(?,?,?,?,?,?,?,?)",
        (uid(), case_id, "case.created", None, "CASE_OPEN", correlation_id, "Caso creado", jd({"scope": scope, "supportCode": body.get("supportCode")})),
    )
    return {
        "ok": True,
        "idempotent": False,
        "correlationId": correlation_id,
        "case": _support_case_dict(con.execute("SELECT * FROM SupportCase WHERE id=?", (case_id,)).fetchone()),
    }


def transition_support_case(con, case_id, expected_revision, *, status=None, stage=None, assigned_to=None, scope=None, event_type="case.transition", summary="Estado actualizado", correlation_id=None, payload=None):
    row = con.execute("SELECT * FROM SupportCase WHERE id=? OR caseCode=?", (case_id, case_id)).fetchone()
    if not row:
        return {"ok": False, "resultCode": "SUPPORT_CASE_NOT_FOUND", "_httpStatus": 404}
    before = _support_case_dict(row)
    current_revision = int(before["revision"])
    if expected_revision is None or int(expected_revision) != current_revision:
        return {
            "ok": False,
            "resultCode": "REVISION_CONFLICT",
            "_httpStatus": 409,
            "expectedRevision": expected_revision,
            "canonicalRevision": current_revision,
            "case": before,
        }
    new_status = status or before["status"]
    new_stage = stage or before["stage"]
    new_scope = scope if isinstance(scope, dict) else before["scope"]
    closed_at = now_iso() if new_status in {"RESOLVED", "CLOSED"} else before.get("closedAt")
    changed = con.execute(
        "UPDATE SupportCase SET status=?,stage=?,assignedTo=?,scope=?,revision=revision+1,updatedAt=CURRENT_TIMESTAMP,closedAt=? WHERE id=? AND revision=?",
        (new_status, new_stage, assigned_to if assigned_to is not None else before.get("assignedTo"), jd(new_scope), closed_at, before["id"], current_revision),
    ).rowcount
    if changed != 1:
        return {"ok": False, "resultCode": "REVISION_CONFLICT", "_httpStatus": 409}
    correlation_id = str(correlation_id or f"support-{uid()}")
    con.execute(
        "INSERT INTO SupportCaseEvent(id,caseId,eventType,fromState,toState,correlationId,summary,payload) VALUES(?,?,?,?,?,?,?,?)",
        (uid(), before["id"], event_type, before["stage"], new_stage, correlation_id, summary[:300], jd(payload or {})),
    )
    after = _support_case_dict(con.execute("SELECT * FROM SupportCase WHERE id=?", (before["id"],)).fetchone())
    return {"ok": True, "correlationId": correlation_id, "beforeRevision": current_revision, "afterRevision": after["revision"], "case": after}


def support_command_by_idempotency(con, idempotency_key):
    if not idempotency_key:
        return None
    return _support_command_dict(con.execute(
        "SELECT * FROM SupportCommandRun WHERE idempotencyKey=?",
        (str(idempotency_key),),
    ).fetchone())


def begin_support_command(con, *, case_id, command_id, idempotency_key, expected_revision, correlation_id, payload, backup_id=None, rollback_id=None):
    previous = support_command_by_idempotency(con, idempotency_key)
    if previous:
        return {"ok": True, "idempotent": True, "commandRun": previous}
    case = None
    if case_id:
        case = _support_case_dict(con.execute("SELECT * FROM SupportCase WHERE id=? OR caseCode=?", (case_id, case_id)).fetchone())
        if not case:
            return {"ok": False, "resultCode": "SUPPORT_CASE_NOT_FOUND", "_httpStatus": 404}
        if expected_revision is None or int(expected_revision) != int(case["revision"]):
            return {"ok": False, "resultCode": "REVISION_CONFLICT", "_httpStatus": 409, "expectedRevision": expected_revision, "canonicalRevision": case["revision"]}
    command_run_id = uid()
    con.execute(
        "INSERT INTO SupportCommandRun(id,caseId,commandId,idempotencyKey,expectedRevision,beforeRevision,status,backupId,rollbackId,correlationId,payload,result) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (command_run_id, case["id"] if case else None, command_id, idempotency_key, expected_revision, case["revision"] if case else None, "RUNNING", backup_id, rollback_id, correlation_id, jd(payload), jd({})),
    )
    return {"ok": True, "idempotent": False, "commandRun": _support_command_dict(con.execute("SELECT * FROM SupportCommandRun WHERE id=?", (command_run_id,)).fetchone())}


def complete_support_command(con, command_run_id, *, status, result, after_revision=None):
    con.execute(
        "UPDATE SupportCommandRun SET status=?,result=?,afterRevision=?,updatedAt=CURRENT_TIMESTAMP WHERE id=?",
        (status, jd(result), after_revision, command_run_id),
    )
    return _support_command_dict(con.execute("SELECT * FROM SupportCommandRun WHERE id=?", (command_run_id,)).fetchone())


def create_support_backup(con, *, case_id, command_id, correlation_id, snapshot, source_revision=None):
    canonical = jd(snapshot)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    backup_id = uid()
    code = gen(con, "backup", {"caseId": case_id, "commandId": command_id})
    con.execute(
        "INSERT INTO SupportRollbackSnapshot(id,backupCode,caseId,commandId,correlationId,sourceRevision,sha256,snapshot) VALUES(?,?,?,?,?,?,?,?)",
        (backup_id, code["humanCode"], case_id, command_id, correlation_id, source_revision, digest, canonical),
    )
    return {"backupId": backup_id, "backupCode": code["humanCode"], "sha256": digest, "rollbackId": f"rollback:{backup_id}"}


def append_support_evidence(con, *, case_id, evidence_type, source, source_revision, correlation_id, payload, observed_at=None):
    canonical = jd(payload)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    evidence_id = uid()
    code = gen(con, "evidence", {"caseId": case_id, "type": evidence_type})
    con.execute(
        "INSERT INTO SupportEvidence(id,evidenceCode,caseId,evidenceType,source,sourceRevision,correlationId,sha256,redacted,payload,observedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (evidence_id, code["humanCode"], case_id, evidence_type, source, source_revision, correlation_id, digest, 1, canonical, observed_at or now_iso()),
    )
    return {"evidenceId": evidence_id, "evidenceCode": code["humanCode"], "sha256": digest, "redacted": True}


def support_store_payload(raw_path, method="GET", body=None):
    ensure_initialized()
    path = urlparse(raw_path).path.rstrip("/")
    payload = body if isinstance(body, dict) else {}
    with db() as con:
        if method == "GET" and path in {"/api/command-center/support/cases", "/api/command-center/support/workspace"}:
            query = parse_qs(urlparse(raw_path).query or "")
            case_id = (query.get("caseId") or [None])[0]
            return {"ok": True, **support_case_snapshot(con, case_id)}
        if method == "POST" and path == "/api/command-center/support/cases":
            out = create_support_case(con, payload)
            con.commit()
            return out
    return {"ok": False, "resultCode": "SUPPORT_STORE_ROUTE_NOT_FOUND", "path": path, "method": method}

def command_center_payload(raw_path, method="GET", body=None):
    ensure_initialized()
    path = urlparse(raw_path).path
    if path.startswith("/api/command-center/support"):
        return support_store_payload(raw_path, method=method, body=body)
    if path.startswith("/api/command-center/billing"):
        with db() as con:
            try:
                out = billing_command(con, path, method, body or {}, gen)
            except BillingError as exc:
                return {"ok": False, "resultCode": exc.code, "error": str(exc), "details": exc.details, "_httpStatus": exc.http_status}
            if method == "POST" and out.get("ok"):
                con.commit()
            return out
    with db() as con:
        if method == "GET" and path in ("/api/command-center", "/api/command-center/bootstrap"):
            return bootstrap(con)
        if method == "GET" and path == "/api/command-center/generate-id":
            q = parse_qs(urlparse(raw_path).query or "")
            x = gen(con, (q.get("kind") or ["item"])[0])
            con.commit()
            return {"ok": True, "identity": x, "counts": _counts(con)}
        routes = {
            "/api/command-center/other": lambda: other(con, body or {}),
            "/api/command-center/draft-client": lambda: draft_client(con, body or {}),
            "/api/command-center/draft-device": lambda: draft_device(con, body or {}),
            "/api/command-center/draft-license": lambda: draft_license(con, body or {}),
            "/api/command-center/draft-deactivation": lambda: draft_deactivation(con, body or {}),
        }
        if method == "POST" and path in routes:
            out = routes[path]()
            con.commit()
            return out
    return {"ok": False, "error": "Unknown command-center route", "path": path, "method": method}

# Governed customer-registration runtime adapter. Installed last so unrelated
# billing/support/licensing behavior remains owned by the original store.
from customer_registration_runtime import install_runtime as _install_customer_registration_runtime
_install_customer_registration_runtime(globals())

if __name__ == "__main__":
    ensure_initialized()
    with db() as con:
        print(json.dumps(bootstrap(con), ensure_ascii=False, indent=2))
