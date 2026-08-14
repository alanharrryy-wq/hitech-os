# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from datetime import datetime
from typing import Any


class FiscalGatewayError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


CFDI_VERSION = "4.0"
PAYMENT_COMPLEMENT_VERSION = "2.0"

SAT_CANCELLATION_REASONS = {
    "01": "Comprobantes emitidos con errores con relacion",
    "02": "Comprobantes emitidos con errores sin relacion",
    "03": "No se llevo a cabo la operacion",
    "04": "Operacion nominativa relacionada en una factura global",
}

PAYMENT_FORM_LABELS = {
    "01": "Efectivo",
    "02": "Cheque nominativo",
    "03": "Transferencia electronica de fondos",
    "04": "Tarjeta de credito",
    "28": "Tarjeta de debito",
    "99": "Por definir",
}


def money_text(cents: int) -> str:
    value = int(cents or 0)
    sign = "-" if value < 0 else ""
    value = abs(value)
    return f"{sign}{value // 100}.{value % 100:02d}"


def tax_rate_text(rate_bps: int) -> str:
    return f"{int(rate_bps or 0) / 10000:.6f}"


def cfdi_draft_datetime() -> str:
    return datetime.now().replace(microsecond=0).isoformat(timespec="seconds")


def normalize_payment_form(value: Any, *, allow_undefined: bool = False) -> str:
    code = str(value or "").strip()
    if not re.fullmatch(r"\d{2}", code):
        raise FiscalGatewayError("CFDI_PAYMENT_FORM_INVALID", "Forma de pago debe ser una clave SAT de dos digitos.")
    if code == "99" and not allow_undefined:
        raise FiscalGatewayError("CFDI_PAYMENT_FORM_UNDEFINED_FOR_RECEIVED_PAYMENT", "Un pago ya recibido no puede registrarse con forma 99 Por definir.")
    return code


def validate_cfdi_uuid(value: Any) -> str:
    uuid = str(value or "").strip().upper()
    if not re.fullmatch(r"[0-9A-F]{8}-[0-9A-F]{4}-[1-5][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}", uuid):
        raise FiscalGatewayError("CFDI_UUID_INVALID", "UUID fiscal invalido.")
    return uuid


def validate_sha256(value: Any) -> str | None:
    digest = str(value or "").strip().lower()
    if not digest:
        return None
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise FiscalGatewayError("CFDI_XML_SHA256_INVALID", "xmlSha256 debe contener 64 caracteres hexadecimales.")
    return digest


def gateway_status(issuer: dict[str, Any] | None) -> dict[str, Any]:
    issuer = issuer or {}
    mode = str(issuer.get("providerMode") or "not_configured")
    provider = str(issuer.get("providerName") or "").strip() or None
    return {
        "mode": mode,
        "provider": provider,
        "issuerStatus": issuer.get("status") or "missing",
        "csdState": issuer.get("csdState") or "not_configured",
        "cfdiVersion": CFDI_VERSION,
        "paymentComplementVersion": PAYMENT_COMPLEMENT_VERSION,
        "liveStampingAllowed": False,
        "liveCancellationAllowed": False,
        "secretsExposed": False,
        "boundary": "EXTERNAL_SAT_OR_AUTHORIZED_PAC_REQUIRED",
        "supportedLocalActions": [
            "prepare_cfdi_draft",
            "prepare_payment_complement_draft",
            "register_external_stamp_result",
            "request_external_cancellation",
            "register_external_cancellation_result",
        ],
    }


def fiscal_prerequisites(issuer: dict[str, Any] | None, receiver: dict[str, Any] | None, charge: dict[str, Any] | None) -> list[str]:
    issuer = issuer or {}
    receiver = receiver or {}
    charge = charge or {}
    missing: list[str] = []
    if issuer.get("status") != "operator_confirmed":
        missing.append("issuer_profile_operator_confirmed")
    for key in ("issuerRfc", "legalName", "postalCode", "fiscalRegime", "productServiceCode", "unitCode", "taxObjectCode"):
        if not issuer.get(key):
            missing.append(f"issuer.{key}")
    if receiver.get("status") != "operator_confirmed":
        missing.append("receiver_fiscal_profile_operator_confirmed")
    for key in ("rfc", "legalName", "postalCode", "fiscalRegime", "cfdiUse"):
        if not receiver.get(key):
            missing.append(f"receiver.{key}")
    if not charge:
        missing.append("charge")
    elif not bool(charge.get("taxConfirmed")):
        missing.append("charge.taxConfirmed")
    return missing


def _income_method_and_form(charge: dict[str, Any], posted_allocations: list[dict[str, Any]], payment_rows: dict[str, dict[str, Any]]) -> tuple[str, str]:
    total = int(charge.get("totalCents") or 0)
    paid = int(charge.get("paidCents") or 0)
    if total > 0 and paid >= total and len(posted_allocations) == 1:
        payment = payment_rows.get(str(posted_allocations[0].get("paymentId"))) or {}
        if int(posted_allocations[0].get("amountCents") or 0) >= total and payment.get("status") == "posted":
            return "PUE", normalize_payment_form(payment.get("paymentForm"))
    return "PPD", "99"


def build_income_cfdi_draft(
    *,
    charge: dict[str, Any],
    contract: dict[str, Any],
    issuer: dict[str, Any] | None,
    receiver: dict[str, Any] | None,
    posted_allocations: list[dict[str, Any]],
    payment_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    missing = fiscal_prerequisites(issuer, receiver, charge)
    issuer = issuer or {}
    receiver = receiver or {}
    method, form = _income_method_and_form(charge, posted_allocations, payment_rows)
    subtotal = int(charge.get("subtotalCents") or 0)
    tax = int(charge.get("taxCents") or 0)
    total = int(charge.get("totalCents") or 0)
    rate_bps = int(charge.get("taxRateBps") or 0)
    concept: dict[str, Any] = {
        "ClaveProdServ": issuer.get("productServiceCode"),
        "NoIdentificacion": f"PRISMA-{contract.get('planCode') or 'LICENSE'}-{contract.get('billingPeriod') or 'PERIOD'}",
        "Cantidad": "1",
        "ClaveUnidad": issuer.get("unitCode"),
        "Unidad": issuer.get("unitName") or "Servicio",
        "Descripcion": f"Licencia PRISMA {contract.get('planLabel') or contract.get('planCode') or ''} - {contract.get('billingPeriod') or ''}".strip(),
        "ValorUnitario": money_text(subtotal),
        "Importe": money_text(subtotal),
        "ObjetoImp": issuer.get("taxObjectCode"),
    }
    if tax > 0:
        concept["Impuestos"] = {
            "Traslados": [{
                "Base": money_text(subtotal),
                "Impuesto": issuer.get("taxCode") or "002",
                "TipoFactor": "Tasa",
                "TasaOCuota": tax_rate_text(rate_bps),
                "Importe": money_text(tax),
            }]
        }
    draft = {
        "standard": "SAT_CFDI_4_0_DRAFT_NOT_XML",
        "Version": CFDI_VERSION,
        "Fecha": cfdi_draft_datetime(),
        "TipoDeComprobante": "I",
        "Exportacion": issuer.get("exportCode") or "01",
        "Moneda": charge.get("currency") or "MXN",
        "SubTotal": money_text(subtotal),
        "Total": money_text(total),
        "MetodoPago": method,
        "FormaPago": form,
        "LugarExpedicion": issuer.get("postalCode"),
        "Emisor": {
            "Rfc": issuer.get("issuerRfc"),
            "Nombre": issuer.get("legalName"),
            "RegimenFiscal": issuer.get("fiscalRegime"),
        },
        "Receptor": {
            "Rfc": receiver.get("rfc"),
            "Nombre": receiver.get("legalName"),
            "DomicilioFiscalReceptor": receiver.get("postalCode"),
            "RegimenFiscalReceptor": receiver.get("fiscalRegime"),
            "UsoCFDI": receiver.get("cfdiUse"),
        },
        "Conceptos": [concept],
        "Impuestos": ({
            "TotalImpuestosTrasladados": money_text(tax),
            "Traslados": [{
                "Base": money_text(subtotal),
                "Impuesto": issuer.get("taxCode") or "002",
                "TipoFactor": "Tasa",
                "TasaOCuota": tax_rate_text(rate_bps),
                "Importe": money_text(tax),
            }],
        } if tax > 0 else None),
        "commercialTrace": {
            "contractCode": contract.get("humanCode"),
            "chargeCode": charge.get("humanCode"),
            "priceVersion": contract.get("priceVersion"),
            "priceSource": contract.get("priceSource"),
        },
    }
    return {
        "ready": not missing,
        "missingPrerequisites": missing,
        "method": method,
        "paymentForm": form,
        "draft": draft,
    }


def proportional_tax_split(allocation_cents: int, charge: dict[str, Any]) -> tuple[int, int]:
    allocation = int(allocation_cents or 0)
    total = int(charge.get("totalCents") or 0)
    subtotal = int(charge.get("subtotalCents") or 0)
    if allocation <= 0 or total <= 0:
        return 0, 0
    base = int((allocation * subtotal + total // 2) // total)
    tax = allocation - base
    return base, tax


def build_payment_complement_draft(
    *,
    payment: dict[str, Any],
    allocations: list[dict[str, Any]],
    charges: dict[str, dict[str, Any]],
    income_documents: dict[str, dict[str, Any]],
    issuer: dict[str, Any] | None,
    receiver: dict[str, Any] | None,
) -> dict[str, Any]:
    issuer = issuer or {}
    receiver = receiver or {}
    missing: list[str] = []
    if issuer.get("status") != "operator_confirmed":
        missing.append("issuer_profile_operator_confirmed")
    if receiver.get("status") != "operator_confirmed":
        missing.append("receiver_fiscal_profile_operator_confirmed")
    if payment.get("status") != "posted":
        missing.append("payment.posted")
    if not allocations:
        missing.append("payment.allocations")
    tax_rates = {int((charges.get(str(item.get("chargeId"))) or {}).get("taxRateBps") or 0) for item in allocations}
    if len(tax_rates) > 1:
        missing.append("payment.multipleTaxRatesRequiresExternalFiscalResolver")

    docs: list[dict[str, Any]] = []
    payment_tax_base = 0
    payment_tax = 0
    for allocation in allocations:
        charge_id = str(allocation.get("chargeId") or "")
        charge = charges.get(charge_id) or {}
        income = income_documents.get(charge_id) or {}
        uuid = income.get("uuid") if income.get("status") == "external_stamped" else None
        if not uuid:
            missing.append(f"charge.{charge.get('humanCode') or charge_id}.parentCfdiUuid")
        base_paid, tax_paid = proportional_tax_split(int(allocation.get("amountCents") or 0), charge)
        payment_tax_base += base_paid
        payment_tax += tax_paid
        rate_bps = int(charge.get("taxRateBps") or 0)
        tax_object = issuer.get("taxObjectCode") or "02"
        related: dict[str, Any] = {
            "IdDocumento": uuid,
            "MonedaDR": charge.get("currency") or "MXN",
            "NumParcialidad": str(int(allocation.get("partialityNumber") or 1)),
            "ImpSaldoAnt": money_text(int(allocation.get("balanceBeforeCents") or 0)),
            "ImpPagado": money_text(int(allocation.get("amountCents") or 0)),
            "ImpSaldoInsoluto": money_text(int(allocation.get("balanceAfterCents") or 0)),
            "ObjetoImpDR": tax_object,
        }
        if tax_paid > 0:
            related["ImpuestosDR"] = {
                "TrasladosDR": [{
                    "BaseDR": money_text(base_paid),
                    "ImpuestoDR": issuer.get("taxCode") or "002",
                    "TipoFactorDR": "Tasa",
                    "TasaOCuotaDR": tax_rate_text(rate_bps),
                    "ImporteDR": money_text(tax_paid),
                }]
            }
        docs.append(related)

    payment_form = None
    try:
        payment_form = normalize_payment_form(payment.get("paymentForm"))
    except FiscalGatewayError as exc:
        missing.append(exc.code)

    payment_node: dict[str, Any] = {
        "FechaPago": payment.get("receivedAt"),
        "FormaDePagoP": payment_form,
        "MonedaP": payment.get("currency") or "MXN",
        "Monto": money_text(int(payment.get("amountCents") or 0)),
        "DoctoRelacionado": docs,
    }
    if payment_tax > 0 and len(tax_rates) <= 1:
        rate_bps = next(iter(tax_rates), 0)
        payment_node["ImpuestosP"] = {
            "TrasladosP": [{
                "BaseP": money_text(payment_tax_base),
                "ImpuestoP": issuer.get("taxCode") or "002",
                "TipoFactorP": "Tasa",
                "TasaOCuotaP": tax_rate_text(rate_bps),
                "ImporteP": money_text(payment_tax),
            }]
        }

    draft = {
        "standard": "SAT_CFDI_4_0_PAGOS_2_0_DRAFT_NOT_XML",
        "Version": CFDI_VERSION,
        "Fecha": cfdi_draft_datetime(),
        "TipoDeComprobante": "P",
        "Exportacion": "01",
        "Moneda": "XXX",
        "SubTotal": "0.00",
        "Total": "0.00",
        "LugarExpedicion": issuer.get("postalCode"),
        "Emisor": {
            "Rfc": issuer.get("issuerRfc"),
            "Nombre": issuer.get("legalName"),
            "RegimenFiscal": issuer.get("fiscalRegime"),
        },
        "Receptor": {
            "Rfc": receiver.get("rfc"),
            "Nombre": receiver.get("legalName"),
            "DomicilioFiscalReceptor": receiver.get("postalCode"),
            "RegimenFiscalReceptor": receiver.get("fiscalRegime"),
            "UsoCFDI": "CP01",
        },
        "Conceptos": [{
            "ClaveProdServ": "84111506",
            "Cantidad": "1",
            "ClaveUnidad": "ACT",
            "Descripcion": "Pago",
            "ValorUnitario": "0",
            "Importe": "0",
            "ObjetoImp": "01",
        }],
        "Complemento": {
            "Pagos20": {
                "Version": PAYMENT_COMPLEMENT_VERSION,
                "Totales": {
                    "MontoTotalPagos": money_text(int(payment.get("amountCents") or 0)),
                    "TotalTrasladosBaseIVA16": money_text(payment_tax_base) if payment_tax else None,
                    "TotalTrasladosImpuestoIVA16": money_text(payment_tax) if payment_tax else None,
                },
                "Pago": [payment_node],
            }
        },
        "commercialTrace": {
            "paymentCode": payment.get("humanCode"),
            "receiptCode": payment.get("receiptCode"),
        },
    }
    return {"ready": not missing, "missingPrerequisites": sorted(set(missing)), "draft": draft}


def validate_cancellation_request(reason: Any, replacement_uuid: Any = None) -> tuple[str, str | None]:
    code = str(reason or "").strip()
    if code not in SAT_CANCELLATION_REASONS:
        raise FiscalGatewayError("CFDI_CANCELLATION_REASON_INVALID", "Motivo de cancelacion debe ser 01, 02, 03 o 04.")
    replacement = None
    if code == "01":
        replacement = validate_cfdi_uuid(replacement_uuid)
    elif replacement_uuid:
        replacement = validate_cfdi_uuid(replacement_uuid)
    return code, replacement
