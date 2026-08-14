#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BILLING = ROOT / "Prisma Cloud Ctr" / "internal" / "py" / "commercial_billing.py"
CFDI = ROOT / "Prisma Cloud Ctr" / "internal" / "py" / "cfdi_gateway.py"
HTTP = ROOT / "Prisma Cloud Ctr" / "internal" / "py" / "prisma_unified_lab_v3.py"
VERIFY = ROOT / "tools" / "verify-commercial-billing-cfdi-01.py"
DOC = ROOT / "docs" / "productization" / "PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_billing() -> None:
    text = BILLING.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '"CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_income_active_idx ON CommercialFiscalDocument(chargeId,kind) WHERE kind=\'CFDI_INGRESO\' AND status!=\'cancelled\'",',
        '"CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_income_active_idx ON CommercialFiscalDocument(chargeId,kind) WHERE kind=\'CFDI_INGRESO\' AND status NOT IN (\'cancelled\',\'discarded\')",',
        "income active index excludes discarded",
    )
    text = replace_once(
        text,
        '"CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_payment_active_idx ON CommercialFiscalDocument(paymentId,kind) WHERE kind=\'CFDI_PAGO\' AND status!=\'cancelled\'",',
        '"CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_payment_active_idx ON CommercialFiscalDocument(paymentId,kind) WHERE kind=\'CFDI_PAGO\' AND status NOT IN (\'cancelled\',\'discarded\')",',
        "payment active index excludes discarded",
    )
    text = replace_once(
        text,
        'existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE chargeId=? AND kind=\'CFDI_INGRESO\' AND status!=\'cancelled\' ORDER BY createdAt DESC,id DESC LIMIT 1", (charge["id"],)).fetchone()',
        'existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE chargeId=? AND kind=\'CFDI_INGRESO\' AND status NOT IN (\'cancelled\',\'discarded\') ORDER BY createdAt DESC,id DESC LIMIT 1", (charge["id"],)).fetchone()',
        "income active lookup excludes discarded",
    )
    text = replace_once(
        text,
        'existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE paymentId=? AND kind=\'CFDI_PAGO\' AND status!=\'cancelled\' ORDER BY createdAt DESC,id DESC LIMIT 1", (payment["id"],)).fetchone()',
        'existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE paymentId=? AND kind=\'CFDI_PAGO\' AND status NOT IN (\'cancelled\',\'discarded\') ORDER BY createdAt DESC,id DESC LIMIT 1", (payment["id"],)).fetchone()',
        "payment active lookup excludes discarded",
    )

    old_void = '''    if fiscal:\n        raise BillingError("BILLING_VOID_BLOCKED_BY_CFDI", "El cargo tiene CFDI timbrado/no cancelado; usa primero la ruta fiscal de cancelacion.", details=dict(fiscal))\n    con.execute("UPDATE CommercialCharge SET status='void',voidReason=?,balanceCents=0,updatedAt=CURRENT_TIMESTAMP WHERE id=?", (reason, charge["id"]))\n    _event(con, "billing.charge_voided", "charge", charge["humanCode"], charge["clientId"], f"Cargo anulado: {charge['humanCode']}", {"reason": reason})\n'''
    new_void = '''    if fiscal:\n        raise BillingError("BILLING_VOID_BLOCKED_BY_CFDI", "El cargo tiene CFDI timbrado/no cancelado; usa primero la ruta fiscal de cancelacion.", details=dict(fiscal))\n    discarded_drafts = con.execute(\n        "UPDATE CommercialFiscalDocument SET status='discarded',lastErrorCode='CHARGE_VOIDED_BEFORE_EXTERNAL_STAMP',updatedAt=CURRENT_TIMESTAMP "\n        "WHERE chargeId=? AND kind='CFDI_INGRESO' AND status IN ('draft_blocked','ready_to_stamp')",\n        (charge["id"],),\n    ).rowcount\n    con.execute("UPDATE CommercialCharge SET status='void',voidReason=?,balanceCents=0,updatedAt=CURRENT_TIMESTAMP WHERE id=?", (reason, charge["id"]))\n    _event(con, "billing.charge_voided", "charge", charge["humanCode"], charge["clientId"], f"Cargo anulado: {charge['humanCode']}", {"reason": reason, "discardedFiscalDrafts": discarded_drafts})\n'''
    text = replace_once(text, old_void, new_void, "void discards unstamped income draft")

    old_reverse = '''    if stamped:\n        raise BillingError("BILLING_PAYMENT_REVERSE_BLOCKED_BY_CFDI", "Hay Complemento de Pagos timbrado/no cancelado; cancela fiscalmente antes de revertir el registro.", details=dict(stamped))\n    allocations = [dict(r) for r in con.execute("SELECT * FROM CommercialPaymentAllocation WHERE paymentId=? AND status='posted'", (payment["id"],))]\n    con.execute("UPDATE CommercialPaymentAllocation SET status='reversed',updatedAt=CURRENT_TIMESTAMP WHERE paymentId=? AND status='posted'", (payment["id"],))\n'''
    new_reverse = '''    if stamped:\n        raise BillingError("BILLING_PAYMENT_REVERSE_BLOCKED_BY_CFDI", "Hay Complemento de Pagos timbrado/no cancelado; cancela fiscalmente antes de revertir el registro.", details=dict(stamped))\n    pue_income = con.execute(\n        "SELECT d.humanCode,d.status,d.uuid,c.humanCode AS chargeCode FROM CommercialPaymentAllocation a "\n        "JOIN CommercialCharge c ON c.id=a.chargeId "\n        "JOIN CommercialFiscalDocument d ON d.chargeId=a.chargeId "\n        "WHERE a.paymentId=? AND a.status='posted' AND d.kind='CFDI_INGRESO' AND d.methodCode='PUE' "\n        "AND d.status IN ('external_stamped','cancel_requested','cancellation_rejected') LIMIT 1",\n        (payment["id"],),\n    ).fetchone()\n    if pue_income:\n        raise BillingError("BILLING_PAYMENT_REVERSE_BLOCKED_BY_PUE_CFDI", "El pago soporta un CFDI PUE timbrado/no cancelado; cancela fiscalmente ese CFDI antes de revertir el registro.", details=dict(pue_income))\n    allocations = [dict(r) for r in con.execute("SELECT * FROM CommercialPaymentAllocation WHERE paymentId=? AND status='posted'", (payment["id"],))]\n    discarded_drafts = con.execute(\n        "UPDATE CommercialFiscalDocument SET status='discarded',lastErrorCode='PAYMENT_REVERSED_BEFORE_EXTERNAL_STAMP',updatedAt=CURRENT_TIMESTAMP "\n        "WHERE paymentId=? AND kind='CFDI_PAGO' AND status IN ('draft_blocked','ready_to_stamp')",\n        (payment["id"],),\n    ).rowcount\n    con.execute("UPDATE CommercialPaymentAllocation SET status='reversed',updatedAt=CURRENT_TIMESTAMP WHERE paymentId=? AND status='posted'", (payment["id"],))\n'''
    text = replace_once(text, old_reverse, new_reverse, "reverse blocks PUE and discards unstamped complement")
    text = replace_once(
        text,
        '{"reason": reason, "fiscalComplementStamped": False}',
        '{"reason": reason, "fiscalComplementStamped": False, "discardedFiscalDrafts": discarded_drafts}',
        "reverse event discarded count",
    )

    old_stamp = '''    if doc.get("status") != "ready_to_stamp":\n        raise BillingError("BILLING_CFDI_NOT_READY", "El documento no cumple prerequisitos locales para registrar timbrado externo.", details={"status": doc.get("status"), "lastErrorCode": doc.get("lastErrorCode")})\n    try:\n'''
    new_stamp = '''    if doc.get("status") != "ready_to_stamp":\n        raise BillingError("BILLING_CFDI_NOT_READY", "El documento no cumple prerequisitos locales para registrar timbrado externo.", details={"status": doc.get("status"), "lastErrorCode": doc.get("lastErrorCode")})\n    if doc.get("kind") == "CFDI_INGRESO" and doc.get("chargeId"):\n        source = con.execute("SELECT status FROM CommercialCharge WHERE id=?", (doc["chargeId"],)).fetchone()\n        if not source or source["status"] == "void":\n            raise BillingError("BILLING_CFDI_STAMP_SOURCE_INVALIDATED", "El cargo origen fue anulado o ya no existe; el borrador fiscal no puede recibir timbrado externo.")\n    if doc.get("kind") == "CFDI_PAGO" and doc.get("paymentId"):\n        source = con.execute("SELECT status FROM CommercialPayment WHERE id=?", (doc["paymentId"],)).fetchone()\n        if not source or source["status"] != "posted":\n            raise BillingError("BILLING_CFDI_STAMP_SOURCE_INVALIDATED", "El pago origen fue revertido o ya no existe; el borrador fiscal no puede recibir timbrado externo.")\n    try:\n'''
    text = replace_once(text, old_stamp, new_stamp, "stamp source validity guard")

    text = replace_once(
        text,
        'doc_row = con.execute("SELECT * FROM CommercialFiscalDocument WHERE chargeId=? AND kind=\'CFDI_INGRESO\'", (ch["id"],)).fetchone()',
        'doc_row = con.execute("SELECT * FROM CommercialFiscalDocument WHERE chargeId=? AND kind=\'CFDI_INGRESO\' AND status=\'external_stamped\' ORDER BY stampedAt DESC,createdAt DESC,id DESC LIMIT 1", (ch["id"],)).fetchone()',
        "payment complement selects active stamped income",
    )

    old_cancel = '''    if doc.get("status") == "cancelled":\n        return {"ok": True, "idempotent": True, "document": doc, "message": "El CFDI ya figura como cancelado externamente."}\n    if doc.get("status") != "external_stamped":\n        raise BillingError("BILLING_CFDI_CANCEL_NOT_STAMPED", "Solo se solicita cancelacion para CFDI con UUID timbrado registrado.")\n    if body.get("confirmCancellationRequest") is not True:\n        raise BillingError("BILLING_CFDI_CANCEL_CONFIRMATION_REQUIRED", "La solicitud de cancelacion requiere confirmacion explicita.")\n    try:\n        reason, replacement = validate_cancellation_request(body.get("reason"), body.get("replacementUuid"))\n    except FiscalGatewayError as exc:\n        raise BillingError(exc.code, str(exc)) from exc\n'''
    new_cancel = '''    if doc.get("status") == "cancelled":\n        return {"ok": True, "idempotent": True, "document": doc, "message": "El CFDI ya figura como cancelado externamente."}\n    if body.get("confirmCancellationRequest") is not True:\n        raise BillingError("BILLING_CFDI_CANCEL_CONFIRMATION_REQUIRED", "La solicitud de cancelacion requiere confirmacion explicita.")\n    try:\n        reason, replacement = validate_cancellation_request(body.get("reason"), body.get("replacementUuid"))\n    except FiscalGatewayError as exc:\n        raise BillingError(exc.code, str(exc)) from exc\n    if doc.get("status") == "cancel_requested":\n        if doc.get("cancellationReason") == reason and (doc.get("replacementUuid") or None) == replacement:\n            return {"ok": True, "idempotent": True, "document": doc, "gateway": gateway_status(issuer_profile(con)), "message": "La misma solicitud de cancelacion ya estaba registrada."}\n        raise BillingError("BILLING_CFDI_CANCEL_REQUEST_CONFLICT", "Ya existe una solicitud de cancelacion pendiente con datos distintos.", http_status=409)\n    if doc.get("status") not in {"external_stamped", "cancellation_rejected"}:\n        raise BillingError("BILLING_CFDI_CANCEL_NOT_STAMPED", "Solo se solicita/reintenta cancelacion para CFDI timbrado vigente o con rechazo previo.")\n'''
    text = replace_once(text, old_cancel, new_cancel, "cancellation idempotency and rejected retry")

    BILLING.write_text(text, encoding="utf-8")


def patch_cfdi() -> None:
    text = CFDI.read_text(encoding="utf-8")
    text = replace_once(text, "import re\nfrom typing import Any\n", "import re\nfrom datetime import datetime\nfrom typing import Any\n", "cfdi datetime import")
    text = replace_once(
        text,
        '''def tax_rate_text(rate_bps: int) -> str:\n    return f"{int(rate_bps or 0) / 10000:.6f}"\n\n\n''',
        '''def tax_rate_text(rate_bps: int) -> str:\n    return f"{int(rate_bps or 0) / 10000:.6f}"\n\n\ndef cfdi_draft_datetime() -> str:\n    return datetime.now().replace(microsecond=0).isoformat(timespec="seconds")\n\n\n''',
        "cfdi draft datetime helper",
    )
    text = replace_once(
        text,
        '        "Version": CFDI_VERSION,\n        "TipoDeComprobante": "I",\n',
        '        "Version": CFDI_VERSION,\n        "Fecha": cfdi_draft_datetime(),\n        "TipoDeComprobante": "I",\n',
        "income draft Fecha",
    )
    old_taxes = '''        "Conceptos": [concept],\n        "Taxes": {\n            "TotalImpuestosTrasladados": money_text(tax),\n            "rateBps": rate_bps,\n            "taxCode": issuer.get("taxCode") or "002",\n        },\n        "commercialTrace": {\n'''
    new_taxes = '''        "Conceptos": [concept],\n        "Impuestos": ({\n            "TotalImpuestosTrasladados": money_text(tax),\n            "Traslados": [{\n                "Base": money_text(subtotal),\n                "Impuesto": issuer.get("taxCode") or "002",\n                "TipoFactor": "Tasa",\n                "TasaOCuota": tax_rate_text(rate_bps),\n                "Importe": money_text(tax),\n            }],\n        } if tax > 0 else None),\n        "commercialTrace": {\n'''
    text = replace_once(text, old_taxes, new_taxes, "income top-level Impuestos")
    text = replace_once(
        text,
        '    if not allocations:\n        missing.append("payment.allocations")\n\n    docs: list[dict[str, Any]] = []\n',
        '    if not allocations:\n        missing.append("payment.allocations")\n    tax_rates = {int((charges.get(str(item.get("chargeId"))) or {}).get("taxRateBps") or 0) for item in allocations}\n    if len(tax_rates) > 1:\n        missing.append("payment.multipleTaxRatesRequiresExternalFiscalResolver")\n\n    docs: list[dict[str, Any]] = []\n',
        "multi tax rate fail closed",
    )
    text = replace_once(
        text,
        '''    if payment_tax > 0:\n        rate_bps = max((int((charges.get(str(a.get('chargeId'))) or {}).get('taxRateBps') or 0) for a in allocations), default=0)\n        payment_node["ImpuestosP"] = {\n''',
        '''    if payment_tax > 0 and len(tax_rates) <= 1:\n        rate_bps = next(iter(tax_rates), 0)\n        payment_node["ImpuestosP"] = {\n''',
        "single tax rate payment aggregate",
    )
    text = replace_once(
        text,
        '        "Version": CFDI_VERSION,\n        "TipoDeComprobante": "P",\n',
        '        "Version": CFDI_VERSION,\n        "Fecha": cfdi_draft_datetime(),\n        "TipoDeComprobante": "P",\n',
        "payment draft Fecha",
    )
    CFDI.write_text(text, encoding="utf-8")


def patch_http() -> None:
    text = HTTP.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '''                payload = command_center_store.command_center_payload(self.path, method="POST", body=body)\n                self.json_response(payload, code=200 if payload.get("ok") else 409)\n''',
        '''                payload = command_center_store.command_center_payload(self.path, method="POST", body=body)\n                code = int(payload.pop("_httpStatus", 200 if payload.get("ok") else 409))\n                self.json_response(payload, code=code)\n''',
        "command center POST status propagation",
    )
    text = replace_once(
        text,
        '''            payload = command_center_store.command_center_payload(self.path, method="GET")\n            self.json_response(payload, code=200 if payload.get("ok") else 409)\n''',
        '''            payload = command_center_store.command_center_payload(self.path, method="GET")\n            code = int(payload.pop("_httpStatus", 200 if payload.get("ok") else 409))\n            self.json_response(payload, code=code)\n''',
        "command center GET status propagation",
    )
    HTTP.write_text(text, encoding="utf-8")


def patch_verify() -> None:
    text = VERIFY.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '        require(income_q["document"]["paymentForm"] == "99", "PPD invoice must prepare with form 99")\n        ok("income_cfdi_ppd_99_before_payment")\n',
        '        require(income_q["document"]["paymentForm"] == "99", "PPD invoice must prepare with form 99")\n        require(income_q["document"]["draftPayload"].get("Fecha"), "Income CFDI draft missing Fecha")\n        require(income_q["document"]["draftPayload"].get("Impuestos", {}).get("TotalImpuestosTrasladados") == "271.84", "Income CFDI top tax summary incorrect")\n        ok("income_cfdi_ppd_99_before_payment")\n',
        "verify income Fecha and Impuestos",
    )
    old_pue = '''        income_pue_stamp = register_external_stamp(\n            con,\n            {\n                "documentCode": income_pue["document"]["humanCode"],\n                "uuid": "423E4567-E89B-42D3-A456-426614174003",\n                "provider": "PAC_SANDBOX_EXTERNAL",\n                "providerEvidenceRef": "sandbox://stamp/income-pue",\n            },\n        )["document"]\n        request_cfdi_cancellation(con, {"documentCode": income_pue_stamp["humanCode"], "reason": "02", "confirmCancellationRequest": True})\n        register_external_cancellation_result(con, {"documentCode": income_pue_stamp["humanCode"], "cancelled": True, "evidenceRef": "sandbox://cancel/income-pue"})\n        replacement = prepare_income_cfdi(con, {"chargeCode": charge_pue["humanCode"]}, ids)["document"]\n        require(replacement["humanCode"] != income_pue_stamp["humanCode"], "Cancelled CFDI history was overwritten instead of creating replacement attempt")\n        require(con.execute("SELECT COUNT(*) FROM CommercialFiscalDocument WHERE chargeId=? AND kind='CFDI_INGRESO'", (charge_pue["id"],)).fetchone()[0] == 2, "Cancelled fiscal document history not preserved")\n        ok("cancelled_cfdi_is_immutable_and_replacement_is_new_document")\n'''
    new_pue = '''        income_pue_stamp = register_external_stamp(\n            con,\n            {\n                "documentCode": income_pue["document"]["humanCode"],\n                "uuid": "423E4567-E89B-42D3-A456-426614174003",\n                "provider": "PAC_SANDBOX_EXTERNAL",\n                "providerEvidenceRef": "sandbox://stamp/income-pue",\n            },\n        )["document"]\n        expect_billing_error(\n            "BILLING_PAYMENT_REVERSE_BLOCKED_BY_PUE_CFDI",\n            reverse_external_payment,\n            con,\n            {"paymentCode": full_payment["payment"]["humanCode"], "confirmReverse": True, "reason": "must cancel PUE first"},\n        )\n        request_cfdi_cancellation(con, {"documentCode": income_pue_stamp["humanCode"], "reason": "02", "confirmCancellationRequest": True})\n        register_external_cancellation_result(con, {"documentCode": income_pue_stamp["humanCode"], "cancelled": True, "evidenceRef": "sandbox://cancel/income-pue"})\n        replacement = prepare_income_cfdi(con, {"chargeCode": charge_pue["humanCode"]}, ids)["document"]\n        require(replacement["humanCode"] != income_pue_stamp["humanCode"], "Cancelled CFDI history was overwritten instead of creating replacement attempt")\n        reversed_pue_payment = reverse_external_payment(\n            con,\n            {"paymentCode": full_payment["payment"]["humanCode"], "confirmReverse": True, "reason": "sandbox reversal after PUE cancellation"},\n        )\n        require(reversed_pue_payment["payment"]["status"] == "reversed", "PUE payment could not be reversed after CFDI cancellation")\n        discarded_replacement = con.execute("SELECT status,lastErrorCode FROM CommercialFiscalDocument WHERE id=?", (replacement["id"],)).fetchone()\n        require(discarded_replacement["status"] == "discarded", "Unstamped replacement draft was not discarded when source payment reversed")\n        require(discarded_replacement["lastErrorCode"] == "PAYMENT_REVERSED_BEFORE_EXTERNAL_STAMP", "Discard reason missing for reversed-payment fiscal draft")\n        post_reverse = prepare_income_cfdi(con, {"chargeCode": charge_pue["humanCode"]}, ids)["document"]\n        require(post_reverse["humanCode"] not in {income_pue_stamp["humanCode"], replacement["humanCode"]}, "New fiscal draft did not get immutable new identity after cancellation/discard")\n        require(post_reverse["methodCode"] == "PPD" and post_reverse["paymentForm"] == "99", "Post-reversal income draft must return to PPD/99")\n        require(con.execute("SELECT COUNT(*) FROM CommercialFiscalDocument WHERE chargeId=? AND kind='CFDI_INGRESO'", (charge_pue["id"],)).fetchone()[0] == 3, "Cancelled/discarded fiscal document history not preserved")\n        ok("pue_reversal_requires_cancellation_and_discards_stale_draft")\n'''
    text = replace_once(text, old_pue, new_pue, "verify PUE reversal integrity")
    old_void = '''        contract_void = make_contract(con, "TABLET_SOLO", "monthly", 4, 4, "2026-08-20")\n        charge_void = create_charge(con, {"contractCode": contract_void["humanCode"], "taxRateBps": 1600, "confirmTax": True}, ids)["charge"]\n        voided = void_charge(con, {"chargeCode": charge_void["humanCode"], "confirmVoid": True, "reason": "sandbox void without payment"})["charge"]\n        require(voided["status"] == "void", "Unpaid charge void failed")\n        ok("void_preserves_history")\n'''
    new_void = '''        contract_void = make_contract(con, "TABLET_SOLO", "monthly", 4, 4, "2026-08-20")\n        charge_void = create_charge(con, {"contractCode": contract_void["humanCode"], "taxRateBps": 1600, "confirmTax": True}, ids)["charge"]\n        void_draft = prepare_income_cfdi(con, {"chargeCode": charge_void["humanCode"]}, ids)["document"]\n        require(void_draft["status"] == "ready_to_stamp", "Void scenario expected a ready draft before void")\n        voided = void_charge(con, {"chargeCode": charge_void["humanCode"], "confirmVoid": True, "reason": "sandbox void without payment"})["charge"]\n        require(voided["status"] == "void", "Unpaid charge void failed")\n        void_doc = con.execute("SELECT status,lastErrorCode FROM CommercialFiscalDocument WHERE id=?", (void_draft["id"],)).fetchone()\n        require(void_doc["status"] == "discarded", "Voided charge did not discard unstamped CFDI draft")\n        expect_billing_error(\n            "BILLING_CFDI_NOT_READY",\n            register_external_stamp,\n            con,\n            {"documentCode": void_draft["humanCode"], "uuid": "623E4567-E89B-42D3-A456-426614174005", "provider": "PAC_SANDBOX_EXTERNAL", "providerEvidenceRef": "sandbox://must-not-stamp"},\n        )\n        ok("void_discards_unstamped_fiscal_draft_and_prevents_late_stamp")\n'''
    text = replace_once(text, old_void, new_void, "verify void stale draft guard")
    text = replace_once(
        text,
        '        require(complement_payload["TipoDeComprobante"] == "P", "Payment complement top CFDI type must be P")\n',
        '        require(complement_payload["TipoDeComprobante"] == "P", "Payment complement top CFDI type must be P")\n        require(complement_payload.get("Fecha"), "Payment complement draft missing Fecha")\n',
        "verify payment Fecha",
    )
    text = replace_once(
        text,
        '        for marker in (\n            \'["billing", "Cobranza"\',\n',
        '        http_source = (ROOT / "Prisma Cloud Ctr" / "internal" / "py" / "prisma_unified_lab_v3.py").read_text(encoding="utf-8")\n        require(\'payload.pop("_httpStatus"\' in http_source, "Command Center HTTP handler does not propagate structured billing status codes")\n        ok("command_center_http_status_propagation")\n\n        for marker in (\n            \'["billing", "Cobranza"\',\n',
        "verify HTTP status source marker",
    )
    VERIFY.write_text(text, encoding="utf-8")


def patch_doc() -> None:
    text = DOC.read_text(encoding="utf-8")
    marker = "<!-- PRISMA:BILLING_INTEGRITY_HARDENING:BEGIN -->"
    if marker in text:
        raise SystemExit("Billing integrity hardening doc block already exists")
    block = '''\n\n<!-- PRISMA:BILLING_INTEGRITY_HARDENING:BEGIN -->\n## 23. Integridad entre pago, cargo y evidencia fiscal\n\nReglas adicionales fail-closed:\n\n- Un pago que soporta un CFDI de ingreso `PUE` timbrado/no cancelado no puede revertirse hasta resolver la cancelacion fiscal externa.\n- Revertir un pago descarta cualquier borrador `CFDI_PAGO` no timbrado asociado; nunca queda disponible para registrar UUID despues de invalidar su pago fuente.\n- Anular un cargo descarta cualquier borrador `CFDI_INGRESO` no timbrado asociado.\n- `register-external-stamp` vuelve a comprobar que el cargo no este `void` y que el pago siga `posted`; un borrador stale no puede recibir UUID.\n- `discarded` es un estado local, no equivale a cancelacion SAT/PAC. Mantiene identidad e historia pero deja de participar en el indice fiscal activo.\n- Un CFDI `cancelled` o un borrador `discarded` nunca se reescribe. Una nueva preparacion recibe nueva identidad `CFD-...`.\n- Solicitudes de cancelacion identicas son idempotentes. Un rechazo externo permite reintento; una solicitud pendiente con datos distintos produce conflicto.\n- Complemento de Pagos selecciona solamente CFDI de ingreso `external_stamped` vigente.\n- Si un pago abarca documentos con tasas distintas, la preparacion local queda bloqueada y exige resolucion fiscal externa; PRISMA no mezcla tasas con una formula inventada.\n- El borrador conceptual incluye `Fecha` y estructura `Impuestos` de nivel comprobante, pero sigue siendo `DRAFT_NOT_XML`; XSD, catalogos, sellado y timbrado pertenecen al SAT/PAC externo.\n<!-- PRISMA:BILLING_INTEGRITY_HARDENING:END -->\n'''
    DOC.write_text(text.rstrip() + block + "\n", encoding="utf-8")


def main() -> int:
    patch_billing()
    patch_cfdi()
    patch_http()
    patch_verify()
    patch_doc()
    print("PASS_COMMERCIAL_BILLING_INTEGRITY_HARDENING_PATCH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
