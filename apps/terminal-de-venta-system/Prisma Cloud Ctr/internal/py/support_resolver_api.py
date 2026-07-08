from __future__ import annotations

import json
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cloud_saas_api
import command_center_store
import license_ops_api
import licflow4_admin_bridge

SOURCE = "prisma-support-resolver"
SCHEMA_VERSION = "1.0.0"
TERMINAL_ROOT = Path(__file__).resolve().parents[3]
SUPPORT_ROOT = TERMINAL_ROOT / "prisma-support-resolver"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _read_json(relative_path: str) -> Any:
    return json.loads((SUPPORT_ROOT / relative_path).read_text(encoding="utf-8"))


def _codes() -> list[dict[str, Any]]:
    payload = _read_json("catalogs/support-error-codes.json")
    codes = payload.get("codes", [])
    return codes if isinstance(codes, list) else []


def _code_map() -> dict[str, dict[str, Any]]:
    return {str(item.get("code")): item for item in _codes() if isinstance(item, dict) and item.get("code")}


def _actions() -> list[dict[str, Any]]:
    payload = _read_json("catalogs/resolver-actions.json")
    actions = payload.get("actions", [])
    return actions if isinstance(actions, list) else []


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            low = str(key).lower()
            if any(token in low for token in ["token", "secret", "authorization", "cookie", "private", "password"]):
                out[key] = "<redacted>"
            else:
                out[key] = _redact(item)
        return out
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str) and ("authorization:" in value.lower() or "private-key" in value.lower()):
        return "<redacted>"
    return value


def _catalog_payload() -> dict[str, Any]:
    codes = _codes()
    categories = sorted({str(item.get("category")) for item in codes if item.get("category")})
    return {
        "ok": True,
        "schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
        "canonicalRoot": str(SUPPORT_ROOT).replace("\\", "/"),
        "codes": codes,
        "categories": categories,
        "actions": _actions(),
        "surfaceStatusCatalog": _read_json("catalogs/surface-status-catalog.json"),
        "featureGates": _read_json("catalogs/feature-gates.json"),
        "secretsExposed": False,
    }


def _issue_from_code(code: str, surface: str = "cloud-center", evidence: list[dict[str, Any]] | None = None, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    catalog = _code_map().get(code)
    if not catalog:
        catalog = _code_map()["NEEDS_CHATGPT_REVIEW"]
    issue = {
        "code": catalog["code"],
        "category": catalog["category"],
        "severity": catalog["severity"],
        "surface": surface,
        "customerId": None,
        "businessId": None,
        "storeId": None,
        "deviceId": None,
        "terminalId": None,
        "licenseId": None,
        "setupCode": None,
        "humanTitle": catalog["label"],
        "humanExplanation": catalog["customerExplanation"],
        "technicalExplanation": catalog["technicalExplanation"],
        "evidence": evidence or [],
        "detectedBy": SOURCE,
        "canAutoResolve": bool(catalog["autoResolvable"]),
        "canRemoteResolve": bool(catalog["remoteResolvable"]),
        "requiresSetupCode": bool(catalog["requiresSetupCode"]),
        "requiresAdminToken": bool(catalog["requiresAdminToken"]),
        "requiresCloudDeploy": False,
        "requiresD1Migration": code in {"D1_SCHEMA_DRIFT", "D1_REQUIRED_AUDIT_MISSING"},
        "requiresCodex": bool(catalog["requiresCodex"]),
        "requiresOnsite": bool(catalog["requiresOnsite"]),
        "safeActions": catalog["safeActions"],
        "blockedActions": catalog["blockedActions"],
        "recommendedAction": catalog["suggestedResolution"],
        "nextStep": catalog["suggestedResolution"],
        "operatorMessage": catalog["label"],
        "resultCode": catalog["code"],
        "secretsExposed": False,
    }
    if overrides:
        issue.update(overrides)
    return issue


def _surface_status(surface: str, issue: dict[str, Any] | None, runtime: dict[str, Any] | None = None, license_doc: dict[str, Any] | None = None) -> dict[str, Any]:
    runtime = runtime or {}
    license_doc = license_doc or {}
    blocked = bool(issue and issue.get("severity") in {"blocked", "critical"})
    operation = "blocked" if blocked else "ready"
    primary_code = str(issue.get("code")) if issue else "OK"
    visible = str(issue.get("humanTitle")) if issue else f"{surface.title()} lista para operar."
    return {
        "surface": surface,
        "visibleStatus": visible,
        "operationStatus": operation,
        "licenseStatus": str(license_doc.get("state") or license_doc.get("status") or ("blocked" if blocked else "active")),
        "assignmentStatus": str(license_doc.get("assignmentState") or ("wrong_business" if primary_code == "LICENSE_ASSIGNMENT_WRONG_BUSINESS" else "assigned")),
        "customerId": license_doc.get("customerId") or runtime.get("customerId"),
        "businessId": license_doc.get("businessId") or runtime.get("businessId"),
        "storeId": license_doc.get("storeId") or runtime.get("storeId"),
        "deviceId": license_doc.get("deviceId") or runtime.get("deviceId"),
        "terminalId": license_doc.get("terminalId") or runtime.get("terminalId"),
        "licenseId": license_doc.get("licenseId"),
        "plan": license_doc.get("plan"),
        "primaryIssueCode": primary_code,
        "issues": [issue] if issue else [],
        "supportSummary": str(issue.get("humanExplanation")) if issue else "Sin bloqueadores visibles.",
        "nextStep": str(issue.get("nextStep")) if issue else "Continuar operacion normal.",
        "featuresAllowed": 0 if blocked else 1,
        "featuresBlocked": 1 if blocked else 0,
        "lastRefreshAt": license_doc.get("lastRefreshAt"),
        "source": SOURCE,
        "secretsExposed": False,
    }


def _default_wrong_business_case() -> tuple[dict[str, Any], dict[str, Any]]:
    runtime = {
        "businessId": "biz_prisma_rey_lineage_seed",
        "storeId": "store_prisma_rey_centro",
        "terminalId": "term_tablet_pos_001",
        "deviceId": "tablet-pos-source-ready",
    }
    license_doc = {
        "businessId": "biz_demo",
        "customerId": "cust_demo",
        "licenseId": "lic_demo_tablet_pro",
        "plan": "TABLET_PRO",
        "state": "active",
    }
    return runtime, license_doc


def _default_identity_worlds() -> list[dict[str, Any]]:
    return [
        {
            "id": "pos_local_seed",
            "label": "DB POS local seed",
            "source": "pos-local-db/runtime",
            "authorityAction": "use_pos_local_seed",
            "customerId": None,
            "businessId": "biz_prisma_rey_lineage_seed",
            "storeId": "store_prisma_rey_centro",
            "terminalId": "term_tablet_pos_001",
            "deviceId": "tablet-001",
            "risk": "requires compatible license/setup; do not edit signed license manually",
        },
        {
            "id": "installed_demo_license",
            "label": "Licencia local instalada demo/dev",
            "source": "local-license",
            "authorityAction": "blocked_demo_identity",
            "customerId": "cust_demo",
            "businessId": "biz_demo",
            "licenseId": "lic_demo_tablet_pro",
            "plan": "TABLET_PRO",
            "risk": "blocked; demo/dev identity cannot be shipped as customer authority",
        },
        {
            "id": "signed_activation_package",
            "label": "Activación firmada Prisma Original Customer",
            "source": "pc-admin-diagnostic/F:/PRISMA_CTX/LICENSING",
            "authorityAction": "use_signed_activation_package",
            "customerId": "cust_prisma_original_customer",
            "tenantId": "tenant_prisma_original_customer",
            "businessId": "biz_78b3c840796a4a4dad",
            "storeId": "store_00728649f3804a9e82",
            "terminalId": "term_49103c7382d84663a3",
            "licenseId": "lic_prisma_original_customer_001",
            "tabletDeviceId": "tablet_prisma_original_customer_001",
            "pcDeviceId": "pc_prisma_original_customer_001",
            "mobileDeviceId": "mobile_prisma_original_customer_001",
            "plan": "TABLET_PC_MANAGED",
            "risk": "requires POS/local provisioning alignment before Tablet POS can operate",
        },
    ]


def _candidate_customer(body: dict[str, Any]) -> dict[str, Any]:
    for key in ("customer", "adminCustomer", "pcCustomer"):
        item = body.get(key)
        if isinstance(item, dict):
            return item
    for key in ("pcAdmin", "adminDiagnostic", "diagnostic", "context"):
        item = body.get(key)
        if isinstance(item, dict) and isinstance(item.get("customer"), dict):
            return item["customer"]
    return {}


def _identity_worlds_from_body(body: dict[str, Any], runtime: dict[str, Any], license_doc: dict[str, Any]) -> list[dict[str, Any]]:
    worlds = _default_identity_worlds()
    customer = _candidate_customer(body)
    top_business = body.get("businessId")
    if top_business:
        worlds.insert(0, {
            "id": "context_business",
            "label": "Contexto administrativo/consulta",
            "source": "request/context",
            "authorityAction": "context_only",
            "businessId": top_business,
            "customerId": body.get("customerId"),
            "risk": "context source; cannot be selected alone without license/runtime evidence",
        })
    if runtime:
        worlds.insert(0, {
            "id": "runtime_local",
            "label": "Runtime local",
            "source": "runtime.json/device-identity",
            "authorityAction": "use_runtime_local_only_after_license_match",
            "customerId": runtime.get("customerId") or runtime.get("clientId"),
            "businessId": runtime.get("businessId"),
            "storeId": runtime.get("storeId"),
            "terminalId": runtime.get("terminalId"),
            "deviceId": runtime.get("deviceId"),
            "risk": "safe to align only when license and selected authority already match",
        })
    if license_doc:
        worlds.insert(0, {
            "id": "installed_license",
            "label": "Licencia local instalada",
            "source": "license.json",
            "authorityAction": "license_claim_or_refresh_required",
            "customerId": license_doc.get("customerId"),
            "businessId": license_doc.get("businessId"),
            "licenseId": license_doc.get("licenseId"),
            "plan": license_doc.get("plan"),
            "risk": "signed license; never edit manually",
        })
    if customer:
        worlds.insert(0, {
            "id": "pc_admin_customer",
            "label": customer.get("displayName") or "PC/Admin customer context",
            "source": "pc-admin-diagnostic",
            "authorityAction": "setup_claim_or_refresh",
            "customerId": customer.get("customerId"),
            "tenantId": customer.get("tenantId"),
            "businessId": customer.get("businessId"),
            "storeId": customer.get("storeId"),
            "terminalId": customer.get("tabletTerminalId") or customer.get("terminalId"),
            "licenseId": customer.get("licenseId"),
            "tabletDeviceId": customer.get("tabletDeviceId"),
            "pcDeviceId": customer.get("pcDeviceId"),
            "mobileDeviceId": customer.get("mobileDeviceId"),
            "plan": customer.get("planLabel"),
            "risk": "strong technical source; still requires claim/refresh/provisioning before mutation",
        })
    return [world for world in worlds if any(world.get(field) for field in ("customerId", "businessId", "licenseId", "terminalId", "deviceId", "tabletDeviceId"))]


def _identity_reconciliation(body: dict[str, Any], runtime: dict[str, Any], license_doc: dict[str, Any]) -> dict[str, Any]:
    worlds = _identity_worlds_from_body(body, runtime, license_doc)
    business_ids = sorted({str(w.get("businessId")) for w in worlds if w.get("businessId")})
    customer_ids = sorted({str(w.get("customerId")) for w in worlds if w.get("customerId")})
    license_ids = sorted({str(w.get("licenseId")) for w in worlds if w.get("licenseId")})
    split = len(business_ids) > 1 or len(customer_ids) > 1 or ("cust_demo" in customer_ids and len(customer_ids) > 1)
    authority_choices = [
        {
            "id": "setup_claim_or_refresh",
            "label": "Usar Setup Code / License Refresh",
            "safeToApply": False,
            "recommended": True,
            "reason": "Ruta producto: reclama slot/refresca licencia sin editar license.json a mano.",
        },
        {
            "id": "use_pos_local_seed",
            "label": "Usar DB POS local seed",
            "safeToApply": False,
            "recommended": False,
            "reason": "Requiere licencia/setup compatible con biz_prisma_rey_lineage_seed antes de operar.",
        },
        {
            "id": "use_signed_activation_package",
            "label": "Usar paquete firmado externo",
            "safeToApply": False,
            "recommended": False,
            "reason": "Requiere provisionar/alinear POS local con biz_78b3... y terminal term_491... antes de operar.",
        },
    ]
    evidence = []
    for world in worlds:
        for field in ("customerId", "businessId", "licenseId", "storeId", "terminalId", "deviceId", "tabletDeviceId"):
            if world.get(field):
                evidence.append({"label": f"{world['id']}.{field}", "value": world.get(field), "source": world.get("source")})
    return {
        "ok": True,
        "splitDetected": split,
        "primaryIssueCode": "CROSS_SOURCE_IDENTITY_SPLIT" if split else "OK",
        "worlds": worlds,
        "businessIds": business_ids,
        "customerIds": customer_ids,
        "licenseIds": license_ids,
        "authorityChoices": authority_choices,
        "selectedAuthority": body.get("authority") or body.get("selectedAuthority") or None,
        "recommendedAuthority": "setup_claim_or_refresh",
        "evidence": evidence,
        "message": "Hay más de una identidad candidata; elige autoridad antes de mutar." if split else "Las fuentes principales no muestran split de identidad.",
        "secretsExposed": False,
    }


def _detect_issues(body: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    runtime = body.get("runtime") if isinstance(body.get("runtime"), dict) else None
    license_doc = body.get("license") if isinstance(body.get("license"), dict) else None
    if runtime is None and license_doc is None:
        runtime, license_doc = _default_wrong_business_case()
    runtime = runtime or {}
    license_doc = license_doc or {}
    surface = str(body.get("surface") or runtime.get("surface") or "tablet")
    issues: list[dict[str, Any]] = []

    reconciliation = _identity_reconciliation(body, runtime, license_doc)
    requested_code = str(body.get("code") or "")
    if reconciliation.get("splitDetected") or requested_code == "CROSS_SOURCE_IDENTITY_SPLIT":
        issues.append(_issue_from_code(
            "CROSS_SOURCE_IDENTITY_SPLIT",
            surface=surface,
            evidence=reconciliation.get("evidence", []),
            overrides={
                "customerId": next((w.get("customerId") for w in reconciliation["worlds"] if w.get("id") == "pc_admin_customer" and w.get("customerId")), license_doc.get("customerId")),
                "businessId": next((w.get("businessId") for w in reconciliation["worlds"] if w.get("id") == "pc_admin_customer" and w.get("businessId")), license_doc.get("businessId") or runtime.get("businessId")),
                "storeId": runtime.get("storeId"),
                "deviceId": runtime.get("deviceId"),
                "terminalId": runtime.get("terminalId"),
                "licenseId": license_doc.get("licenseId"),
                "reconciliation": reconciliation,
            },
        ))
    if runtime.get("businessId") and license_doc.get("businessId") and runtime.get("businessId") != license_doc.get("businessId"):
        issues.append(_issue_from_code(
            "LICENSE_ASSIGNMENT_WRONG_BUSINESS",
            surface=surface,
            evidence=[
                {"label": "runtime.businessId", "value": runtime.get("businessId"), "source": "diagnose"},
                {"label": "license.businessId", "value": license_doc.get("businessId"), "source": "diagnose"},
            ],
            overrides={
                "customerId": license_doc.get("customerId"),
                "businessId": license_doc.get("businessId"),
                "storeId": runtime.get("storeId"),
                "deviceId": runtime.get("deviceId"),
                "terminalId": runtime.get("terminalId"),
                "licenseId": license_doc.get("licenseId"),
            },
        ))
    joined = json.dumps({"runtime": runtime, "license": license_doc}, sort_keys=True).lower()
    if "demo" in joined:
        issues.append(_issue_from_code(
            "RUNTIME_IDENTITY_DEMO_MODE",
            surface=surface,
            evidence=[{"label": "demo_marker", "value": "present", "source": "diagnose"}],
        ))
    if runtime.get("terminalId") == "term_missing":
        issues.append(_issue_from_code(
            "RUNTIME_TERMINAL_ID_NOT_IN_DB",
            surface=surface,
            evidence=[{"label": "terminalId", "value": runtime.get("terminalId"), "source": "diagnose"}],
        ))
    primary = issues[0] if issues else None
    status = _surface_status(surface, primary, runtime, license_doc)
    if primary and primary.get("reconciliation"):
        status["reconciliation"] = primary["reconciliation"]
    return issues, [status]


def _search_payload(body: dict[str, Any]) -> dict[str, Any]:
    query = str(body.get("query") or body.get("q") or "").strip()
    cloud = cloud_saas_api.summary_payload(allow_admin=False)
    license_ops = license_ops_api.license_ops_payload("/api/license-ops/latest", public=True)
    command = command_center_store.command_center_payload("/api/command-center/bootstrap", method="GET")
    runtime, license_doc = _default_wrong_business_case()
    reconciliation = _identity_reconciliation(body, runtime, license_doc)
    issue_code = "CROSS_SOURCE_IDENTITY_SPLIT" if reconciliation.get("splitDetected") else "LICENSE_ASSIGNMENT_WRONG_BUSINESS"
    issue = _issue_from_code(issue_code, surface="tablet", evidence=reconciliation.get("evidence", []), overrides={"reconciliation": reconciliation})
    source_mode = "cross_source_identity_split" if issue_code == "CROSS_SOURCE_IDENTITY_SPLIT" else "fallback_honest"
    return {
        "ok": True,
        "query": query,
        "sourceMode": source_mode,
        "fallbackHonest": True,
        "reconciliation": reconciliation,
        "authorityChoices": reconciliation.get("authorityChoices", []),
        "customers": [{
            "customer": "Prisma Original Customer",
            "business": "Prisma Rey",
            "email": "support-redacted@example.invalid",
            "phone": "redacted",
            "licenses": 1,
            "devices": 3,
            "status": "blocked-identity-split",
            "primaryIssue": issue["code"],
            "action": "Elegir autoridad"
        }],
        "licenses": [{
            "licenseId": "lic_demo_tablet_pro",
            "customer": "cust_demo",
            "business": "biz_demo",
            "plan": "TABLET_PRO",
            "status": "active",
            "validUntil": "sanitized",
            "assignment": "wrong_business",
            "primaryIssue": "LICENSE_ASSIGNMENT_WRONG_BUSINESS",
            "action": "Diagnosticar"
        }, {
            "licenseId": "lic_prisma_original_customer_001",
            "customer": "cust_prisma_original_customer",
            "business": "biz_78b3c840796a4a4dad",
            "plan": "TABLET_PC_MANAGED",
            "status": "signed-activation-candidate",
            "validUntil": "sanitized",
            "assignment": "candidate_not_installed",
            "primaryIssue": issue["code"],
            "action": "Setup Code / Refresh"
        }],
        "devices": [{
            "deviceId": "tablet-pos-source-ready",
            "surface": "tablet",
            "slot": "Tablet POS Slot",
            "status": "review",
            "customer": "cust_demo",
            "business": "biz_demo",
            "store": "store_prisma_rey_centro",
            "terminal": "term_tablet_pos_001",
            "lastSeenAt": "sanitized",
            "primaryIssue": issue["code"],
            "action": "Elegir autoridad"
        }, {
            "deviceId": "tablet_prisma_original_customer_001",
            "surface": "tablet",
            "slot": "Tablet POS Slot",
            "status": "signed-activation-candidate",
            "customer": "cust_prisma_original_customer",
            "business": "biz_78b3c840796a4a4dad",
            "store": "store_00728649f3804a9e82",
            "terminal": "term_49103c7382d84663a3",
            "lastSeenAt": "sanitized",
            "primaryIssue": issue["code"],
            "action": "Provisionar/alinear POS"
        }],
        "terminals": [{
            "terminalId": "term_tablet_pos_001",
            "name": "Tablet POS 001",
            "store": "store_prisma_rey_centro",
            "active": True,
            "assignedDevice": "tablet-pos-source-ready",
            "cashOpen": None,
            "lastSale": "sanitized",
            "issue": issue["code"],
            "action": "Elegir autoridad"
        }, {
            "terminalId": "term_49103c7382d84663a3",
            "name": "Tablet Caja 1",
            "store": "store_00728649f3804a9e82",
            "active": None,
            "assignedDevice": "tablet_prisma_original_customer_001",
            "cashOpen": None,
            "lastSale": "sanitized",
            "issue": issue["code"],
            "action": "Validar/provisionar"
        }],
        "events": [{
            "date": _now(),
            "event": "support.search",
            "customer": "Prisma Original Customer",
            "device": "tablet-pos-source-ready",
            "result": source_mode,
            "issue": issue["code"],
            "evidence": "sanitized"
        }],
        "snapshots": _redact({"cloud": cloud, "licenseOps": license_ops, "commandCenter": command}),
        "secretsExposed": False,
    }


def _customer_payload(customer_id: str) -> dict[str, Any]:
    search = _search_payload({"query": customer_id})
    return {
        "ok": True,
        "customerId": customer_id,
        "customer360": {
            "commercial": search["customers"][0],
            "contacts": [{"type": "email", "value": "support-redacted@example.invalid"}],
            "licenses": search["licenses"],
            "devices": search["devices"],
            "slots": ["Tablet POS Slot", "PC Admin Slot", "Mobile Companion Slot"],
            "setupCodes": ["redacted-present"],
            "activeIssues": ["LICENSE_ASSIGNMENT_WRONG_BUSINESS"],
            "actions": ["Diagnosticar", "Simular resolucion", "Exportar evidencia"]
        },
        "secretsExposed": False,
    }


def _device_payload(device_id: str) -> dict[str, Any]:
    search = _search_payload({"query": device_id})
    return {
        "ok": True,
        "deviceId": device_id,
        "device360": {
            "summary": search["devices"][0],
            "runtimeExpected": {"businessId": "biz_prisma_rey_lineage_seed", "terminalId": "term_tablet_pos_001"},
            "runtimeActual": {"businessId": "biz_prisma_rey_lineage_seed", "terminalId": "term_tablet_pos_001"},
            "licenseInstalled": {"businessId": "biz_demo", "plan": "TABLET_PRO"},
            "activeIssues": ["LICENSE_ASSIGNMENT_WRONG_BUSINESS"],
            "actions": ["Diagnosticar", "Simular resolucion", "Exportar evidencia"]
        },
        "secretsExposed": False,
    }


def _diagnose_payload(body: dict[str, Any]) -> dict[str, Any]:
    issues, statuses = _detect_issues(body)
    primary = issues[0]["code"] if issues else "OK"
    return {
        "ok": True,
        "resultCode": primary,
        "primaryIssueCode": primary,
        "issues": issues,
        "surfaceStatus": statuses,
        "recommendedAction": issues[0]["recommendedAction"] if issues else "No action required.",
        "secretsExposed": False,
    }


def _simulate_payload(body: dict[str, Any]) -> dict[str, Any]:
    diagnosis = _diagnose_payload(body)
    issue_code = diagnosis["primaryIssueCode"]
    issues = diagnosis.get("issues") if isinstance(diagnosis.get("issues"), list) else []
    reconciliation = next((item.get("reconciliation") for item in issues if isinstance(item, dict) and item.get("reconciliation")), None)

    # recon3b: the Cloud Center UI can request identity reconciliation while the selected
    # code is still LICENSE_ASSIGNMENT_WRONG_BUSINESS. Promote that case to the canonical
    # split response so simulation tells the full story instead of the old runtime-only plan.
    if reconciliation is None:
        runtime = body.get("runtime") if isinstance(body.get("runtime"), dict) else None
        license_doc = body.get("license") if isinstance(body.get("license"), dict) else None
        if runtime is None and license_doc is None:
            runtime, license_doc = _default_wrong_business_case()
        reconciliation = _identity_reconciliation(body, runtime or {}, license_doc or {})

    wants_reconciliation = bool(
        body.get("identityReconciliationRequested")
        or body.get("authority")
        or body.get("selectedAuthority")
        or body.get("authorityStrategy")
        or body.get("code") == "CROSS_SOURCE_IDENTITY_SPLIT"
    )

    if issue_code == "CROSS_SOURCE_IDENTITY_SPLIT" or reconciliation.get("splitDetected") or wants_reconciliation:
        if issue_code != "CROSS_SOURCE_IDENTITY_SPLIT":
            split_issue = _issue_from_code(
                "CROSS_SOURCE_IDENTITY_SPLIT",
                surface=str(body.get("surface") or "tablet"),
                evidence=reconciliation.get("evidence", []),
                overrides={"reconciliation": reconciliation},
            )
            diagnosis = dict(diagnosis)
            diagnosis["resultCode"] = "CROSS_SOURCE_IDENTITY_SPLIT"
            diagnosis["primaryIssueCode"] = "CROSS_SOURCE_IDENTITY_SPLIT"
            diagnosis["issues"] = [split_issue] + issues
            if isinstance(diagnosis.get("surfaceStatus"), list) and diagnosis["surfaceStatus"]:
                diagnosis["surfaceStatus"][0]["primaryIssueCode"] = "CROSS_SOURCE_IDENTITY_SPLIT"
                diagnosis["surfaceStatus"][0]["reconciliation"] = reconciliation

        return {
            "ok": True,
            "resultCode": "IDENTITY_RECONCILIATION_REQUIRED",
            "primaryIssueCode": "CROSS_SOURCE_IDENTITY_SPLIT",
            "dryRun": True,
            "wouldMutate": False,
            "safeToApply": False,
            "safeToApplyReason": "Apply remains blocked because multiple authority candidates exist. Choose Setup Code/Refresh, POS local seed, or signed activation package first.",
            "wouldChange": [],
            "touches": [],
            "authorityChoices": reconciliation.get("authorityChoices", []),
            "selectedAuthority": reconciliation.get("selectedAuthority") or body.get("authority") or body.get("selectedAuthority"),
            "recommendedAuthority": reconciliation.get("recommendedAuthority"),
            "candidateWorlds": reconciliation.get("worlds", []),
            "identityReconciliation": reconciliation,
            "risks": ["signed license is not edited", "no deploy", "no D1 migration", "secretsExposed:false", "no apply until authority route has rollback"],
            "rollbackAvailable": False,
            "validationsAfterAction": ["one authority selected", "runtime/license/POS IDs match selected authority", "surface status recompute"],
            "diagnosis": diagnosis,
            "reconciliation": reconciliation,
            "secretsExposed": False,
        }
    safe = issue_code in {"LICENSE_ASSIGNMENT_WRONG_BUSINESS", "RUNTIME_IDENTITY_DEMO_MODE", "OK"}
    return {
        "ok": True,
        "resultCode": "SIMULATION_READY",
        "dryRun": True,
        "wouldMutate": False,
        "safeToApply": False,
        "safeToApplyReason": "Support Center prepares a plan; real mutation remains confirmation-gated and blocked unless a safe action implements rollback.",
        "wouldChange": ["runtime.json alignment plan", "device-identity.json alignment plan"] if safe and issue_code != "OK" else [],
        "touches": ["Config/runtime.json", "Config/device-identity.json"] if safe and issue_code != "OK" else [],
        "risks": ["signed license is not edited", "no deploy", "no D1 migration", "secretsExposed:false"],
        "rollbackAvailable": False,
        "validationsAfterAction": ["schema parse", "surface status recompute", "support issue no longer blocked"],
        "diagnosis": diagnosis,
        "secretsExposed": False,
    }


def _apply_payload(body: dict[str, Any]) -> dict[str, Any]:
    confirmed = body.get("confirmResolutionAction") is True or body.get("confirm") is True
    if not confirmed:
        return {
            "ok": False,
            "_httpStatus": 409,
            "resultCode": "APPLY_CONFIRMATION_REQUIRED",
            "message": "apply requires confirmResolutionAction:true after simulate.",
            "mutationPerformed": False,
            "secretsExposed": False,
        }
    simulation = _simulate_payload(body)
    if simulation.get("resultCode") == "IDENTITY_RECONCILIATION_REQUIRED":
        return {
            "ok": False,
            "_httpStatus": 409,
            "resultCode": "CROSS_SOURCE_IDENTITY_SPLIT",
            "message": "No se mutó nada: hay varias identidades candidatas. Elige autoridad y usa Setup Code/Refresh o una ruta con rollback.",
            "mutationPerformed": False,
            "simulation": simulation,
            "secretsExposed": False,
        }
    return {
        "ok": False,
        "_httpStatus": 409,
        "resultCode": "RESOLUTION_NOT_SAFE_REMOTE",
        "message": "No real mutation was performed because rollback-safe apply is not available for this case yet.",
        "mutationPerformed": False,
        "simulation": simulation,
        "secretsExposed": False,
    }


def _export_case_payload(body: dict[str, Any]) -> dict[str, Any]:
    diagnosis = _diagnose_payload(body)
    case_id = f"support-case-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    return {
        "ok": True,
        "resultCode": "SUPPORT_CASE_EXPORT_READY",
        "caseId": case_id,
        "files": [
            "support-case.json",
            "support-case.md",
            "issues.json",
            "surface-status.json",
            "customer-summary.json",
            "device-summary.json",
            "resolution-plan.json",
            "redaction-report.json",
            "CONTINUATION.md"
        ],
        "diagnosis": diagnosis,
        "redaction": {
            "tokens": "excluded",
            "privateKeys": "excluded",
            "authorizationHeaders": "excluded",
            "rawDumps": "excluded",
            "secretsExposed": False
        },
        "secretsExposed": False,
    }


def support_payload(path: str, method: str = "GET", body: dict[str, Any] | None = None, local_request: bool = False) -> dict[str, Any]:
    body = body or {}
    parsed = urllib.parse.urlparse(path)
    route = parsed.path
    if method == "GET" and route in {"/api/support/catalog", "/api/support/codes"}:
        payload = _catalog_payload()
        if route.endswith("/codes"):
            return {"ok": True, "codes": payload["codes"], "categories": payload["categories"], "secretsExposed": False}
        return payload
    if method == "GET" and route.startswith("/api/support/customer/"):
        return _customer_payload(urllib.parse.unquote(route.rsplit("/", 1)[-1]))
    if method == "GET" and route.startswith("/api/support/device/"):
        return _device_payload(urllib.parse.unquote(route.rsplit("/", 1)[-1]))
    if method == "POST" and route == "/api/support/search":
        return _search_payload(body)
    if method == "POST" and route == "/api/support/diagnose":
        return _diagnose_payload(body)
    if method == "POST" and route == "/api/support/resolve/simulate":
        return _simulate_payload(body)
    if method == "POST" and route == "/api/support/resolve/apply":
        return _apply_payload(body)
    if method == "POST" and route == "/api/support/export-case":
        return _export_case_payload(body)
    if method == "GET" and route == "/api/support/bridge-status":
        return {"ok": True, "bridge": licflow4_admin_bridge.diagnostics_payload(), "secretsExposed": False}
    return {"ok": False, "_httpStatus": 404, "resultCode": "SUPPORT_ROUTE_NOT_FOUND", "route": route, "secretsExposed": False}


# === PRISMA RECON4 SETUP CLAIM OR REFRESH GUIDED START ===

from copy import deepcopy as _recon4_deepcopy


def _recon4_dict(value):
    return value if isinstance(value, dict) else {}


def _recon4_list(value):
    return value if isinstance(value, list) else []


def _recon4_selected_authority(payload, result=None):
    payload = _recon4_dict(payload)
    result = _recon4_dict(result)
    selected = (
        payload.get("selectedAuthority")
        or payload.get("authorityStrategy")
        or payload.get("authority")
        or result.get("selectedAuthority")
        or result.get("recommendedAuthority")
        or _recon4_dict(result.get("identityReconciliation")).get("selectedAuthority")
        or _recon4_dict(result.get("reconciliation")).get("selectedAuthority")
    )
    return selected or "setup_claim_or_refresh"


def _recon4_reconciliation_from(result):
    result = _recon4_dict(result)
    rec = result.get("identityReconciliation") or result.get("reconciliation")
    if isinstance(rec, dict):
        return rec
    diagnosis = _recon4_dict(result.get("diagnosis"))
    for issue in _recon4_list(diagnosis.get("issues")):
        if isinstance(issue, dict) and isinstance(issue.get("reconciliation"), dict):
            return issue["reconciliation"]
    for surface in _recon4_list(diagnosis.get("surfaceStatus")):
        if isinstance(surface, dict) and isinstance(surface.get("reconciliation"), dict):
            return surface["reconciliation"]
    return {}


def _recon4_find_world(rec, world_id):
    for world in _recon4_list(_recon4_dict(rec).get("worlds")):
        if isinstance(world, dict) and world.get("id") == world_id:
            return world
    return {}


def _recon4_guide(result, payload=None):
    payload = _recon4_dict(payload)
    rec = _recon4_reconciliation_from(result)
    pc = _recon4_find_world(rec, "pc_admin_customer") or _recon4_find_world(rec, "signed_activation_package")
    installed = _recon4_find_world(rec, "installed_license") or _recon4_find_world(rec, "installed_demo_license")
    runtime = _recon4_find_world(rec, "runtime_local")
    pos = _recon4_find_world(rec, "pos_local_seed")
    selected = _recon4_selected_authority(payload, result)
    return {
        "id": "setup_claim_or_refresh",
        "title": "Setup Code / License Refresh guiado",
        "stage": "input_required",
        "selectedAuthority": selected,
        "recommendedAuthority": "setup_claim_or_refresh",
        "primaryIssueCode": "CROSS_SOURCE_IDENTITY_SPLIT",
        "resultCode": "SETUP_CLAIM_OR_REFRESH_GUIDED",
        "humanExplanation": "La ruta producto requiere reclamar el slot con Setup Code o refrescar licencia; no edita license.json firmado a mano.",
        "technicalExplanation": "Use Customer Setup / Device Claim / License Refresh to replace demo/local license state with a signed assignment matching the selected authority.",
        "requiredInputs": [
            {"id": "setupCode", "label": "Setup Code del cliente correcto", "required": True, "secret": False},
            {"id": "surface", "label": "Surface", "required": True, "expected": "tablet"},
            {"id": "deviceId", "label": "Device ID local", "required": True, "expected": runtime.get("deviceId") or pc.get("tabletDeviceId")},
            {"id": "operatorConfirmation", "label": "Confirmación humana", "required": True},
        ],
        "preflightChecks": [
            "setup code exists and belongs to selected customer",
            "surface is allowed by plan",
            "tablet slot is available or matches this device",
            "signed refreshed license verifies before installation",
            "runtime/device identity target IDs are derived from signed claim result",
            "POS local DB alignment is validated before enabling Tablet POS",
        ],
        "blockedUntil": [
            "setupCode or refresh source is provided",
            "signed refreshed license is verified",
            "rollback-safe local write plan exists",
            "post-action surface status recompute is available",
        ],
        "candidateAuthority": {
            "customerId": pc.get("customerId"),
            "tenantId": pc.get("tenantId"),
            "businessId": pc.get("businessId"),
            "storeId": pc.get("storeId"),
            "terminalId": pc.get("terminalId"),
            "licenseId": pc.get("licenseId"),
            "tabletDeviceId": pc.get("tabletDeviceId"),
            "plan": pc.get("plan"),
        },
        "currentlyInstalled": {
            "customerId": installed.get("customerId"),
            "businessId": installed.get("businessId"),
            "licenseId": installed.get("licenseId"),
            "plan": installed.get("plan"),
        },
        "runtimeLocal": {
            "businessId": runtime.get("businessId"),
            "storeId": runtime.get("storeId"),
            "terminalId": runtime.get("terminalId"),
            "deviceId": runtime.get("deviceId"),
        },
        "posLocalSeed": {
            "businessId": pos.get("businessId"),
            "storeId": pos.get("storeId"),
            "terminalId": pos.get("terminalId"),
            "deviceId": pos.get("deviceId"),
        },
        "safeActionsNow": ["diagnose", "simulate", "export_evidence", "copy_support_summary"],
        "futureApplyAction": "setup_claim_or_refresh_apply_with_backup_rollback",
        "blockedActions": [
            "edit_signed_license",
            "blind_manual_license_rewrite",
            "claim_without_setup_code",
            "overwrite_runtime_without_verified_license",
            "merge_worlds_without_pos_db_validation",
        ],
        "mutationPerformed": False,
        "wouldMutate": False,
        "safeToApply": False,
        "rollbackAvailable": False,
        "secretsExposed": False,
    }


def _recon4_enrich_simulation(result, payload=None):
    payload = _recon4_dict(payload)
    selected = _recon4_selected_authority(payload, result)
    if selected != "setup_claim_or_refresh":
        return result
    out = _recon4_deepcopy(_recon4_dict(result))
    guide = _recon4_guide(out, payload)
    out["ok"] = True
    out["resultCode"] = "SETUP_CLAIM_OR_REFRESH_GUIDED"
    out["baseResultCode"] = _recon4_dict(result).get("resultCode")
    out["primaryIssueCode"] = "CROSS_SOURCE_IDENTITY_SPLIT"
    out["dryRun"] = True
    out["wouldMutate"] = False
    out["safeToApply"] = False
    out["safeToApplyReason"] = "Setup Code / License Refresh is selected, but apply remains blocked until setup code or refresh source, signed-license verification, backup and rollback-safe local write plan exist."
    out["wouldChange"] = []
    out["touches"] = []
    out["guidedResolution"] = guide
    risks = list(_recon4_list(out.get("risks")))
    for risk in [
        "signed license is not edited",
        "setup claim/refresh must produce signed replacement license",
        "no apply until rollback-safe write path exists",
        "secretsExposed:false",
    ]:
        if risk not in risks:
            risks.append(risk)
    out["risks"] = risks
    out["rollbackAvailable"] = False
    validations = list(_recon4_list(out.get("validationsAfterAction")))
    for check in [
        "setup code belongs to selected customer",
        "signed refreshed license verifies",
        "runtime/license/POS IDs match selected authority",
        "surface status recompute",
    ]:
        if check not in validations:
            validations.append(check)
    out["validationsAfterAction"] = validations
    out["secretsExposed"] = False
    return out


def _recon4_apply_guard(result, payload=None):
    payload = _recon4_dict(payload)
    selected = _recon4_selected_authority(payload, result)
    if selected != "setup_claim_or_refresh":
        return result
    sim = _recon4_enrich_simulation(_recon4_dict(result).get("simulation") or result, payload)
    return {
        "ok": False,
        "resultCode": "SETUP_CLAIM_OR_REFRESH_INPUT_REQUIRED",
        "primaryIssueCode": "CROSS_SOURCE_IDENTITY_SPLIT",
        "message": "No mutation was performed. Setup Code / License Refresh requires setupCode/refresh source, signed-license verification, backup, rollback and post-action validations before apply.",
        "mutationPerformed": False,
        "requiresSetupCode": True,
        "requiresRefreshSource": True,
        "requiresRollbackSafePlan": True,
        "simulation": sim,
        "guidedResolution": sim.get("guidedResolution"),
        "secretsExposed": False,
    }


try:
    _recon4_original_support_payload = support_payload
except NameError:  # pragma: no cover
    _recon4_original_support_payload = None


def support_payload(path, method="GET", body=None, query=None, *args, **kwargs):
    payload = body if isinstance(body, dict) else {}
    path_text = str(path or "")
    if path_text.endswith("/api/support/authority/guide") or path_text.endswith("/support/authority/guide"):
        base = {}
        if _recon4_original_support_payload:
            try:
                base = _recon4_original_support_payload("/api/support/resolve/simulate", method="POST", body=payload, query=query)
            except TypeError:
                base = _recon4_original_support_payload("/api/support/resolve/simulate", "POST", payload, query)
            except Exception:
                base = {}
        enriched = _recon4_enrich_simulation(base, payload)
        return {"ok": True, "resultCode": "SETUP_CLAIM_OR_REFRESH_GUIDED", "guidedResolution": enriched.get("guidedResolution"), "simulation": enriched, "secretsExposed": False}
    if not _recon4_original_support_payload:
        return {"ok": False, "resultCode": "SUPPORT_PAYLOAD_NOT_AVAILABLE", "secretsExposed": False}
    try:
        result = _recon4_original_support_payload(path, method=method, body=body, query=query, *args, **kwargs)
    except TypeError:
        result = _recon4_original_support_payload(path, method, body, query)
    if path_text.endswith("/api/support/resolve/simulate") or path_text.endswith("/support/resolve/simulate"):
        return _recon4_enrich_simulation(result, payload)
    if path_text.endswith("/api/support/resolve/apply") or path_text.endswith("/support/resolve/apply"):
        selected = _recon4_selected_authority(payload, result)
        if selected == "setup_claim_or_refresh":
            return _recon4_apply_guard(result, payload)
    return result
# === PRISMA RECON4 SETUP CLAIM OR REFRESH GUIDED END ===

# === PRISMA RECON5 SETUP CLAIM APPLY PREFLIGHT START ===
# recon5: guarded Setup Code / License Refresh apply planner.
# It does NOT edit signed license.json and does NOT mutate local runtime.
# It turns the Resolve button into a rollback-safe preflight contract until a
# signed refresh source and local write plan are available.

def _recon5_dict(value):
    return value if isinstance(value, dict) else {}


def _recon5_list(value):
    return value if isinstance(value, list) else []


def _recon5_selected_authority(payload, result=None):
    payload = _recon5_dict(payload)
    result = _recon5_dict(result)
    rec = _recon5_dict(result.get("identityReconciliation") or result.get("reconciliation"))
    selected = (
        payload.get("selectedAuthority")
        or payload.get("authorityStrategy")
        or payload.get("authority")
        or result.get("selectedAuthority")
        or result.get("recommendedAuthority")
        or rec.get("selectedAuthority")
        or rec.get("recommendedAuthority")
    )
    return selected or "setup_claim_or_refresh"


def _recon5_find_world(rec, world_id):
    for world in _recon5_list(_recon5_dict(rec).get("worlds")):
        if isinstance(world, dict) and world.get("id") == world_id:
            return world
    return {}


def _recon5_reconciliation_from(result):
    result = _recon5_dict(result)
    rec = result.get("identityReconciliation") or result.get("reconciliation")
    if isinstance(rec, dict):
        return rec
    diagnosis = _recon5_dict(result.get("diagnosis"))
    for issue in _recon5_list(diagnosis.get("issues")):
        if isinstance(issue, dict) and isinstance(issue.get("reconciliation"), dict):
            return issue["reconciliation"]
    for surface in _recon5_list(diagnosis.get("surfaceStatus")):
        if isinstance(surface, dict) and isinstance(surface.get("reconciliation"), dict):
            return surface["reconciliation"]
    return {}


def _recon5_bool(value):
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "si", "sí", "confirmed", "confirmado"}
    return False


def _recon5_setup_code(payload):
    payload = _recon5_dict(payload)
    raw = payload.get("setupCode") or payload.get("setup_code") or payload.get("refreshCode") or ""
    return str(raw).strip()


def _recon5_mask_code(value):
    value = str(value or "").strip()
    if not value:
        return ""
    if len(value) <= 8:
        return "redacted-present"
    return value[:4] + "…" + value[-4:]


def _recon5_apply_plan(payload, simulation):
    payload = _recon5_dict(payload)
    simulation = _recon5_dict(simulation)
    guide = _recon5_dict(simulation.get("guidedResolution"))
    rec = _recon5_reconciliation_from(simulation)
    pc = _recon5_find_world(rec, "pc_admin_customer") or _recon5_find_world(rec, "signed_activation_package") or _recon5_dict(guide.get("candidateAuthority"))
    installed = _recon5_find_world(rec, "installed_license") or _recon5_find_world(rec, "installed_demo_license") or _recon5_dict(guide.get("currentlyInstalled"))
    runtime = _recon5_find_world(rec, "runtime_local") or _recon5_dict(guide.get("runtimeLocal"))
    pos = _recon5_find_world(rec, "pos_local_seed") or _recon5_dict(guide.get("posLocalSeed"))
    setup_code = _recon5_setup_code(payload)
    return {
        "id": "setup_claim_or_refresh_apply_with_backup_rollback",
        "stage": "ready_for_signed_refresh" if setup_code else "input_required",
        "selectedAuthority": _recon5_selected_authority(payload, simulation),
        "primaryIssueCode": "CROSS_SOURCE_IDENTITY_SPLIT",
        "setupCodePresent": bool(setup_code),
        "setupCodePreview": _recon5_mask_code(setup_code),
        "mutationPerformed": False,
        "wouldMutate": False,
        "safeToApply": False,
        "rollbackAvailable": False,
        "candidateAuthority": {
            "customerId": pc.get("customerId"),
            "tenantId": pc.get("tenantId"),
            "businessId": pc.get("businessId"),
            "storeId": pc.get("storeId"),
            "terminalId": pc.get("terminalId"),
            "licenseId": pc.get("licenseId"),
            "tabletDeviceId": pc.get("tabletDeviceId"),
            "plan": pc.get("plan"),
        },
        "currentlyInstalled": {
            "customerId": installed.get("customerId"),
            "businessId": installed.get("businessId"),
            "licenseId": installed.get("licenseId"),
            "plan": installed.get("plan"),
        },
        "runtimeLocal": {
            "businessId": runtime.get("businessId"),
            "storeId": runtime.get("storeId"),
            "terminalId": runtime.get("terminalId"),
            "deviceId": runtime.get("deviceId"),
        },
        "posLocalSeed": {
            "businessId": pos.get("businessId"),
            "storeId": pos.get("storeId"),
            "terminalId": pos.get("terminalId"),
            "deviceId": pos.get("deviceId"),
        },
        "requiredBeforeMutation": [
            "cloud/customer setup confirms setupCode belongs to candidate customer",
            "device claim or license refresh returns signed replacement license",
            "signed refreshed license verifies against public key before install",
            "backup captures current license/runtime/device identity files",
            "rollback script restores exact previous files",
            "POS local DB alignment is validated before enabling Tablet POS",
            "surface status recompute returns no blocked identity issue",
        ],
        "localWritePlan": [
            {"path": "Config/license.json", "source": "signed refreshed license", "operation": "replace only after signature verification"},
            {"path": "Config/runtime.json", "source": "signed claim result", "operation": "align customer/business/store/terminal/device"},
            {"path": "Config/device-identity.json", "source": "signed claim result", "operation": "align claimed device identity"},
            {"path": "POS local DB", "source": "validation only", "operation": "no blind merge; validate terminal/store before enabling POS"},
        ],
        "rollbackPlan": [
            "copy current local identity/license files to timestamped backup",
            "write rollback_manifest.json with sha256 before/after",
            "on failure restore all touched files and recompute support status",
            "never restore or expose private keys/tokens",
        ],
        "postChecks": [
            "license signature verifies",
            "license/customer/business matches selected authority",
            "runtime/customer/business/store/terminal/device matches license",
            "POS terminal/store exists and is locally operable",
            "support surfaceStatus no longer reports CROSS_SOURCE_IDENTITY_SPLIT",
        ],
        "blockedActions": [
            "edit_signed_license",
            "blind_manual_license_rewrite",
            "claim_without_setup_code",
            "overwrite_runtime_without_verified_license",
            "merge_worlds_without_pos_db_validation",
        ],
        "secretsExposed": False,
    }


def _recon5_apply_response(payload, base_result=None):
    payload = _recon5_dict(payload)
    selected = _recon5_selected_authority(payload, base_result)
    if selected != "setup_claim_or_refresh":
        return base_result or {"ok": False, "resultCode": "UNSUPPORTED_AUTHORITY", "mutationPerformed": False, "secretsExposed": False}

    confirm = _recon5_bool(payload.get("confirmResolutionAction")) or _recon5_bool(payload.get("confirm"))
    setup_code = _recon5_setup_code(payload)

    try:
        simulation = _recon5_previous_support_payload("/api/support/resolve/simulate", method="POST", body=payload)
    except TypeError:
        simulation = _recon5_previous_support_payload("/api/support/resolve/simulate", "POST", payload)
    except Exception:
        simulation = _recon5_dict(base_result).get("simulation") or _recon5_dict(base_result)

    plan = _recon5_apply_plan(payload, simulation)
    if not confirm:
        return {
            "ok": False,
            "_httpStatus": 409,
            "resultCode": "APPLY_CONFIRMATION_REQUIRED",
            "primaryIssueCode": "CROSS_SOURCE_IDENTITY_SPLIT",
            "message": "Resolver problema requiere confirmResolutionAction:true y preflight de Setup Code / License Refresh.",
            "mutationPerformed": False,
            "simulation": simulation,
            "applyPlan": plan,
            "secretsExposed": False,
        }

    if not setup_code:
        return {
            "ok": False,
            "_httpStatus": 409,
            "resultCode": "SETUP_CLAIM_OR_REFRESH_INPUT_REQUIRED",
            "primaryIssueCode": "CROSS_SOURCE_IDENTITY_SPLIT",
            "message": "Setup Code requerido. No se mutó nada.",
            "mutationPerformed": False,
            "requiresSetupCode": True,
            "requiresSignedRefresh": True,
            "requiresRollbackSafePlan": True,
            "simulation": simulation,
            "guidedResolution": _recon5_dict(simulation).get("guidedResolution"),
            "applyPlan": plan,
            "secretsExposed": False,
        }

    return {
        "ok": True,
        "resultCode": "SETUP_CLAIM_OR_REFRESH_PREFLIGHT_READY",
        "primaryIssueCode": "CROSS_SOURCE_IDENTITY_SPLIT",
        "message": "Preflight listo: Setup Code presente. No se mutó nada; falta ejecutar claim/refresh real, verificar licencia firmada y activar rollback-safe write plan.",
        "mutationPerformed": False,
        "dryRun": True,
        "wouldMutate": False,
        "safeToApply": False,
        "safeToApplyReason": "Setup Code presente, pero la escritura local permanece bloqueada hasta obtener licencia refrescada firmada y validar rollback.",
        "simulation": simulation,
        "guidedResolution": _recon5_dict(simulation).get("guidedResolution"),
        "applyPlan": plan,
        "nextBackendAction": "claim_or_refresh_setup_code_and_verify_signed_license",
        "secretsExposed": False,
    }


try:
    _recon5_previous_support_payload = support_payload
except NameError:  # pragma: no cover
    _recon5_previous_support_payload = None


def support_payload(path, method="GET", body=None, query=None, *args, **kwargs):
    payload = body if isinstance(body, dict) else {}
    path_text = str(path or "")
    if not _recon5_previous_support_payload:
        return {"ok": False, "resultCode": "SUPPORT_PAYLOAD_NOT_AVAILABLE", "secretsExposed": False}
    if path_text.endswith("/api/support/resolve/apply-plan") or path_text.endswith("/support/resolve/apply-plan"):
        return _recon5_apply_response({**payload, "confirmResolutionAction": True})
    try:
        result = _recon5_previous_support_payload(path, method=method, body=body, query=query, *args, **kwargs)
    except TypeError:
        result = _recon5_previous_support_payload(path, method, body, query)
    if path_text.endswith("/api/support/resolve/apply") or path_text.endswith("/support/resolve/apply"):
        if _recon5_selected_authority(payload, result) == "setup_claim_or_refresh":
            return _recon5_apply_response(payload, result)
    if path_text.endswith("/api/support/resolve/simulate") or path_text.endswith("/support/resolve/simulate"):
        out = _recon5_dict(result)
        if _recon5_selected_authority(payload, out) == "setup_claim_or_refresh":
            try:
                out = dict(out)
                guide = _recon5_dict(out.get("guidedResolution"))
                guide["futureApplyAction"] = "setup_claim_or_refresh_apply_with_backup_rollback"
                out["guidedResolution"] = guide
                out["recon5ApplyPlanReady"] = True
                risks = list(_recon5_list(out.get("risks")))
                for risk in ["apply preflight requires setup code", "actual local writes remain blocked until signed refresh verifies"]:
                    if risk not in risks:
                        risks.append(risk)
                out["risks"] = risks
            except Exception:
                pass
        return out
    return result
# === PRISMA RECON5 SETUP CLAIM APPLY PREFLIGHT END ===
