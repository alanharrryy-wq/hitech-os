# -*- coding: utf-8 -*-
from __future__ import annotations

import calendar
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


class CommercialContractError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _load_catalog(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CommercialContractError("COMMERCIAL_CATALOG_UNREADABLE", f"No se pudo leer pricing canonico: {exc}") from exc
    if not isinstance(payload, dict):
        raise CommercialContractError("COMMERCIAL_CATALOG_INVALID", "El catalogo canonico no es un objeto JSON valido.")
    return payload


def _as_date(value: Any) -> date:
    if value in (None, ""):
        return date.today()
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError as exc:
        raise CommercialContractError("COMMERCIAL_VALID_FROM_INVALID", "validFrom debe usar YYYY-MM-DD.") from exc


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + int(months)
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _parse_money(value: Any, fallback: int) -> int:
    if value in (None, ""):
        return int(fallback)
    try:
        parsed = int(str(value).strip())
    except Exception as exc:
        raise CommercialContractError("COMMERCIAL_PRICE_INVALID", "agreedPriceMxn debe ser un entero en MXN antes de IVA.") from exc
    if parsed < 0:
        raise CommercialContractError("COMMERCIAL_PRICE_INVALID", "agreedPriceMxn no puede ser negativo.")
    return parsed


def canonical_plan_snapshot(catalog_path: Path, plan_code: str) -> dict[str, Any]:
    payload = _load_catalog(catalog_path)
    policy = payload.get("commercialPolicy") if isinstance(payload.get("commercialPolicy"), dict) else {}
    plans = payload.get("plans") if isinstance(payload.get("plans"), list) else []
    plan = next((item for item in plans if isinstance(item, dict) and item.get("plan") == plan_code), None)
    if not plan or not plan.get("vendible"):
        raise CommercialContractError("COMMERCIAL_PLAN_NOT_SELLABLE", f"El plan {plan_code!r} no es vendible en el catalogo canonico.")
    commercial = plan.get("commercial") if isinstance(plan.get("commercial"), dict) else {}
    prices = commercial.get("listPriceMxn") if isinstance(commercial.get("listPriceMxn"), dict) else {}
    periods = policy.get("periods") if isinstance(policy.get("periods"), dict) else {}
    if not prices or not periods:
        raise CommercialContractError("COMMERCIAL_PRICE_MISSING", f"El plan {plan_code!r} no tiene pricing canonico completo.")
    return {
        "plan": plan_code,
        "planLabel": plan.get("label") or plan_code,
        "priceVersion": commercial.get("priceVersion"),
        "listPriceMxn": {str(key): int(value) for key, value in prices.items()},
        "periods": {str(key): int(value) for key, value in periods.items()},
        "currency": str(policy.get("currency") or "MXN"),
        "taxTreatment": str(policy.get("taxTreatment") or "PLUS_APPLICABLE_IVA"),
        "market": str(policy.get("market") or "MX"),
        "billingScope": str(policy.get("billingScope") or "PER_LICENSE_ASSIGNMENT_WITH_PLAN_LIMITS"),
        "effectiveFrom": policy.get("effectiveFrom"),
    }


def resolve_commercial_terms(
    catalog_path: Path,
    plan_code: str,
    *,
    billing_period: str = "monthly",
    agreed_price_mxn: Any = None,
    price_treatment: str = "canonical_list",
    price_evidence_ref: Any = None,
    commercial_note: Any = None,
    valid_from: Any = None,
) -> dict[str, Any]:
    snapshot = canonical_plan_snapshot(catalog_path, plan_code)
    period = str(billing_period or "monthly").strip().lower()
    if period not in snapshot["periods"] or period not in snapshot["listPriceMxn"]:
        raise CommercialContractError("COMMERCIAL_BILLING_PERIOD_INVALID", f"Periodo comercial no soportado: {period!r}.")

    list_price = int(snapshot["listPriceMxn"][period])
    agreed_price = _parse_money(agreed_price_mxn, list_price)
    treatment = str(price_treatment or "canonical_list").strip().lower()
    allowed_treatments = {"canonical_list", "signed_contract_override", "grandfathered_contract"}
    if treatment not in allowed_treatments:
        raise CommercialContractError("COMMERCIAL_PRICE_TREATMENT_INVALID", f"Tratamiento comercial no soportado: {treatment!r}.")

    evidence_ref = str(price_evidence_ref or "").strip()[:240]
    note = str(commercial_note or "").strip()[:1000]
    if treatment == "canonical_list" and agreed_price != list_price:
        raise CommercialContractError(
            "COMMERCIAL_PRICE_TREATMENT_REQUIRED",
            "Un precio distinto al canon requiere signed_contract_override o grandfathered_contract.",
        )
    if treatment != "canonical_list" and not evidence_ref:
        raise CommercialContractError(
            "COMMERCIAL_PRICE_EVIDENCE_REQUIRED",
            "Un precio contractual excepcional requiere referencia de contrato/recibo/evidencia.",
        )

    start = _as_date(valid_from)
    months = int(snapshot["periods"][period])
    end = _add_months(start, months)
    price_source = {
        "canonical_list": "CANONICAL_LIST_PRICE",
        "signed_contract_override": "SIGNED_CONTRACT_OVERRIDE",
        "grandfathered_contract": "GRANDFATHERED_SIGNED_CONTRACT",
    }[treatment]

    return {
        "planCode": plan_code,
        "planLabel": snapshot["planLabel"],
        "billingPeriod": period,
        "periodMonths": months,
        "currency": snapshot["currency"],
        "listPriceMxn": list_price,
        "agreedPriceMxn": agreed_price,
        "priceVersion": snapshot["priceVersion"],
        "taxTreatment": snapshot["taxTreatment"],
        "market": snapshot["market"],
        "billingScope": snapshot["billingScope"],
        "validFrom": start.isoformat(),
        "validUntil": end.isoformat(),
        "renewalOn": end.isoformat(),
        "grandfathered": treatment == "grandfathered_contract",
        "priceTreatment": treatment,
        "priceSource": price_source,
        "priceEvidenceRef": evidence_ref or None,
        "commercialNote": note or None,
    }


def ensure_commercial_schema(con) -> None:
    con.execute(
        "CREATE TABLE IF NOT EXISTS CommercialContract("
        "id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, "
        "clientId TEXT NOT NULL, licenseAssignmentId TEXT NOT NULL UNIQUE, planCode TEXT NOT NULL, "
        "billingPeriod TEXT NOT NULL, currency TEXT NOT NULL, listPriceMxn INTEGER NOT NULL, "
        "agreedPriceMxn INTEGER NOT NULL, priceVersion TEXT NOT NULL, taxTreatment TEXT NOT NULL, "
        "status TEXT DEFAULT 'prepared', validFrom TEXT NOT NULL, validUntil TEXT NOT NULL, renewalOn TEXT NOT NULL, "
        "grandfathered INTEGER DEFAULT 0, priceTreatment TEXT NOT NULL, priceSource TEXT NOT NULL, "
        "priceEvidenceRef TEXT, commercialNote TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, "
        "updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    con.execute("CREATE INDEX IF NOT EXISTS CommercialContract_clientId_idx ON CommercialContract(clientId, createdAt)")
    con.execute("CREATE INDEX IF NOT EXISTS CommercialContract_plan_period_idx ON CommercialContract(planCode, billingPeriod)")


def insert_commercial_contract(
    con,
    *,
    identity: dict[str, Any],
    client_id: str,
    license_assignment_id: str,
    terms: dict[str, Any],
) -> dict[str, Any]:
    row_id = str(identity.get("internalId") or "").strip()
    human_code = str(identity.get("humanCode") or "").strip()
    if not row_id or not human_code:
        raise CommercialContractError("COMMERCIAL_CONTRACT_IDENTITY_REQUIRED", "El contrato necesita identidad CTR trazable.")
    con.execute(
        "INSERT INTO CommercialContract("
        "id,internalId,humanCode,clientId,licenseAssignmentId,planCode,billingPeriod,currency,listPriceMxn,"
        "agreedPriceMxn,priceVersion,taxTreatment,status,validFrom,validUntil,renewalOn,grandfathered,"
        "priceTreatment,priceSource,priceEvidenceRef,commercialNote) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            row_id,
            row_id,
            human_code,
            client_id,
            license_assignment_id,
            terms["planCode"],
            terms["billingPeriod"],
            terms["currency"],
            terms["listPriceMxn"],
            terms["agreedPriceMxn"],
            terms["priceVersion"],
            terms["taxTreatment"],
            "prepared",
            terms["validFrom"],
            terms["validUntil"],
            terms["renewalOn"],
            1 if terms.get("grandfathered") else 0,
            terms["priceTreatment"],
            terms["priceSource"],
            terms.get("priceEvidenceRef"),
            terms.get("commercialNote"),
        ),
    )
    return {
        **identity,
        **terms,
        "dbId": row_id,
        "licenseAssignmentId": license_assignment_id,
        "status": "prepared",
    }


def count_commercial_contracts(con) -> int:
    return int(con.execute("SELECT COUNT(*) FROM CommercialContract").fetchone()[0])


def list_commercial_contracts(con, limit: int = 50) -> list[dict[str, Any]]:
    rows = con.execute(
        "SELECT cc.id,cc.internalId,cc.humanCode,cc.status,cc.planCode,cc.billingPeriod,cc.currency,"
        "cc.listPriceMxn,cc.agreedPriceMxn,cc.priceVersion,cc.taxTreatment,cc.validFrom,cc.validUntil,"
        "cc.renewalOn,cc.grandfathered,cc.priceTreatment,cc.priceSource,cc.priceEvidenceRef,cc.commercialNote,"
        "cc.createdAt,c.humanCode AS clientCode,c.displayName AS clientName,la.humanCode AS licenseCode "
        "FROM CommercialContract cc "
        "LEFT JOIN CommandClient c ON c.id=cc.clientId "
        "LEFT JOIN LicenseAssignment la ON la.id=cc.licenseAssignmentId "
        "ORDER BY cc.createdAt DESC LIMIT ?",
        (int(limit),),
    ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["grandfathered"] = bool(item.get("grandfathered"))
        out.append(item)
    return out
