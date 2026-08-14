# -*- coding: utf-8 -*-
"""Governed customer-registration runtime adapter for Prisma Cloud Center.

This module intentionally patches only the customer-registration/catalog slice of
command_center_store. Billing, support, LICFLOW and unrelated Cloud Center code
remain owned by their existing modules.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from customer_registration import (
    catalog_tuples,
    customer_fingerprint,
    load_customer_catalog_config,
    normalize_text,
    recommendation_for,
    validate_customer_payload,
)


SCHEMA_VERSION = 1


def install_runtime(ns: dict[str, Any]) -> None:
    """Install the governed customer-registration behavior into command_center_store."""
    if ns.get("_CUSTOMER_REGISTRATION_RUNTIME_INSTALLED"):
        return
    ns["_CUSTOMER_REGISTRATION_RUNTIME_INSTALLED"] = True

    PathCls = ns.get("Path", Path)
    lab_root = ns["LAB_ROOT"]
    catalog_path = lab_root / "internal" / "config" / "customer_registration_catalogs.canonical.json"
    ns["CUSTOMER_CATALOG_PATH"] = catalog_path

    old_exec_schema = ns["_exec_schema"]
    old_seed_first_customer = ns["_seed_first_customer"]
    old_bootstrap = ns["bootstrap"]
    old_draft_device = ns["draft_device"]
    old_draft_license = ns["draft_license"]
    old_draft_deactivation = ns["draft_deactivation"]

    def _config() -> dict[str, Any]:
        return load_customer_catalog_config(catalog_path)

    def _static_catalogs() -> dict[str, tuple[str, bool, list[tuple[str, str, dict[str, Any]]]]]:
        cfg = _config()
        governed = catalog_tuples(cfg)
        governed["license_plan"] = ("Tipo de licencia", False, ns["_canonical_license_plan_options"]())
        return governed

    def _exec_schema(con):
        old_exec_schema(con)
        con.execute(
            "CREATE TABLE IF NOT EXISTS ClientProfile("
            "id TEXT PRIMARY KEY, clientId TEXT NOT NULL UNIQUE, relationshipStageCode TEXT NOT NULL DEFAULT 'onboarding', "
            "dedupKey TEXT NOT NULL UNIQUE, profileSource TEXT NOT NULL DEFAULT 'operator', acquisitionChannelCode TEXT, "
            "contactRoleCode TEXT, countryCode TEXT, stateCode TEXT, city TEXT, zone TEXT, "
            "createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)"
        )
        con.execute("CREATE INDEX IF NOT EXISTS ClientProfile_acquisition_idx ON ClientProfile(acquisitionChannelCode)")
        con.execute("CREATE INDEX IF NOT EXISTS ClientProfile_relationship_idx ON ClientProfile(relationshipStageCode)")

        migrations = {
            "CommandClient": [
                ("clientRequestId", "clientRequestId TEXT"),
                ("acquisitionChannelCode", "acquisitionChannelCode TEXT"),
                ("contactRoleCode", "contactRoleCode TEXT"),
                ("countryCode", "countryCode TEXT"),
                ("stateCode", "stateCode TEXT"),
                ("city", "city TEXT"),
                ("zone", "zone TEXT"),
            ],
            "ManagedDevice": [
                ("displayAlias", "displayAlias TEXT"),
            ],
        }
        for table, columns in migrations.items():
            present = {str(row[1]) for row in con.execute(f"PRAGMA table_info({table})")}
            for column, ddl in columns:
                if column not in present:
                    con.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")
                    present.add(column)
        con.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS CommandClient_clientRequestId_unique "
            "ON CommandClient(clientRequestId) WHERE clientRequestId IS NOT NULL AND clientRequestId <> ''"
        )

    def _seed_first_customer(con):
        # Existing seed records are never reclassified here. This prevents the runtime
        # from re-inventing vertical/location facts on every boot. A brand-new test DB
        # may use the historical seed creator, then the unverified classifications are
        # removed immediately and remain measurable as unknown.
        existing = con.execute("SELECT id FROM CommandClient WHERE id='client_prisma_original_customer'").fetchone()
        if existing:
            return
        old_seed_first_customer(con)
        con.execute(
            "UPDATE CommandClient SET legalName=NULL, verticalCode=NULL, subverticalCode=NULL, "
            "sizeCode=NULL, operationCode=NULL, cityZoneCode=NULL, acquisitionChannelCode=NULL, "
            "contactRoleCode=NULL, countryCode=NULL, stateCode=NULL, city=NULL, zone=NULL "
            "WHERE id='client_prisma_original_customer'"
        )

    def ensure_initialized():
        with ns["db"]() as con:
            _exec_schema(con)
            cfg = _config()
            governed = _static_catalogs()

            # Explicitly retire historical catalogs such as city_zone while preserving rows.
            for code in cfg.get("retiredCatalogs") or []:
                row = con.execute("SELECT id FROM Catalog WHERE code=?", (code,)).fetchone()
                if row:
                    con.execute("UPDATE Catalog SET mode='retired', updatedAt=CURRENT_TIMESTAMP WHERE code=?", (code,))
                    con.execute("UPDATE CatalogOption SET active=0, updatedAt=CURRENT_TIMESTAMP WHERE catalogId=?", (row["id"],))

            for idx, (code, spec) in enumerate(governed.items(), start=1):
                label, allow_other, options = spec
                catalog_id = f"cat_{code}"
                con.execute(
                    "INSERT OR IGNORE INTO Catalog(id,code,label,mode,allowOther,sortOrder) VALUES(?,?,?,?,?,?)",
                    (catalog_id, code, label, "governed", 1 if allow_other else 0, idx * 10),
                )
                con.execute(
                    "UPDATE Catalog SET label=?, mode='governed', allowOther=?, sortOrder=?, updatedAt=CURRENT_TIMESTAMP WHERE code=?",
                    (label, 1 if allow_other else 0, idx * 10, code),
                )
                con.execute("UPDATE CatalogOption SET active=0, updatedAt=CURRENT_TIMESTAMP WHERE catalogId=?", (catalog_id,))
                for pos, (opt_code, opt_label, metadata) in enumerate(options, start=1):
                    option_id = f"opt_{code}_{opt_code}"
                    con.execute(
                        "INSERT OR IGNORE INTO CatalogOption(id,catalogId,code,label,metadata,active,sortOrder) VALUES(?,?,?,?,?,?,?)",
                        (option_id, catalog_id, opt_code, opt_label, ns["jd"](metadata or {}), 1, pos * 10),
                    )
                    con.execute(
                        "UPDATE CatalogOption SET label=?,metadata=?,active=1,sortOrder=?,updatedAt=CURRENT_TIMESTAMP "
                        "WHERE catalogId=? AND code=?",
                        (opt_label, ns["jd"](metadata or {}), pos * 10, catalog_id, opt_code),
                    )

            plan_options = governed["license_plan"][2]
            canonical_plan_codes = {code for code, _label, _meta in plan_options}
            for opt_code, opt_label, metadata in plan_options:
                con.execute(
                    "INSERT OR IGNORE INTO LicensePlan(id,code,label,tier,maxDevices,maxBranches,modules,rules,active) VALUES(?,?,?,?,?,?,?,?,1)",
                    (
                        f"plan_{opt_code}", opt_code, opt_label, int(metadata.get("tier") or 100),
                        metadata.get("maxDevices"), metadata.get("maxBranches"),
                        ns["jd"](metadata.get("modules") or metadata.get("features") or []), ns["jd"](metadata),
                    ),
                )
                con.execute(
                    "UPDATE LicensePlan SET label=?,tier=?,maxDevices=?,maxBranches=?,modules=?,rules=?,active=1,updatedAt=CURRENT_TIMESTAMP WHERE code=?",
                    (
                        opt_label, int(metadata.get("tier") or 100), metadata.get("maxDevices"), metadata.get("maxBranches"),
                        ns["jd"](metadata.get("modules") or metadata.get("features") or []), ns["jd"](metadata), opt_code,
                    ),
                )
            if canonical_plan_codes:
                placeholders = ",".join("?" for _ in canonical_plan_codes)
                con.execute(f"UPDATE LicensePlan SET active=0 WHERE code NOT IN ({placeholders})", tuple(sorted(canonical_plan_codes)))

            con.execute(
                "INSERT OR IGNORE INTO CloudBridgeStatus(id,mode,cloudOrigin,tokenState,lastCheckedAt,payload) VALUES(?,?,?,?,?,?)",
                ("bridge_local", "local_prepared", "https://app.hitechrts.com", "server_side_or_absent", ns["now_iso"](), ns["jd"]({"note": "Command Center local workflow DB"})),
            )
            _seed_first_customer(con)
            con.commit()

    def catalogs(con):
        out: dict[str, Any] = {}
        for row in con.execute("SELECT * FROM Catalog WHERE COALESCE(mode,'governed') <> 'retired' ORDER BY sortOrder,label"):
            item = dict(row)
            item["allowOther"] = bool(item.get("allowOther"))
            item["options"] = []
            out[item["code"]] = item
        by_id = {item["id"]: item for item in out.values()}
        for row in con.execute("SELECT * FROM CatalogOption WHERE active=1 ORDER BY catalogId,sortOrder,label"):
            opt = dict(row)
            opt["active"] = bool(opt.get("active"))
            opt["metadata"] = ns["jl"](opt.get("metadata"))
            cat = by_id.get(opt["catalogId"])
            if cat:
                cat["options"].append(opt)

        def dynamic(code: str, label: str, rows: list[dict[str, Any]], mapper):
            out[code] = {
                "id": f"dynamic_{code}", "code": code, "label": label, "description": "Selección exacta desde registros locales",
                "allowOther": False, "mode": "dynamic", "options": [mapper(row) for row in rows],
            }

        clients = [dict(row) for row in con.execute(
            "SELECT id,humanCode,displayName,status,verticalCode,operationCode,createdAt FROM CommandClient ORDER BY createdAt DESC LIMIT 200"
        )]
        dynamic("client", "Cliente destino", clients, lambda r: {
            "id": r["id"], "code": r["humanCode"], "label": f"{r['displayName']} · {r['humanCode']}", "active": True,
            "metadata": {"dbId": r["id"], "status": r.get("status"), "vertical": r.get("verticalCode"), "operation": r.get("operationCode")},
        })

        devices = [dict(row) for row in con.execute(
            "SELECT d.id,d.humanCode,d.deviceType,d.roleCode,d.displayAlias,d.status,c.displayName AS clientName "
            "FROM ManagedDevice d LEFT JOIN CommandClient c ON c.id=d.clientId ORDER BY d.createdAt DESC LIMIT 200"
        )]
        dynamic("managed_device", "Dispositivo exacto", devices, lambda r: {
            "id": r["id"], "code": r["humanCode"],
            "label": f"{r.get('displayAlias') or r['humanCode']} · {r.get('clientName') or 'sin cliente'}",
            "active": True, "metadata": {"deviceType": r.get("deviceType"), "roleCode": r.get("roleCode"), "status": r.get("status")},
        })

        licenses = [dict(row) for row in con.execute(
            "SELECT la.id,la.humanCode,la.status,c.displayName AS clientName,lp.label AS planLabel "
            "FROM LicenseAssignment la LEFT JOIN CommandClient c ON c.id=la.clientId "
            "LEFT JOIN LicensePlan lp ON lp.id=la.planId ORDER BY la.createdAt DESC LIMIT 200"
        )]
        dynamic("license_assignment", "Licencia exacta", licenses, lambda r: {
            "id": r["id"], "code": r["humanCode"],
            "label": f"{r.get('clientName') or 'Cliente'} · {r.get('planLabel') or 'Plan'} · {r['humanCode']}",
            "active": True, "metadata": {"status": r.get("status")},
        })
        return out

    def reco(cats, body):
        return recommendation_for(cats, body if isinstance(body, dict) else {})

    def _client_by_code(con, client_code=None):
        code = str(client_code or "").strip()
        if not code:
            return None
        row = con.execute("SELECT * FROM CommandClient WHERE humanCode=? OR id=?", (code, code)).fetchone()
        return dict(row) if row else None

    def _plan_by_code(con, plan_code):
        code = str(plan_code or "").strip()
        if not code:
            return None
        row = con.execute("SELECT * FROM LicensePlan WHERE code=? AND active=1", (code,)).fetchone()
        return dict(row) if row else None

    def _customer_metrics(con):
        def grouped(sql: str):
            return [dict(row) for row in con.execute(sql)]

        seed = con.execute(
            "SELECT legalName,verticalCode,subverticalCode,sizeCode,operationCode,cityZoneCode "
            "FROM CommandClient WHERE id='client_prisma_original_customer'"
        ).fetchone()
        seed_review = 0
        if seed:
            seed_review = 1 if any(seed[key] not in (None, "") for key in ("verticalCode", "subverticalCode", "sizeCode", "operationCode", "cityZoneCode")) else 0
        legacy_city = con.execute("SELECT COUNT(*) FROM CommandClient WHERE cityZoneCode IS NOT NULL AND TRIM(cityZoneCode)<>''").fetchone()[0]
        profiles = con.execute("SELECT COUNT(*) FROM ClientProfile").fetchone()[0]
        return {
            "profiles": profiles,
            "byAcquisition": grouped(
                "SELECT COALESCE(acquisitionChannelCode,'unknown') AS code, COUNT(*) AS count FROM ClientProfile GROUP BY COALESCE(acquisitionChannelCode,'unknown') ORDER BY count DESC,code"
            ),
            "byRelationshipStage": grouped(
                "SELECT COALESCE(relationshipStageCode,'unknown') AS code, COUNT(*) AS count FROM ClientProfile GROUP BY COALESCE(relationshipStageCode,'unknown') ORDER BY count DESC,code"
            ),
            "byVertical": grouped(
                "SELECT COALESCE(verticalCode,'unknown') AS code, COUNT(*) AS count FROM CommandClient WHERE id<>'client_prisma_original_customer' GROUP BY COALESCE(verticalCode,'unknown') ORDER BY count DESC,code"
            ),
            "dataQuality": {
                "seedLegacyClassificationNeedsReview": seed_review,
                "legacyCityZoneValues": int(legacy_city),
                "profilesMeasured": int(profiles),
                "measurementMode": "manual_facts_plus_derived_stage",
            },
        }

    def bootstrap(con):
        payload = old_bootstrap(con)
        cfg = _config()
        payload["customerCatalogSchemaVersion"] = str(cfg.get("schemaVersion") or "1.0.0")
        payload["customerCatalogEffectiveFrom"] = cfg.get("effectiveFrom")
        payload["customerMeasurementPolicy"] = cfg.get("measurementPolicy") or {}
        payload["customerMetrics"] = _customer_metrics(con)
        payload["catalogs"] = catalogs(con)
        return payload

    def other(con, body):
        cats = catalogs(con)
        code = str((body or {}).get("catalog") or "").strip()
        text = str((body or {}).get("manualText") or "").strip()
        if code not in cats:
            return {"ok": False, "resultCode": "CATALOG_INVALID", "error": "Catálogo inválido", "catalog": code}
        if not cats[code].get("allowOther"):
            return {"ok": False, "resultCode": "CATALOG_OTHER_NOT_ALLOWED", "error": "Catálogo no permite Otro", "catalog": code}
        if len(text) < 2:
            return {"ok": False, "resultCode": "CATALOG_OTHER_TEXT_REQUIRED", "error": "Texto Otro obligatorio"}
        normalized = normalize_text(text)[:160]
        catalog_id = cats[code]["id"]
        existing = con.execute(
            "SELECT id,manualText,status FROM CatalogOtherSubmission WHERE catalogId=? AND normalized=? ORDER BY createdAt DESC LIMIT 1",
            (catalog_id, normalized),
        ).fetchone()
        if existing:
            return {"ok": True, "idempotent": True, "id": existing["id"], "catalog": code, "manualText": existing["manualText"], "status": existing["status"]}
        iid = ns["uid"]()
        con.execute(
            "INSERT INTO CatalogOtherSubmission(id,catalogId,manualText,normalized,status,context) VALUES(?,?,?,?,?,?)",
            (iid, catalog_id, text[:160], normalized, "pending_catalog_review", ns["jd"]((body or {}).get("context") or {})),
        )
        result = {"id": iid, "catalog": code, "manualText": text[:160], "status": "pending_catalog_review"}
        ns["add_event"](con, "catalog_other_submitted", "catalog", code, f"Otro pendiente en {code}: {text[:60]}", result)
        return {"ok": True, **result}

    def _existing_client_response(con, row, *, idempotency_reason: str):
        client = dict(row)
        profile_row = con.execute("SELECT * FROM ClientProfile WHERE clientId=?", (client["id"],)).fetchone()
        profile = dict(profile_row) if profile_row else {}
        body = {
            "vertical": client.get("verticalCode"), "businessSize": client.get("sizeCode"),
            "operationMode": client.get("operationCode"),
        }
        return {
            "ok": True, "mode": "prepared", "idempotent": True, "idempotencyReason": idempotency_reason,
            "message": "El cliente ya estaba preparado; no se generaron IDs duplicados.",
            "client": {"dbId": client["id"], "internalId": client["internalId"], "humanCode": client["humanCode"], "displayName": client["displayName"], "status": client["status"]},
            "profile": profile,
            "recommendation": recommendation_for(catalogs(con), body),
            "source": "local_prepared_not_cloud_created",
            "counts": ns["_counts"](con),
        }

    def draft_client(con, body):
        cats = catalogs(con)
        try:
            valid = validate_customer_payload(cats, body or {})
        except ValueError as exc:
            raw = str(exc)
            return {"ok": False, "resultCode": raw.split(":", 1)[0], "error": raw}

        request_id = valid.get("sourceRequestId")
        if request_id:
            existing = con.execute("SELECT * FROM CommandClient WHERE clientRequestId=?", (request_id,)).fetchone()
            if existing:
                return _existing_client_response(con, existing, idempotency_reason="clientRequestId")

        dedup_key = customer_fingerprint(valid)
        existing = con.execute(
            "SELECT c.* FROM CommandClient c JOIN ClientProfile p ON p.clientId=c.id WHERE p.dedupKey=? LIMIT 1",
            (dedup_key,),
        ).fetchone()
        if existing:
            return _existing_client_response(con, existing, idempotency_reason="customerFingerprint")

        recommendation = recommendation_for(cats, valid)
        ids = {
            "client": ns["gen"](con, "client"),
            "contract": ns["gen"](con, "contract"),
            "provisioning": ns["gen"](con, "provisioning"),
        }
        cid = ns["uid"]()
        status = "pending_cloud_activation"
        con.execute(
            "INSERT INTO CommandClient(id,internalId,humanCode,displayName,legalName,status,verticalCode,subverticalCode,sizeCode,operationCode,cityZoneCode,catalogOther,clientRequestId,acquisitionChannelCode,contactRoleCode,countryCode,stateCode,city,zone) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                cid, ids["client"]["internalId"], ids["client"]["humanCode"], valid["displayName"], valid.get("legalName"), status,
                valid.get("vertical"), valid.get("subvertical"), valid.get("businessSize"), valid.get("operationMode"), None,
                ns["jd"](valid.get("other") or {}), request_id, valid.get("acquisitionChannel"), valid.get("contactRole"),
                valid.get("country"), valid.get("state"), valid.get("city"), valid.get("zone"),
            ),
        )
        relationship_stage = "onboarding"
        con.execute(
            "INSERT INTO ClientProfile(id,clientId,relationshipStageCode,dedupKey,profileSource,acquisitionChannelCode,contactRoleCode,countryCode,stateCode,city,zone) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                ns["uid"](), cid, relationship_stage, dedup_key, "operator",
                valid.get("acquisitionChannel"), valid.get("contactRole"), valid.get("country"), valid.get("state"), valid.get("city"), valid.get("zone"),
            ),
        )
        con.execute(
            "INSERT INTO ClientContact(id,clientId,role,name,phone,email) VALUES(?,?,?,?,?,?)",
            (ns["uid"](), cid, valid.get("contactRole") or "primary", valid.get("contactName"), valid.get("phone"), valid.get("email")),
        )
        con.execute(
            "INSERT INTO ClientNote(id,clientId,noteType,text) VALUES(?,?,?,?)",
            (ns["uid"](), cid, "system", "Alta preparada localmente desde Prisma Cloud Ctr. Pendiente activación cloud."),
        )

        other_map = valid.get("other") or {}
        field_catalog = {
            "vertical": "vertical", "subvertical": "subvertical", "operationMode": "operation_mode",
            "acquisitionChannel": "acquisition_channel", "contactRole": "contact_role", "country": "country",
        }
        for field, catalog_code in field_catalog.items():
            if valid.get(field) == "other" and str(other_map.get(field) or "").strip():
                other(con, {"catalog": catalog_code, "manualText": other_map[field], "context": {"field": field, "clientCode": ids["client"]["humanCode"]}})

        profile = {
            "dedupKey": dedup_key,
            "relationshipStageCode": relationship_stage,
            "acquisitionChannelCode": valid.get("acquisitionChannel"),
            "contactRoleCode": valid.get("contactRole"),
            "countryCode": valid.get("country"), "stateCode": valid.get("state"), "city": valid.get("city"), "zone": valid.get("zone"),
        }
        payload = {
            "client": {"dbId": cid, "displayName": valid["displayName"], "status": status, **ids["client"]},
            "profile": profile, "contract": ids["contract"], "provisioning": ids["provisioning"],
            "recommendation": recommendation, "source": "local_prepared_not_cloud_created",
        }
        con.execute(
            "INSERT INTO ProvisioningDraft(id,internalId,humanCode,clientId,kind,status,payload) VALUES(?,?,?,?,?,?,?)",
            (ns["uid"](), ids["provisioning"]["internalId"], ids["provisioning"]["humanCode"], cid, "client_onboarding", "prepared", ns["jd"](payload)),
        )
        ns["add_event"](con, "client_prepared", "client", ids["client"]["humanCode"], f"Cliente preparado: {valid['displayName']}", payload)
        return {"ok": True, "mode": "prepared", "idempotent": False, "message": "Cliente preparado localmente; pendiente endpoint cloud de creación real.", **payload, "counts": ns["_counts"](con)}

    def draft_device(con, body):
        payload = dict(body or {})
        client = _client_by_code(con, payload.get("clientCode"))
        if not client:
            return {"ok": False, "resultCode": "CUSTOMER_SELECTION_REQUIRED", "error": "Selecciona un cliente exacto para el dispositivo."}
        cats = catalogs(con)
        device_type = str(payload.get("deviceType") or "").strip()
        valid_types = {item["code"]: item for item in cats.get("device_type", {}).get("options") or []}
        if device_type not in valid_types:
            return {"ok": False, "resultCode": "DEVICE_TYPE_INVALID", "error": "Tipo de dispositivo inválido."}
        role = str(payload.get("deviceRole") or payload.get("roleCode") or (valid_types[device_type].get("metadata") or {}).get("defaultRole") or "").strip()
        valid_roles = {item["code"]: item for item in cats.get("device_role", {}).get("options") or []}
        role_item = valid_roles.get(role)
        allowed_types = (role_item or {}).get("metadata", {}).get("deviceTypes") or []
        if not role_item or (allowed_types and device_type not in allowed_types):
            return {"ok": False, "resultCode": "DEVICE_ROLE_MISMATCH", "error": "El rol no corresponde al tipo de dispositivo."}
        payload["roleCode"] = role
        payload.pop("operationMode", None)
        out = old_draft_device(con, payload)
        if out.get("ok"):
            alias = str(payload.get("deviceAlias") or "").strip()[:100] or None
            human = (out.get("device") or {}).get("humanCode")
            con.execute("UPDATE ManagedDevice SET displayAlias=?,roleCode=? WHERE humanCode=?", (alias, role, human))
            out["device"]["displayAlias"] = alias
            out["device"]["roleCode"] = role
        return out

    def draft_license(con, body):
        payload = dict(body or {})
        if not _client_by_code(con, payload.get("clientCode")):
            return {"ok": False, "resultCode": "CUSTOMER_SELECTION_REQUIRED", "error": "Selecciona un cliente exacto para la licencia."}
        cats = catalogs(con)
        plan = str(payload.get("plan") or "").strip()
        if plan and plan not in {item["code"] for item in cats.get("license_plan", {}).get("options") or []}:
            return {"ok": False, "resultCode": "LICENSE_PLAN_INVALID", "error": f"Plan fuera del catálogo canónico: {plan}"}
        if not plan:
            payload["plan"] = recommendation_for(cats, payload).get("suggestedPlan")
        return old_draft_license(con, payload)

    def draft_deactivation(con, body):
        payload = dict(body or {})
        target_kind = str(payload.get("targetKind") or "").strip()
        target_code = str(payload.get("targetCode") or payload.get("clientCode") or "").strip()
        allowed = {"client": ("CommandClient",), "license": ("LicenseAssignment",), "device": ("ManagedDevice",)}
        if target_kind not in allowed or not target_code:
            return {"ok": False, "resultCode": "DEACTIVATION_TARGET_REQUIRED", "error": "Selecciona un objetivo exacto."}
        table = allowed[target_kind][0]
        target = con.execute(f"SELECT id,humanCode FROM {table} WHERE humanCode=? OR id=?", (target_code, target_code)).fetchone()
        if not target:
            return {"ok": False, "resultCode": "DEACTIVATION_TARGET_REQUIRED", "error": "El objetivo seleccionado no existe."}
        payload["targetCode"] = target["humanCode"]
        reason = str(payload.get("reason") or "").strip()
        valid_reasons = {item["code"] for item in catalogs(con).get("deactivation_reason", {}).get("options") or []}
        if reason not in valid_reasons:
            return {"ok": False, "resultCode": "DEACTIVATION_REASON_INVALID", "error": "Motivo fuera de catálogo."}
        return old_draft_deactivation(con, payload)

    ns.update({
        "_exec_schema": _exec_schema,
        "_seed_first_customer": _seed_first_customer,
        "ensure_initialized": ensure_initialized,
        "catalogs": catalogs,
        "reco": reco,
        "_client_by_code": _client_by_code,
        "_plan_by_code": _plan_by_code,
        "_customer_metrics": _customer_metrics,
        "bootstrap": bootstrap,
        "other": other,
        "draft_client": draft_client,
        "draft_device": draft_device,
        "draft_license": draft_license,
        "draft_deactivation": draft_deactivation,
        "CUSTOMER_CATALOG_SCHEMA_VERSION": SCHEMA_VERSION,
    })
