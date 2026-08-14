# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Callable

from cfdi_gateway import (
    FiscalGatewayError,
    build_income_cfdi_draft,
    build_payment_complement_draft,
    gateway_status,
    normalize_payment_form,
    validate_cancellation_request,
    validate_cfdi_uuid,
    validate_sha256,
)


class BillingError(ValueError):
    def __init__(self, code: str, message: str, *, http_status: int = 400, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.http_status = int(http_status)
        self.details = details or {}


DEFAULT_TAX_RATE_BPS = 1600
DEFAULT_TAX_RATE_SOURCE = "LIVA_ART_1_GENERAL_RATE_OPERATOR_CONFIRMED"
DEFAULT_DUE_POLICY = "PREPAID_PERIOD_START"
BILLING_MODEL_VERSION = "2026-08-14.v1"

CHARGE_OPEN_STATES = {"open", "partially_paid", "past_due"}
FISCAL_ACTIVE_STATES = {"draft_blocked", "ready_to_stamp", "external_stamped", "cancel_requested", "cancellation_rejected"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _today(value: Any = None) -> date:
    if value in (None, ""):
        return date.today()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError as exc:
        raise BillingError("BILLING_DATE_INVALID", "La fecha debe usar YYYY-MM-DD.") from exc


def _canonical_json(value: Any) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_load(value: Any, fallback: Any = None) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if value in (None, ""):
        return {} if fallback is None else fallback
    try:
        return json.loads(str(value))
    except Exception:
        return {} if fallback is None else fallback


def _sha256_payload(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _money_to_cents(value: Any, field: str = "amountMxn") -> int:
    if isinstance(value, bool) or value in (None, ""):
        raise BillingError("BILLING_AMOUNT_REQUIRED", f"{field} es obligatorio.")
    try:
        amount = Decimal(str(value).strip()).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise BillingError("BILLING_AMOUNT_INVALID", f"{field} debe ser un importe MXN valido con maximo dos decimales.") from exc
    if amount <= 0:
        raise BillingError("BILLING_AMOUNT_INVALID", f"{field} debe ser mayor a cero.")
    return int((amount * 100).to_integral_value(rounding=ROUND_HALF_UP))


def _validate_rate_bps(value: Any) -> int:
    try:
        rate = int(value)
    except Exception as exc:
        raise BillingError("BILLING_TAX_RATE_INVALID", "taxRateBps debe ser un entero de puntos base.") from exc
    if rate < 0 or rate > 10000:
        raise BillingError("BILLING_TAX_RATE_INVALID", "taxRateBps debe estar entre 0 y 10000.")
    return rate


def _tax_cents(subtotal_cents: int, rate_bps: int) -> int:
    return int((Decimal(int(subtotal_cents)) * Decimal(int(rate_bps)) / Decimal(10000)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def _client(con: sqlite3.Connection, code: Any) -> dict[str, Any]:
    raw = str(code or "").strip()
    if not raw:
        raise BillingError("BILLING_CLIENT_REQUIRED", "Selecciona un cliente.")
    row = con.execute(
        "SELECT * FROM CommandClient WHERE id=? OR humanCode=? LIMIT 1",
        (raw, raw),
    ).fetchone()
    if not row:
        raise BillingError("BILLING_CLIENT_NOT_FOUND", "Cliente no encontrado.", http_status=404)
    return dict(row)


def _contract(con: sqlite3.Connection, code: Any) -> dict[str, Any]:
    raw = str(code or "").strip()
    if not raw:
        raise BillingError("BILLING_CONTRACT_REQUIRED", "Selecciona un contrato comercial CTR.")
    row = con.execute(
        "SELECT cc.*, c.humanCode AS clientCode, c.displayName AS clientName "
        "FROM CommercialContract cc LEFT JOIN CommandClient c ON c.id=cc.clientId "
        "WHERE cc.id=? OR cc.internalId=? OR cc.humanCode=? LIMIT 1",
        (raw, raw, raw),
    ).fetchone()
    if not row:
        raise BillingError("BILLING_CONTRACT_NOT_FOUND", "Contrato comercial no encontrado.", http_status=404)
    return dict(row)


def _charge(con: sqlite3.Connection, code: Any) -> dict[str, Any]:
    raw = str(code or "").strip()
    row = con.execute(
        "SELECT bc.*, c.humanCode AS clientCode, c.displayName AS clientName, cc.humanCode AS contractCode, "
        "cc.planCode, cc.billingPeriod, cc.priceVersion, cc.priceSource, cc.taxTreatment "
        "FROM CommercialCharge bc "
        "LEFT JOIN CommandClient c ON c.id=bc.clientId "
        "LEFT JOIN CommercialContract cc ON cc.id=bc.contractId "
        "WHERE bc.id=? OR bc.internalId=? OR bc.humanCode=? LIMIT 1",
        (raw, raw, raw),
    ).fetchone()
    if not row:
        raise BillingError("BILLING_CHARGE_NOT_FOUND", "Cargo comercial no encontrado.", http_status=404)
    return dict(row)


def _payment(con: sqlite3.Connection, code: Any) -> dict[str, Any]:
    raw = str(code or "").strip()
    row = con.execute(
        "SELECT * FROM CommercialPayment WHERE id=? OR internalId=? OR humanCode=? LIMIT 1",
        (raw, raw, raw),
    ).fetchone()
    if not row:
        raise BillingError("BILLING_PAYMENT_NOT_FOUND", "Pago registrado no encontrado.", http_status=404)
    return dict(row)


def _fiscal_document(con: sqlite3.Connection, code: Any) -> dict[str, Any]:
    raw = str(code or "").strip()
    row = con.execute(
        "SELECT * FROM CommercialFiscalDocument WHERE id=? OR internalId=? OR humanCode=? OR uuid=? LIMIT 1",
        (raw, raw, raw, raw.upper()),
    ).fetchone()
    if not row:
        raise BillingError("BILLING_FISCAL_DOCUMENT_NOT_FOUND", "Documento fiscal no encontrado.", http_status=404)
    item = dict(row)
    item["draftPayload"] = _json_load(item.get("draftPayload"), {})
    item["issuerSnapshot"] = _json_load(item.get("issuerSnapshot"), {})
    item["receiverSnapshot"] = _json_load(item.get("receiverSnapshot"), {})
    return item


def ensure_billing_schema(con: sqlite3.Connection) -> None:
    statements = [
        "CREATE TABLE IF NOT EXISTS CommercialFiscalProfile("
        "id TEXT PRIMARY KEY, clientId TEXT NOT NULL UNIQUE, rfc TEXT NOT NULL, legalName TEXT NOT NULL, "
        "postalCode TEXT NOT NULL, fiscalRegime TEXT NOT NULL, cfdiUse TEXT NOT NULL, email TEXT, "
        "status TEXT NOT NULL DEFAULT 'prepared', sourceRef TEXT, confirmedAt TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS CommercialIssuerProfile("
        "id TEXT PRIMARY KEY, issuerRfc TEXT, legalName TEXT, postalCode TEXT, fiscalRegime TEXT, "
        "productServiceCode TEXT, unitCode TEXT, unitName TEXT, taxObjectCode TEXT, taxCode TEXT, exportCode TEXT, "
        "providerMode TEXT NOT NULL DEFAULT 'not_configured', providerName TEXT, csdState TEXT NOT NULL DEFAULT 'not_configured', "
        "status TEXT NOT NULL DEFAULT 'missing', sourceRef TEXT, confirmedAt TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS CommercialCharge("
        "id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, contractId TEXT NOT NULL UNIQUE, "
        "clientId TEXT NOT NULL, licenseAssignmentId TEXT, status TEXT NOT NULL DEFAULT 'open', currency TEXT NOT NULL DEFAULT 'MXN', "
        "subtotalCents INTEGER NOT NULL, taxRateBps INTEGER NOT NULL, taxCents INTEGER NOT NULL, totalCents INTEGER NOT NULL, "
        "paidCents INTEGER NOT NULL DEFAULT 0, balanceCents INTEGER NOT NULL, taxConfirmed INTEGER NOT NULL DEFAULT 0, "
        "taxRateSource TEXT NOT NULL, duePolicy TEXT NOT NULL, periodStart TEXT NOT NULL, periodEnd TEXT NOT NULL, dueOn TEXT NOT NULL, "
        "voidReason TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE INDEX IF NOT EXISTS CommercialCharge_client_due_idx ON CommercialCharge(clientId,dueOn,status)",
        "CREATE TABLE IF NOT EXISTS CommercialPayment("
        "id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, clientId TEXT NOT NULL, "
        "status TEXT NOT NULL DEFAULT 'posted', idempotencyKey TEXT NOT NULL UNIQUE, requestDigest TEXT NOT NULL, receivedAt TEXT NOT NULL, "
        "currency TEXT NOT NULL DEFAULT 'MXN', amountCents INTEGER NOT NULL, allocatedCents INTEGER NOT NULL DEFAULT 0, unappliedCents INTEGER NOT NULL DEFAULT 0, "
        "paymentForm TEXT NOT NULL, externalReference TEXT, evidenceRef TEXT, operatorNote TEXT, reversalReason TEXT, reversedAt TEXT, "
        "createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE INDEX IF NOT EXISTS CommercialPayment_client_received_idx ON CommercialPayment(clientId,receivedAt,status)",
        "CREATE TABLE IF NOT EXISTS CommercialPaymentAllocation("
        "id TEXT PRIMARY KEY, paymentId TEXT NOT NULL, chargeId TEXT NOT NULL, amountCents INTEGER NOT NULL, "
        "partialityNumber INTEGER NOT NULL, balanceBeforeCents INTEGER NOT NULL, balanceAfterCents INTEGER NOT NULL, "
        "status TEXT NOT NULL DEFAULT 'posted', createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP, "
        "UNIQUE(paymentId,chargeId))",
        "CREATE INDEX IF NOT EXISTS CommercialPaymentAllocation_charge_idx ON CommercialPaymentAllocation(chargeId,status)",
        "CREATE TABLE IF NOT EXISTS CommercialReceipt("
        "id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, paymentId TEXT NOT NULL UNIQUE, clientId TEXT NOT NULL, "
        "status TEXT NOT NULL DEFAULT 'issued', amountCents INTEGER NOT NULL, currency TEXT NOT NULL DEFAULT 'MXN', "
        "nonFiscal INTEGER NOT NULL DEFAULT 1, disclaimer TEXT NOT NULL, externalReference TEXT, issuedAt TEXT NOT NULL, voidedAt TEXT, "
        "createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS CommercialFiscalDocument("
        "id TEXT PRIMARY KEY, internalId TEXT NOT NULL UNIQUE, humanCode TEXT NOT NULL UNIQUE, kind TEXT NOT NULL, status TEXT NOT NULL, "
        "clientId TEXT NOT NULL, chargeId TEXT, paymentId TEXT, cfdiVersion TEXT NOT NULL DEFAULT '4.0', complementVersion TEXT, "
        "methodCode TEXT, paymentForm TEXT, currency TEXT, subtotalCents INTEGER, taxCents INTEGER, totalCents INTEGER, "
        "issuerSnapshot TEXT NOT NULL DEFAULT '{}', receiverSnapshot TEXT NOT NULL DEFAULT '{}', draftPayload TEXT NOT NULL DEFAULT '{}', "
        "uuid TEXT UNIQUE, provider TEXT, providerEvidenceRef TEXT, xmlSha256 TEXT, pdfRef TEXT, stampedAt TEXT, parentUuid TEXT, "
        "cancellationReason TEXT, replacementUuid TEXT, cancellationEvidenceRef TEXT, cancelRequestedAt TEXT, cancelledAt TEXT, "
        "lastErrorCode TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP, updatedAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_income_active_idx ON CommercialFiscalDocument(chargeId,kind) WHERE kind='CFDI_INGRESO'",
        "CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_payment_active_idx ON CommercialFiscalDocument(paymentId,kind) WHERE kind='CFDI_PAGO'",
        "CREATE INDEX IF NOT EXISTS CommercialFiscalDocument_client_status_idx ON CommercialFiscalDocument(clientId,status,kind)",
        "CREATE TABLE IF NOT EXISTS CommercialBillingEvent("
        "id TEXT PRIMARY KEY, eventType TEXT NOT NULL, entityKind TEXT NOT NULL, entityCode TEXT, clientId TEXT, correlationId TEXT NOT NULL, "
        "summary TEXT NOT NULL, payload TEXT NOT NULL DEFAULT '{}', createdAt TEXT DEFAULT CURRENT_TIMESTAMP)",
        "CREATE INDEX IF NOT EXISTS CommercialBillingEvent_client_created_idx ON CommercialBillingEvent(clientId,createdAt DESC)",
    ]
    for sql in statements:
        con.execute(sql)
    con.execute(
        "INSERT OR IGNORE INTO CommercialIssuerProfile(id,status,providerMode,csdState) VALUES('issuer_primary','missing','not_configured','not_configured')"
    )


def _event(con: sqlite3.Connection, event_type: str, kind: str, code: str | None, client_id: str | None, summary: str, payload: Any) -> None:
    con.execute(
        "INSERT INTO CommercialBillingEvent(id,eventType,entityKind,entityCode,clientId,correlationId,summary,payload) VALUES(?,?,?,?,?,?,?,?)",
        (uuid.uuid4().hex, event_type, kind, code, client_id, f"billing-{uuid.uuid4().hex}", summary[:300], _canonical_json(payload)),
    )


def issuer_profile(con: sqlite3.Connection) -> dict[str, Any]:
    row = con.execute("SELECT * FROM CommercialIssuerProfile WHERE id='issuer_primary'").fetchone()
    return dict(row) if row else {"id": "issuer_primary", "status": "missing", "providerMode": "not_configured", "csdState": "not_configured"}


def receiver_profile(con: sqlite3.Connection, client_id: str) -> dict[str, Any] | None:
    row = con.execute("SELECT * FROM CommercialFiscalProfile WHERE clientId=?", (client_id,)).fetchone()
    return dict(row) if row else None


def save_receiver_profile(con: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    client = _client(con, body.get("clientCode") or body.get("clientId"))
    rfc = str(body.get("rfc") or "").strip().upper()
    legal_name = str(body.get("legalName") or "").strip()
    postal = str(body.get("postalCode") or "").strip()
    regime = str(body.get("fiscalRegime") or "").strip()
    cfdi_use = str(body.get("cfdiUse") or "").strip().upper()
    email = str(body.get("email") or "").strip() or None
    source_ref = str(body.get("sourceRef") or "").strip()[:240] or None
    confirmed = body.get("confirmFiscalData") is True

    if not re.fullmatch(r"[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}", rfc):
        raise BillingError("BILLING_RFC_INVALID", "RFC receptor invalido.")
    if not legal_name:
        raise BillingError("BILLING_FISCAL_NAME_REQUIRED", "Nombre o razon social fiscal es obligatorio.")
    if not re.fullmatch(r"\d{5}", postal):
        raise BillingError("BILLING_FISCAL_POSTAL_INVALID", "Codigo postal fiscal debe tener cinco digitos.")
    if not re.fullmatch(r"\d{3}", regime):
        raise BillingError("BILLING_FISCAL_REGIME_INVALID", "Regimen fiscal debe ser una clave SAT de tres digitos.")
    if not re.fullmatch(r"[A-Z0-9]{3}", cfdi_use):
        raise BillingError("BILLING_CFDI_USE_INVALID", "Uso CFDI debe ser una clave SAT de tres caracteres.")
    if confirmed and not source_ref:
        raise BillingError("BILLING_FISCAL_EVIDENCE_REQUIRED", "Confirmar datos fiscales requiere referencia a constancia/documento fuente.")

    existing = con.execute("SELECT id FROM CommercialFiscalProfile WHERE clientId=?", (client["id"],)).fetchone()
    row_id = existing["id"] if existing else f"fiscal_{uuid.uuid4().hex}"
    status = "operator_confirmed" if confirmed else "prepared"
    confirmed_at = _now_iso() if confirmed else None
    if existing:
        con.execute(
            "UPDATE CommercialFiscalProfile SET rfc=?,legalName=?,postalCode=?,fiscalRegime=?,cfdiUse=?,email=?,status=?,sourceRef=?,confirmedAt=?,updatedAt=CURRENT_TIMESTAMP WHERE id=?",
            (rfc, legal_name, postal, regime, cfdi_use, email, status, source_ref, confirmed_at, row_id),
        )
    else:
        con.execute(
            "INSERT INTO CommercialFiscalProfile(id,clientId,rfc,legalName,postalCode,fiscalRegime,cfdiUse,email,status,sourceRef,confirmedAt) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (row_id, client["id"], rfc, legal_name, postal, regime, cfdi_use, email, status, source_ref, confirmed_at),
        )
    result = receiver_profile(con, client["id"]) or {}
    _event(con, "fiscal.receiver_profile_saved", "fiscal_profile", row_id, client["id"], f"Perfil fiscal receptor {status}: {client['displayName']}", {"status": status, "sourceRef": source_ref})
    return {"ok": True, "profile": result, "message": "Perfil fiscal guardado; no emite CFDI."}


def save_issuer_profile(con: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    allowed_fields = {
        "issuerRfc", "legalName", "postalCode", "fiscalRegime", "productServiceCode", "unitCode", "unitName",
        "taxObjectCode", "taxCode", "exportCode", "providerMode", "providerName", "csdState", "sourceRef", "confirmIssuerData",
    }
    secretish = [key for key in body if re.search(r"password|private.?key|secret|token|cerBytes|keyBytes", key, re.I)]
    if secretish:
        raise BillingError("BILLING_FISCAL_SECRET_FORBIDDEN", "Cloud Center no recibe CSD, llaves privadas, contrasenas ni tokens.", details={"forbiddenFields": secretish})
    unexpected = [key for key in body if key not in allowed_fields]
    if unexpected:
        raise BillingError("BILLING_ISSUER_FIELD_UNSUPPORTED", "Hay campos fiscales no soportados.", details={"fields": unexpected})

    rfc = str(body.get("issuerRfc") or "").strip().upper()
    legal_name = str(body.get("legalName") or "").strip()
    postal = str(body.get("postalCode") or "").strip()
    regime = str(body.get("fiscalRegime") or "").strip()
    prod = str(body.get("productServiceCode") or "").strip()
    unit = str(body.get("unitCode") or "").strip().upper()
    unit_name = str(body.get("unitName") or "Servicio").strip() or "Servicio"
    tax_object = str(body.get("taxObjectCode") or "").strip()
    tax_code = str(body.get("taxCode") or "").strip()
    export_code = str(body.get("exportCode") or "").strip()
    provider_mode = str(body.get("providerMode") or "not_configured").strip().lower()
    provider_name = str(body.get("providerName") or "").strip() or None
    csd_state = str(body.get("csdState") or "not_configured").strip().lower()
    source_ref = str(body.get("sourceRef") or "").strip()[:240] or None
    confirmed = body.get("confirmIssuerData") is True

    if provider_mode not in {"not_configured", "manual_sat", "pac_external"}:
        raise BillingError("BILLING_PROVIDER_MODE_INVALID", "providerMode debe ser not_configured, manual_sat o pac_external.")
    if csd_state not in {"not_configured", "presence_only", "externally_managed"}:
        raise BillingError("BILLING_CSD_STATE_INVALID", "csdState debe ser not_configured, presence_only o externally_managed.")
    if confirmed:
        if not re.fullmatch(r"[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}", rfc):
            raise BillingError("BILLING_ISSUER_RFC_INVALID", "RFC emisor invalido.")
        if not legal_name:
            raise BillingError("BILLING_ISSUER_NAME_REQUIRED", "Nombre o razon social del emisor es obligatorio.")
        if not re.fullmatch(r"\d{5}", postal):
            raise BillingError("BILLING_ISSUER_POSTAL_INVALID", "Codigo postal emisor debe tener cinco digitos.")
        if not re.fullmatch(r"\d{3}", regime):
            raise BillingError("BILLING_ISSUER_REGIME_INVALID", "Regimen fiscal emisor debe ser clave SAT de tres digitos.")
        if not re.fullmatch(r"\d{8}", prod):
            raise BillingError("BILLING_PRODUCT_SERVICE_CODE_INVALID", "ClaveProdServ debe tener ocho digitos y ser confirmada por el emisor.")
        if not re.fullmatch(r"[A-Z0-9]{2,3}", unit):
            raise BillingError("BILLING_UNIT_CODE_INVALID", "ClaveUnidad debe ser una clave SAT valida para el servicio.")
        if not re.fullmatch(r"\d{2}", tax_object):
            raise BillingError("BILLING_TAX_OBJECT_CODE_INVALID", "ObjetoImp debe ser una clave SAT de dos digitos.")
        if not re.fullmatch(r"\d{3}", tax_code):
            raise BillingError("BILLING_TAX_CODE_INVALID", "Impuesto debe ser una clave SAT de tres digitos.")
        if not re.fullmatch(r"\d{2}", export_code):
            raise BillingError("BILLING_EXPORT_CODE_INVALID", "Exportacion debe ser una clave SAT de dos digitos.")
        if not source_ref:
            raise BillingError("BILLING_ISSUER_EVIDENCE_REQUIRED", "Confirmar emisor requiere referencia a datos fiscales/documento fuente.")
        if provider_mode == "pac_external" and not provider_name:
            raise BillingError("BILLING_PAC_NAME_REQUIRED", "PAC externo requiere nombre de proveedor.")

    status = "operator_confirmed" if confirmed else "prepared"
    confirmed_at = _now_iso() if confirmed else None
    con.execute(
        "UPDATE CommercialIssuerProfile SET issuerRfc=?,legalName=?,postalCode=?,fiscalRegime=?,productServiceCode=?,unitCode=?,unitName=?,"
        "taxObjectCode=?,taxCode=?,exportCode=?,providerMode=?,providerName=?,csdState=?,status=?,sourceRef=?,confirmedAt=?,updatedAt=CURRENT_TIMESTAMP WHERE id='issuer_primary'",
        (rfc or None, legal_name or None, postal or None, regime or None, prod or None, unit or None, unit_name, tax_object or None,
         tax_code or None, export_code or None, provider_mode, provider_name, csd_state, status, source_ref, confirmed_at),
    )
    result = issuer_profile(con)
    _event(con, "fiscal.issuer_profile_saved", "issuer_profile", "issuer_primary", None, f"Perfil fiscal emisor {status}", {"status": status, "providerMode": provider_mode, "csdState": csd_state, "secretsExposed": False})
    return {"ok": True, "profile": result, "gateway": gateway_status(result), "message": "Perfil emisor guardado; CSD/secretos permanecen fuera de PRISMA."}


def _derived_charge_state(charge: dict[str, Any], *, as_of: Any = None) -> str:
    if charge.get("status") == "void":
        return "void"
    balance = int(charge.get("balanceCents") or 0)
    paid = int(charge.get("paidCents") or 0)
    if balance <= 0:
        return "paid"
    if _today(as_of) > _today(charge.get("dueOn")):
        return "past_due"
    if paid > 0:
        return "partially_paid"
    return "open"


def _active_allocated_for_charge(con: sqlite3.Connection, charge_id: str) -> int:
    row = con.execute(
        "SELECT COALESCE(SUM(amountCents),0) AS total FROM CommercialPaymentAllocation WHERE chargeId=? AND status='posted'",
        (charge_id,),
    ).fetchone()
    return int(row["total"] if row else 0)


def _refresh_charge(con: sqlite3.Connection, charge_id: str, *, as_of: Any = None) -> dict[str, Any]:
    row = con.execute("SELECT * FROM CommercialCharge WHERE id=?", (charge_id,)).fetchone()
    if not row:
        raise BillingError("BILLING_CHARGE_NOT_FOUND", "Cargo no encontrado.", http_status=404)
    item = dict(row)
    if item.get("status") == "void":
        return item
    paid = _active_allocated_for_charge(con, charge_id)
    total = int(item.get("totalCents") or 0)
    balance = max(total - paid, 0)
    item.update({"paidCents": paid, "balanceCents": balance})
    status = _derived_charge_state(item, as_of=as_of)
    con.execute(
        "UPDATE CommercialCharge SET paidCents=?,balanceCents=?,status=?,updatedAt=CURRENT_TIMESTAMP WHERE id=?",
        (paid, balance, status, charge_id),
    )
    item.update({"status": status})
    return item


def create_charge(con: sqlite3.Connection, body: dict[str, Any], id_factory: Callable[[sqlite3.Connection, str, Any], dict[str, Any]]) -> dict[str, Any]:
    contract = _contract(con, body.get("contractCode") or body.get("contractId"))
    existing = con.execute("SELECT * FROM CommercialCharge WHERE contractId=?", (contract["id"],)).fetchone()
    if existing:
        item = dict(existing)
        item["status"] = _derived_charge_state(item, as_of=body.get("asOf"))
        return {"ok": True, "idempotent": True, "charge": item, "message": "El contrato ya tiene un cargo comercial; no se duplico."}

    tax_confirmed = body.get("confirmTax") is True
    if not tax_confirmed:
        raise BillingError("BILLING_TAX_CONFIRMATION_REQUIRED", "Crear cargo requiere confirmar tratamiento/tasa de impuesto para este contrato.")
    rate = _validate_rate_bps(body.get("taxRateBps") if body.get("taxRateBps") not in (None, "") else DEFAULT_TAX_RATE_BPS)
    subtotal = int(contract.get("agreedPriceMxn") or 0) * 100
    if subtotal <= 0:
        raise BillingError("BILLING_CONTRACT_PRICE_INVALID", "El contrato no tiene precio acordado positivo.")
    tax = _tax_cents(subtotal, rate)
    total = subtotal + tax
    due_on = _today(body.get("dueOn") or contract.get("validFrom")).isoformat()
    identity = id_factory(con, "charge", {"contractCode": contract["humanCode"], "clientCode": contract.get("clientCode")})
    row_id = identity["internalId"]
    status_seed = "open"
    con.execute(
        "INSERT INTO CommercialCharge(id,internalId,humanCode,contractId,clientId,licenseAssignmentId,status,currency,subtotalCents,taxRateBps,taxCents,totalCents,paidCents,balanceCents,taxConfirmed,taxRateSource,duePolicy,periodStart,periodEnd,dueOn) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (row_id, row_id, identity["humanCode"], contract["id"], contract["clientId"], contract.get("licenseAssignmentId"), status_seed,
         contract.get("currency") or "MXN", subtotal, rate, tax, total, 0, total, 1,
         str(body.get("taxRateSource") or DEFAULT_TAX_RATE_SOURCE), str(body.get("duePolicy") or DEFAULT_DUE_POLICY),
         contract["validFrom"], contract["validUntil"], due_on),
    )
    item = _refresh_charge(con, row_id, as_of=body.get("asOf"))
    item.update({"contractCode": contract["humanCode"], "clientCode": contract.get("clientCode"), "clientName": contract.get("clientName"), "planCode": contract.get("planCode"), "billingPeriod": contract.get("billingPeriod")})
    _event(con, "billing.charge_created", "charge", identity["humanCode"], contract["clientId"], f"Cargo {identity['humanCode']} creado desde {contract['humanCode']}", {"subtotalCents": subtotal, "taxCents": tax, "totalCents": total, "taxRateBps": rate, "dueOn": due_on})
    return {"ok": True, "idempotent": False, "charge": item, "message": "Cargo creado desde contrato canonico; no mueve dinero."}


def void_charge(con: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    charge = _charge(con, body.get("chargeCode") or body.get("chargeId"))
    reason = str(body.get("reason") or "").strip()[:500]
    if body.get("confirmVoid") is not True or not reason:
        raise BillingError("BILLING_VOID_CONFIRMATION_REQUIRED", "Anular cargo requiere confirmacion explicita y motivo.")
    allocated = _active_allocated_for_charge(con, charge["id"])
    if allocated > 0:
        raise BillingError("BILLING_VOID_BLOCKED_BY_PAYMENT", "No se puede anular un cargo con pagos asignados; primero resuelve/revierte el pago cuando fiscalmente sea valido.")
    fiscal = con.execute(
        "SELECT status,humanCode FROM CommercialFiscalDocument WHERE chargeId=? AND kind='CFDI_INGRESO' AND status IN ('external_stamped','cancel_requested','cancellation_rejected') LIMIT 1",
        (charge["id"],),
    ).fetchone()
    if fiscal:
        raise BillingError("BILLING_VOID_BLOCKED_BY_CFDI", "El cargo tiene CFDI timbrado/no cancelado; usa primero la ruta fiscal de cancelacion.", details=dict(fiscal))
    con.execute("UPDATE CommercialCharge SET status='void',voidReason=?,balanceCents=0,updatedAt=CURRENT_TIMESTAMP WHERE id=?", (reason, charge["id"]))
    _event(con, "billing.charge_voided", "charge", charge["humanCode"], charge["clientId"], f"Cargo anulado: {charge['humanCode']}", {"reason": reason})
    return {"ok": True, "charge": _charge(con, charge["id"]), "message": "Cargo anulado administrativamente; no elimina evidencia."}


def _payment_request_digest(body: dict[str, Any], charge: dict[str, Any], amount_cents: int, payment_form: str) -> str:
    material = {
        "chargeId": charge["id"],
        "clientId": charge["clientId"],
        "amountCents": amount_cents,
        "currency": str(body.get("currency") or "MXN").upper(),
        "paymentForm": payment_form,
        "receivedAt": str(body.get("receivedAt") or ""),
        "externalReference": str(body.get("externalReference") or "").strip(),
        "evidenceRef": str(body.get("evidenceRef") or "").strip(),
    }
    return _sha256_payload(material)


def register_external_payment(con: sqlite3.Connection, body: dict[str, Any], id_factory: Callable[[sqlite3.Connection, str, Any], dict[str, Any]]) -> dict[str, Any]:
    charge = _charge(con, body.get("chargeCode") or body.get("chargeId"))
    if charge.get("status") == "void":
        raise BillingError("BILLING_PAYMENT_CHARGE_VOID", "No se puede asignar pago a un cargo anulado.")
    charge = _refresh_charge(con, charge["id"], as_of=body.get("asOf"))
    amount = _money_to_cents(body.get("amountMxn"), "amountMxn")
    currency = str(body.get("currency") or "MXN").strip().upper()
    if currency != str(charge.get("currency") or "MXN").upper():
        raise BillingError("BILLING_PAYMENT_CURRENCY_MISMATCH", "Moneda del pago no coincide con el cargo.")
    try:
        payment_form = normalize_payment_form(body.get("paymentForm"))
    except FiscalGatewayError as exc:
        raise BillingError(exc.code, str(exc)) from exc
    idem = str(body.get("idempotencyKey") or "").strip()
    if len(idem) < 8:
        raise BillingError("BILLING_IDEMPOTENCY_KEY_REQUIRED", "Registrar pago externo requiere idempotencyKey estable de al menos ocho caracteres.")
    external_ref = str(body.get("externalReference") or "").strip()[:240] or None
    evidence_ref = str(body.get("evidenceRef") or "").strip()[:240] or None
    if not external_ref and not evidence_ref:
        raise BillingError("BILLING_PAYMENT_EVIDENCE_REQUIRED", "Registrar un pago externo requiere referencia o evidencia; PRISMA no valida el movimiento bancario.")
    received_at = str(body.get("receivedAt") or _now_iso()).strip()
    try:
        datetime.fromisoformat(received_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BillingError("BILLING_PAYMENT_DATE_INVALID", "receivedAt debe ser fecha/hora ISO valida.") from exc
    digest = _payment_request_digest({**body, "receivedAt": received_at}, charge, amount, payment_form)
    existing = con.execute("SELECT * FROM CommercialPayment WHERE idempotencyKey=?", (idem,)).fetchone()
    if existing:
        item = dict(existing)
        if item.get("requestDigest") != digest:
            raise BillingError("BILLING_IDEMPOTENCY_CONFLICT", "La misma idempotencyKey ya existe con datos distintos.", http_status=409)
        receipt = con.execute("SELECT * FROM CommercialReceipt WHERE paymentId=?", (item["id"],)).fetchone()
        allocations = [dict(r) for r in con.execute("SELECT * FROM CommercialPaymentAllocation WHERE paymentId=? ORDER BY createdAt", (item["id"],))]
        return {"ok": True, "idempotent": True, "payment": item, "receipt": _row_dict(receipt), "allocations": allocations, "message": "Retry idempotente: no se duplico el pago."}

    payment_identity = id_factory(con, "payment", {"chargeCode": charge["humanCode"], "clientCode": charge.get("clientCode")})
    receipt_identity = id_factory(con, "receipt", {"paymentCode": payment_identity["humanCode"]})
    payment_id = payment_identity["internalId"]
    receipt_id = receipt_identity["internalId"]
    balance_before = int(charge.get("balanceCents") or 0)
    allocation_amount = min(amount, balance_before)
    unapplied = max(amount - allocation_amount, 0)
    partiality_row = con.execute(
        "SELECT COUNT(*) AS n FROM CommercialPaymentAllocation WHERE chargeId=? AND status='posted'",
        (charge["id"],),
    ).fetchone()
    partiality = int(partiality_row["n"] if partiality_row else 0) + 1
    balance_after = max(balance_before - allocation_amount, 0)
    con.execute(
        "INSERT INTO CommercialPayment(id,internalId,humanCode,clientId,status,idempotencyKey,requestDigest,receivedAt,currency,amountCents,allocatedCents,unappliedCents,paymentForm,externalReference,evidenceRef,operatorNote) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (payment_id, payment_id, payment_identity["humanCode"], charge["clientId"], "posted", idem, digest, received_at, currency, amount,
         allocation_amount, unapplied, payment_form, external_ref, evidence_ref, str(body.get("operatorNote") or "").strip()[:1000] or None),
    )
    allocations: list[dict[str, Any]] = []
    if allocation_amount > 0:
        allocation_id = f"alloc_{uuid.uuid4().hex}"
        con.execute(
            "INSERT INTO CommercialPaymentAllocation(id,paymentId,chargeId,amountCents,partialityNumber,balanceBeforeCents,balanceAfterCents,status) VALUES(?,?,?,?,?,?,?,'posted')",
            (allocation_id, payment_id, charge["id"], allocation_amount, partiality, balance_before, balance_after),
        )
        allocations.append(dict(con.execute("SELECT * FROM CommercialPaymentAllocation WHERE id=?", (allocation_id,)).fetchone()))
    disclaimer = "RECIBO INTERNO NO FISCAL. PRISMA registra un pago externo informado por el operador; no procesa, valida ni custodia fondos."
    con.execute(
        "INSERT INTO CommercialReceipt(id,internalId,humanCode,paymentId,clientId,status,amountCents,currency,nonFiscal,disclaimer,externalReference,issuedAt) VALUES(?,?,?,?,?,'issued',?,?,1,?,?,?)",
        (receipt_id, receipt_id, receipt_identity["humanCode"], payment_id, charge["clientId"], amount, currency, disclaimer, external_ref, received_at),
    )
    refreshed = _refresh_charge(con, charge["id"], as_of=body.get("asOf"))
    payment = dict(con.execute("SELECT * FROM CommercialPayment WHERE id=?", (payment_id,)).fetchone())
    receipt = dict(con.execute("SELECT * FROM CommercialReceipt WHERE id=?", (receipt_id,)).fetchone())
    _event(con, "billing.external_payment_recorded", "payment", payment_identity["humanCode"], charge["clientId"], f"Pago externo registrado {payment_identity['humanCode']} contra {charge['humanCode']}", {"amountCents": amount, "allocatedCents": allocation_amount, "unappliedCents": unapplied, "paymentForm": payment_form, "externalReference": external_ref, "evidenceRef": evidence_ref, "moneyMovedByPrisma": False})
    return {"ok": True, "idempotent": False, "payment": payment, "receipt": receipt, "allocations": allocations, "charge": refreshed, "message": "Pago externo registrado; PRISMA no movio ni valido dinero."}


def reverse_external_payment(con: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    payment = _payment(con, body.get("paymentCode") or body.get("paymentId"))
    if payment.get("status") == "reversed":
        return {"ok": True, "idempotent": True, "payment": payment, "message": "El pago ya estaba revertido."}
    reason = str(body.get("reason") or "").strip()[:500]
    if body.get("confirmReverse") is not True or not reason:
        raise BillingError("BILLING_PAYMENT_REVERSE_CONFIRMATION_REQUIRED", "Revertir pago requiere confirmacion explicita y motivo.")
    stamped = con.execute(
        "SELECT humanCode,status,uuid FROM CommercialFiscalDocument WHERE paymentId=? AND kind='CFDI_PAGO' AND status IN ('external_stamped','cancel_requested','cancellation_rejected') LIMIT 1",
        (payment["id"],),
    ).fetchone()
    if stamped:
        raise BillingError("BILLING_PAYMENT_REVERSE_BLOCKED_BY_CFDI", "Hay Complemento de Pagos timbrado/no cancelado; cancela fiscalmente antes de revertir el registro.", details=dict(stamped))
    allocations = [dict(r) for r in con.execute("SELECT * FROM CommercialPaymentAllocation WHERE paymentId=? AND status='posted'", (payment["id"],))]
    con.execute("UPDATE CommercialPaymentAllocation SET status='reversed',updatedAt=CURRENT_TIMESTAMP WHERE paymentId=? AND status='posted'", (payment["id"],))
    con.execute("UPDATE CommercialPayment SET status='reversed',allocatedCents=0,unappliedCents=0,reversalReason=?,reversedAt=?,updatedAt=CURRENT_TIMESTAMP WHERE id=?", (reason, _now_iso(), payment["id"]))
    con.execute("UPDATE CommercialReceipt SET status='void',voidedAt=?,updatedAt=CURRENT_TIMESTAMP WHERE paymentId=?", (_now_iso(), payment["id"]))
    charges = []
    for allocation in allocations:
        charges.append(_refresh_charge(con, allocation["chargeId"]))
    after = _payment(con, payment["id"])
    _event(con, "billing.external_payment_reversed", "payment", payment["humanCode"], payment["clientId"], f"Registro de pago revertido: {payment['humanCode']}", {"reason": reason, "fiscalComplementStamped": False})
    return {"ok": True, "idempotent": False, "payment": after, "charges": charges, "message": "Registro de pago externo revertido sin borrar historial."}


def _active_allocations(con: sqlite3.Connection, *, charge_id: str | None = None, payment_id: str | None = None) -> list[dict[str, Any]]:
    if charge_id:
        rows = con.execute("SELECT * FROM CommercialPaymentAllocation WHERE chargeId=? AND status='posted' ORDER BY createdAt", (charge_id,)).fetchall()
    elif payment_id:
        rows = con.execute("SELECT * FROM CommercialPaymentAllocation WHERE paymentId=? AND status='posted' ORDER BY createdAt", (payment_id,)).fetchall()
    else:
        rows = []
    return [dict(row) for row in rows]


def _payment_map(con: sqlite3.Connection, ids: list[str]) -> dict[str, dict[str, Any]]:
    return {pid: dict(con.execute("SELECT * FROM CommercialPayment WHERE id=?", (pid,)).fetchone()) for pid in ids if con.execute("SELECT 1 FROM CommercialPayment WHERE id=?", (pid,)).fetchone()}


def prepare_income_cfdi(con: sqlite3.Connection, body: dict[str, Any], id_factory: Callable[[sqlite3.Connection, str, Any], dict[str, Any]]) -> dict[str, Any]:
    charge = _charge(con, body.get("chargeCode") or body.get("chargeId"))
    if charge.get("status") == "void":
        raise BillingError("BILLING_CFDI_CHARGE_VOID", "No se prepara CFDI para cargo anulado.")
    contract = _contract(con, charge["contractId"])
    issuer = issuer_profile(con)
    receiver = receiver_profile(con, charge["clientId"]) or {}
    allocations = _active_allocations(con, charge_id=charge["id"])
    payments = _payment_map(con, sorted({str(item["paymentId"]) for item in allocations}))
    charge = _refresh_charge(con, charge["id"], as_of=body.get("asOf"))
    prepared = build_income_cfdi_draft(charge=charge, contract=contract, issuer=issuer, receiver=receiver, posted_allocations=allocations, payment_rows=payments)
    status = "ready_to_stamp" if prepared["ready"] else "draft_blocked"
    existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE chargeId=? AND kind='CFDI_INGRESO'", (charge["id"],)).fetchone()
    if existing and existing["status"] in {"external_stamped", "cancel_requested", "cancellation_rejected"}:
        return {"ok": True, "idempotent": True, "document": _fiscal_document(con, existing["id"]), "gateway": gateway_status(issuer), "message": "El cargo ya tiene CFDI externo registrado; no se reemplazo."}
    identity = None
    if existing:
        doc_id = existing["id"]
        human_code = existing["humanCode"]
    else:
        identity = id_factory(con, "fiscal", {"kind": "CFDI_INGRESO", "chargeCode": charge["humanCode"]})
        doc_id = identity["internalId"]
        human_code = identity["humanCode"]
    payload = prepared["draft"]
    values = (
        status, prepared.get("method"), prepared.get("paymentForm"), charge.get("currency") or "MXN", int(charge.get("subtotalCents") or 0),
        int(charge.get("taxCents") or 0), int(charge.get("totalCents") or 0), _canonical_json(issuer), _canonical_json(receiver), _canonical_json(payload),
        prepared["missingPrerequisites"][0] if prepared["missingPrerequisites"] else None,
    )
    if existing:
        con.execute(
            "UPDATE CommercialFiscalDocument SET status=?,methodCode=?,paymentForm=?,currency=?,subtotalCents=?,taxCents=?,totalCents=?,issuerSnapshot=?,receiverSnapshot=?,draftPayload=?,lastErrorCode=?,updatedAt=CURRENT_TIMESTAMP WHERE id=?",
            (*values, doc_id),
        )
    else:
        con.execute(
            "INSERT INTO CommercialFiscalDocument(id,internalId,humanCode,kind,status,clientId,chargeId,cfdiVersion,methodCode,paymentForm,currency,subtotalCents,taxCents,totalCents,issuerSnapshot,receiverSnapshot,draftPayload,lastErrorCode) VALUES(?,?,?,'CFDI_INGRESO',?,?,?,'4.0',?,?,?,?,?,?,?,?,?,?)",
            (doc_id, doc_id, human_code, status, charge["clientId"], charge["id"], prepared.get("method"), prepared.get("paymentForm"), charge.get("currency") or "MXN",
             int(charge.get("subtotalCents") or 0), int(charge.get("taxCents") or 0), int(charge.get("totalCents") or 0), _canonical_json(issuer), _canonical_json(receiver), _canonical_json(payload),
             prepared["missingPrerequisites"][0] if prepared["missingPrerequisites"] else None),
        )
    doc = _fiscal_document(con, doc_id)
    _event(con, "fiscal.income_draft_prepared", "fiscal_document", human_code, charge["clientId"], f"CFDI ingreso {status}: {human_code}", {"ready": prepared["ready"], "missing": prepared["missingPrerequisites"], "liveStamping": False})
    return {"ok": True, "idempotent": bool(existing), "document": doc, "missingPrerequisites": prepared["missingPrerequisites"], "gateway": gateway_status(issuer), "message": "Borrador CFDI preparado localmente; no fue timbrado."}


def register_external_stamp(con: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    doc = _fiscal_document(con, body.get("documentCode") or body.get("documentId"))
    if doc.get("status") == "external_stamped":
        supplied = validate_cfdi_uuid(body.get("uuid"))
        if supplied != doc.get("uuid"):
            raise BillingError("BILLING_CFDI_STAMP_CONFLICT", "El documento ya tiene otro UUID registrado.", http_status=409)
        return {"ok": True, "idempotent": True, "document": doc, "message": "UUID externo ya registrado."}
    if doc.get("status") != "ready_to_stamp":
        raise BillingError("BILLING_CFDI_NOT_READY", "El documento no cumple prerequisitos locales para registrar timbrado externo.", details={"status": doc.get("status"), "lastErrorCode": doc.get("lastErrorCode")})
    try:
        cfdi_uuid = validate_cfdi_uuid(body.get("uuid"))
        xml_sha = validate_sha256(body.get("xmlSha256"))
    except FiscalGatewayError as exc:
        raise BillingError(exc.code, str(exc)) from exc
    provider = str(body.get("provider") or "").strip()[:120]
    evidence = str(body.get("providerEvidenceRef") or "").strip()[:240]
    if not provider or not evidence:
        raise BillingError("BILLING_CFDI_EXTERNAL_EVIDENCE_REQUIRED", "Registrar timbrado externo requiere proveedor y referencia de evidencia.")
    pdf_ref = str(body.get("pdfRef") or "").strip()[:240] or None
    stamped_at = str(body.get("stampedAt") or _now_iso()).strip()
    con.execute(
        "UPDATE CommercialFiscalDocument SET status='external_stamped',uuid=?,provider=?,providerEvidenceRef=?,xmlSha256=?,pdfRef=?,stampedAt=?,lastErrorCode=NULL,updatedAt=CURRENT_TIMESTAMP WHERE id=?",
        (cfdi_uuid, provider, evidence, xml_sha, pdf_ref, stamped_at, doc["id"]),
    )
    after = _fiscal_document(con, doc["id"])
    _event(con, "fiscal.external_stamp_registered", "fiscal_document", doc["humanCode"], doc["clientId"], f"Timbrado externo registrado: {doc['humanCode']}", {"uuid": cfdi_uuid, "provider": provider, "providerEvidenceRef": evidence, "xmlStored": False, "secretsExposed": False})
    return {"ok": True, "idempotent": False, "document": after, "message": "Resultado de timbrado externo registrado; PRISMA no ejecuto el timbrado."}


def prepare_payment_complement(con: sqlite3.Connection, body: dict[str, Any], id_factory: Callable[[sqlite3.Connection, str, Any], dict[str, Any]]) -> dict[str, Any]:
    payment = _payment(con, body.get("paymentCode") or body.get("paymentId"))
    if payment.get("status") != "posted":
        raise BillingError("BILLING_PAYMENT_COMPLEMENT_PAYMENT_NOT_POSTED", "Complemento requiere pago registrado activo.")
    allocations = _active_allocations(con, payment_id=payment["id"])
    charges: dict[str, dict[str, Any]] = {}
    income_docs: dict[str, dict[str, Any]] = {}
    client_ids: set[str] = set()
    for allocation in allocations:
        ch = _charge(con, allocation["chargeId"])
        charges[ch["id"]] = ch
        client_ids.add(ch["clientId"])
        doc_row = con.execute("SELECT * FROM CommercialFiscalDocument WHERE chargeId=? AND kind='CFDI_INGRESO'", (ch["id"],)).fetchone()
        if doc_row:
            income_docs[ch["id"]] = _fiscal_document(con, doc_row["id"])
    if len(client_ids) != 1 or payment["clientId"] not in client_ids:
        raise BillingError("BILLING_PAYMENT_COMPLEMENT_CLIENT_SCOPE_INVALID", "Las asignaciones del pago deben pertenecer a un solo cliente.")
    issuer = issuer_profile(con)
    receiver = receiver_profile(con, payment["clientId"]) or {}
    prepared = build_payment_complement_draft(payment=payment, allocations=allocations, charges=charges, income_documents=income_docs, issuer=issuer, receiver=receiver)
    status = "ready_to_stamp" if prepared["ready"] else "draft_blocked"
    existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE paymentId=? AND kind='CFDI_PAGO'", (payment["id"],)).fetchone()
    if existing and existing["status"] in {"external_stamped", "cancel_requested", "cancellation_rejected"}:
        return {"ok": True, "idempotent": True, "document": _fiscal_document(con, existing["id"]), "gateway": gateway_status(issuer), "message": "El pago ya tiene Complemento timbrado registrado."}
    if existing:
        doc_id = existing["id"]
        human_code = existing["humanCode"]
    else:
        identity = id_factory(con, "fiscal", {"kind": "CFDI_PAGO", "paymentCode": payment["humanCode"]})
        doc_id = identity["internalId"]
        human_code = identity["humanCode"]
    parent_uuids = sorted({str(doc.get("uuid")) for doc in income_docs.values() if doc.get("uuid")})
    parent_uuid = parent_uuids[0] if len(parent_uuids) == 1 else None
    payload = prepared["draft"]
    if existing:
        con.execute(
            "UPDATE CommercialFiscalDocument SET status=?,currency=?,totalCents=?,issuerSnapshot=?,receiverSnapshot=?,draftPayload=?,parentUuid=?,lastErrorCode=?,updatedAt=CURRENT_TIMESTAMP WHERE id=?",
            (status, payment.get("currency") or "MXN", int(payment.get("amountCents") or 0), _canonical_json(issuer), _canonical_json(receiver), _canonical_json(payload), parent_uuid,
             prepared["missingPrerequisites"][0] if prepared["missingPrerequisites"] else None, doc_id),
        )
    else:
        con.execute(
            "INSERT INTO CommercialFiscalDocument(id,internalId,humanCode,kind,status,clientId,paymentId,cfdiVersion,complementVersion,currency,totalCents,issuerSnapshot,receiverSnapshot,draftPayload,parentUuid,lastErrorCode) VALUES(?,?,?,'CFDI_PAGO',?,?,?,'4.0','2.0',?,?,?,?,?,?,?)",
            (doc_id, doc_id, human_code, status, payment["clientId"], payment["id"], payment.get("currency") or "MXN", int(payment.get("amountCents") or 0), _canonical_json(issuer), _canonical_json(receiver), _canonical_json(payload), parent_uuid,
             prepared["missingPrerequisites"][0] if prepared["missingPrerequisites"] else None),
        )
    doc = _fiscal_document(con, doc_id)
    _event(con, "fiscal.payment_complement_draft_prepared", "fiscal_document", human_code, payment["clientId"], f"Complemento de Pagos {status}: {human_code}", {"ready": prepared["ready"], "missing": prepared["missingPrerequisites"], "liveStamping": False})
    return {"ok": True, "idempotent": bool(existing), "document": doc, "missingPrerequisites": prepared["missingPrerequisites"], "gateway": gateway_status(issuer), "message": "Borrador de Complemento de Pagos 2.0 preparado; no fue timbrado."}


def request_cfdi_cancellation(con: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    doc = _fiscal_document(con, body.get("documentCode") or body.get("documentId"))
    if doc.get("status") == "cancelled":
        return {"ok": True, "idempotent": True, "document": doc, "message": "El CFDI ya figura como cancelado externamente."}
    if doc.get("status") != "external_stamped":
        raise BillingError("BILLING_CFDI_CANCEL_NOT_STAMPED", "Solo se solicita cancelacion para CFDI con UUID timbrado registrado.")
    if body.get("confirmCancellationRequest") is not True:
        raise BillingError("BILLING_CFDI_CANCEL_CONFIRMATION_REQUIRED", "La solicitud de cancelacion requiere confirmacion explicita.")
    try:
        reason, replacement = validate_cancellation_request(body.get("reason"), body.get("replacementUuid"))
    except FiscalGatewayError as exc:
        raise BillingError(exc.code, str(exc)) from exc
    con.execute(
        "UPDATE CommercialFiscalDocument SET status='cancel_requested',cancellationReason=?,replacementUuid=?,cancelRequestedAt=?,updatedAt=CURRENT_TIMESTAMP WHERE id=?",
        (reason, replacement, _now_iso(), doc["id"]),
    )
    after = _fiscal_document(con, doc["id"])
    _event(con, "fiscal.external_cancellation_requested", "fiscal_document", doc["humanCode"], doc["clientId"], f"Cancelacion externa solicitada localmente: {doc['humanCode']}", {"reason": reason, "replacementUuid": replacement, "liveCancellation": False})
    return {"ok": True, "idempotent": False, "document": after, "gateway": gateway_status(issuer_profile(con)), "message": "Solicitud registrada; PRISMA no envio cancelacion a SAT/PAC."}


def register_external_cancellation_result(con: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    doc = _fiscal_document(con, body.get("documentCode") or body.get("documentId"))
    if doc.get("status") == "cancelled":
        return {"ok": True, "idempotent": True, "document": doc, "message": "Cancelacion externa ya registrada."}
    if doc.get("status") != "cancel_requested":
        raise BillingError("BILLING_CFDI_CANCEL_RESULT_WITHOUT_REQUEST", "Primero registra la solicitud local de cancelacion.")
    evidence = str(body.get("evidenceRef") or "").strip()[:240]
    if not evidence:
        raise BillingError("BILLING_CFDI_CANCEL_EVIDENCE_REQUIRED", "Resultado de cancelacion externa requiere evidencia.")
    accepted = body.get("cancelled") is True
    status = "cancelled" if accepted else "cancellation_rejected"
    con.execute(
        "UPDATE CommercialFiscalDocument SET status=?,cancellationEvidenceRef=?,cancelledAt=?,lastErrorCode=?,updatedAt=CURRENT_TIMESTAMP WHERE id=?",
        (status, evidence, _now_iso() if accepted else None, None if accepted else str(body.get("resultCode") or "EXTERNAL_CANCELLATION_REJECTED")[:120], doc["id"]),
    )
    after = _fiscal_document(con, doc["id"])
    _event(con, "fiscal.external_cancellation_result", "fiscal_document", doc["humanCode"], doc["clientId"], f"Resultado cancelacion externa: {status} {doc['humanCode']}", {"status": status, "evidenceRef": evidence, "liveCancellationByPrisma": False})
    return {"ok": True, "idempotent": False, "document": after, "message": "Resultado externo de cancelacion registrado."}


def reconcile_billing(con: sqlite3.Connection, *, as_of: Any = None, mutate_status: bool = False) -> dict[str, Any]:
    target = _today(as_of)
    rows = [dict(row) for row in con.execute("SELECT * FROM CommercialCharge ORDER BY dueOn,createdAt")]
    aging = {"current": 0, "1_30": 0, "31_60": 0, "61_90": 0, "90_plus": 0}
    outstanding = 0
    overdue = 0
    for item in rows:
        if item.get("status") == "void":
            continue
        paid = _active_allocated_for_charge(con, item["id"])
        total = int(item.get("totalCents") or 0)
        balance = max(total - paid, 0)
        item["paidCents"] = paid
        item["balanceCents"] = balance
        state = _derived_charge_state(item, as_of=target)
        item["derivedStatus"] = state
        if mutate_status:
            con.execute("UPDATE CommercialCharge SET paidCents=?,balanceCents=?,status=?,updatedAt=CURRENT_TIMESTAMP WHERE id=?", (paid, balance, state, item["id"]))
        outstanding += balance
        if balance <= 0:
            continue
        days = (target - _today(item["dueOn"])).days
        if days <= 0:
            aging["current"] += balance
        elif days <= 30:
            aging["1_30"] += balance
            overdue += balance
        elif days <= 60:
            aging["31_60"] += balance
            overdue += balance
        elif days <= 90:
            aging["61_90"] += balance
            overdue += balance
        else:
            aging["90_plus"] += balance
            overdue += balance
    payments = [dict(row) for row in con.execute("SELECT * FROM CommercialPayment WHERE status='posted'")]
    collected = sum(int(item.get("amountCents") or 0) for item in payments)
    allocated = sum(int(item.get("allocatedCents") or 0) for item in payments)
    unapplied = sum(int(item.get("unappliedCents") or 0) for item in payments)
    return {
        "asOf": target.isoformat(),
        "outstandingCents": outstanding,
        "overdueCents": overdue,
        "collectedCents": collected,
        "allocatedCents": allocated,
        "unappliedCents": unapplied,
        "agingCents": aging,
        "chargeCount": len(rows),
        "postedPaymentCount": len(payments),
        "pastDueDoesNotSuspendLicense": True,
    }


def _list_rows(con: sqlite3.Connection, query: str, args: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(row) for row in con.execute(query, args).fetchall()]


def billing_counts(con: sqlite3.Connection) -> dict[str, int]:
    return {
        "fiscalProfiles": int(con.execute("SELECT COUNT(*) FROM CommercialFiscalProfile").fetchone()[0]),
        "charges": int(con.execute("SELECT COUNT(*) FROM CommercialCharge").fetchone()[0]),
        "payments": int(con.execute("SELECT COUNT(*) FROM CommercialPayment WHERE status='posted'").fetchone()[0]),
        "receipts": int(con.execute("SELECT COUNT(*) FROM CommercialReceipt WHERE status='issued'").fetchone()[0]),
        "fiscalDocuments": int(con.execute("SELECT COUNT(*) FROM CommercialFiscalDocument").fetchone()[0]),
        "stampedDocuments": int(con.execute("SELECT COUNT(*) FROM CommercialFiscalDocument WHERE status='external_stamped'").fetchone()[0]),
        "billingEvents": int(con.execute("SELECT COUNT(*) FROM CommercialBillingEvent").fetchone()[0]),
    }


def billing_local_payload(con: sqlite3.Connection) -> dict[str, Any]:
    fiscal_profiles = _list_rows(con, "SELECT fp.*,c.humanCode AS clientCode,c.displayName AS clientName FROM CommercialFiscalProfile fp LEFT JOIN CommandClient c ON c.id=fp.clientId ORDER BY fp.updatedAt DESC LIMIT 50")
    charges = _list_rows(con, "SELECT bc.*,c.humanCode AS clientCode,c.displayName AS clientName,cc.humanCode AS contractCode,cc.planCode,cc.billingPeriod,cc.priceVersion FROM CommercialCharge bc LEFT JOIN CommandClient c ON c.id=bc.clientId LEFT JOIN CommercialContract cc ON cc.id=bc.contractId ORDER BY bc.createdAt DESC LIMIT 80")
    for item in charges:
        item["derivedStatus"] = _derived_charge_state(item)
    payments = _list_rows(con, "SELECT p.*,c.humanCode AS clientCode,c.displayName AS clientName FROM CommercialPayment p LEFT JOIN CommandClient c ON c.id=p.clientId ORDER BY p.receivedAt DESC LIMIT 80")
    receipts = _list_rows(con, "SELECT r.*,p.humanCode AS paymentCode,c.humanCode AS clientCode,c.displayName AS clientName FROM CommercialReceipt r LEFT JOIN CommercialPayment p ON p.id=r.paymentId LEFT JOIN CommandClient c ON c.id=r.clientId ORDER BY r.issuedAt DESC LIMIT 80")
    docs = _list_rows(con, "SELECT d.id,d.internalId,d.humanCode,d.kind,d.status,d.clientId,d.chargeId,d.paymentId,d.cfdiVersion,d.complementVersion,d.methodCode,d.paymentForm,d.currency,d.subtotalCents,d.taxCents,d.totalCents,d.uuid,d.provider,d.providerEvidenceRef,d.xmlSha256,d.pdfRef,d.stampedAt,d.parentUuid,d.cancellationReason,d.replacementUuid,d.cancellationEvidenceRef,d.cancelRequestedAt,d.cancelledAt,d.lastErrorCode,d.createdAt,d.updatedAt,c.humanCode AS clientCode,c.displayName AS clientName FROM CommercialFiscalDocument d LEFT JOIN CommandClient c ON c.id=d.clientId ORDER BY d.createdAt DESC LIMIT 80")
    events = _list_rows(con, "SELECT * FROM CommercialBillingEvent ORDER BY createdAt DESC LIMIT 80")
    return {
        "fiscalProfiles": fiscal_profiles,
        "charges": charges,
        "payments": payments,
        "commercialReceipts": receipts,
        "fiscalDocuments": docs,
        "billingEvents": events,
    }


def billing_snapshot(con: sqlite3.Connection, *, as_of: Any = None) -> dict[str, Any]:
    issuer = issuer_profile(con)
    local = billing_local_payload(con)
    return {
        "modelVersion": BILLING_MODEL_VERSION,
        "mode": "LOCAL_COMMERCIAL_LEDGER_EXTERNAL_MONEY_AND_FISCAL_MUTATION",
        "moneyProcessing": False,
        "bankValidation": False,
        "cardCapture": False,
        "speiValidation": False,
        "automaticBankReconciliation": False,
        "licenseAutoSuspension": False,
        "defaultTaxRateBps": DEFAULT_TAX_RATE_BPS,
        "defaultTaxRateSource": DEFAULT_TAX_RATE_SOURCE,
        "defaultDuePolicy": DEFAULT_DUE_POLICY,
        "reconciliation": reconcile_billing(con, as_of=as_of, mutate_status=False),
        "counts": billing_counts(con),
        "issuer": issuer,
        "gateway": gateway_status(issuer),
        "local": local,
    }


def billing_command(
    con: sqlite3.Connection,
    raw_path: str,
    method: str,
    body: dict[str, Any] | None,
    id_factory: Callable[[sqlite3.Connection, str, Any], dict[str, Any]],
) -> dict[str, Any]:
    ensure_billing_schema(con)
    payload = body if isinstance(body, dict) else {}
    path = raw_path.rstrip("/")
    try:
        if method == "GET" and path in {"/api/command-center/billing", "/api/command-center/billing/snapshot"}:
            return {"ok": True, **billing_snapshot(con, as_of=payload.get("asOf"))}
        if method == "POST" and path == "/api/command-center/billing/receiver-profile":
            return save_receiver_profile(con, payload)
        if method == "POST" and path == "/api/command-center/billing/issuer-profile":
            return save_issuer_profile(con, payload)
        if method == "POST" and path == "/api/command-center/billing/create-charge":
            return create_charge(con, payload, id_factory)
        if method == "POST" and path == "/api/command-center/billing/void-charge":
            return void_charge(con, payload)
        if method == "POST" and path == "/api/command-center/billing/register-payment":
            return register_external_payment(con, payload, id_factory)
        if method == "POST" and path == "/api/command-center/billing/reverse-payment":
            return reverse_external_payment(con, payload)
        if method == "POST" and path == "/api/command-center/billing/prepare-income-cfdi":
            return prepare_income_cfdi(con, payload, id_factory)
        if method == "POST" and path == "/api/command-center/billing/register-external-stamp":
            return register_external_stamp(con, payload)
        if method == "POST" and path == "/api/command-center/billing/prepare-payment-complement":
            return prepare_payment_complement(con, payload, id_factory)
        if method == "POST" and path == "/api/command-center/billing/request-cancellation":
            return request_cfdi_cancellation(con, payload)
        if method == "POST" and path == "/api/command-center/billing/register-cancellation-result":
            return register_external_cancellation_result(con, payload)
        if method == "POST" and path == "/api/command-center/billing/reconcile":
            result = reconcile_billing(con, as_of=payload.get("asOf"), mutate_status=True)
            _event(con, "billing.reconciled", "billing", "BILLING", None, f"Cobranza reconciliada al {result['asOf']}", result)
            return {"ok": True, "reconciliation": result, "message": "Estados de cobranza reconciliados; no se modificaron licencias ni dinero."}
    except BillingError:
        raise
    except FiscalGatewayError as exc:
        raise BillingError(exc.code, str(exc)) from exc
    return {"ok": False, "resultCode": "BILLING_ROUTE_NOT_FOUND", "path": path, "method": method, "_httpStatus": 404}
