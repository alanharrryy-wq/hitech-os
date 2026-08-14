#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BILLING = ROOT / "Prisma Cloud Ctr" / "internal" / "py" / "commercial_billing.py"
CFDI = ROOT / "Prisma Cloud Ctr" / "internal" / "py" / "cfdi_gateway.py"
STORE = ROOT / "Prisma Cloud Ctr" / "internal" / "py" / "command_center_store.py"
JS = ROOT / "Prisma Cloud Ctr" / "internal" / "web" / "cloud_command_center.js"
WORKFLOW = ROOT.parents[1] / ".github" / "workflows" / "commercial-billing-authority.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_billing() -> None:
    text = BILLING.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '"CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_income_active_idx ON CommercialFiscalDocument(chargeId,kind) WHERE kind=\'CFDI_INGRESO\'",',
        '"CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_income_active_idx ON CommercialFiscalDocument(chargeId,kind) WHERE kind=\'CFDI_INGRESO\' AND status!=\'cancelled\'",',
        "income active fiscal index",
    )
    text = replace_once(
        text,
        '"CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_payment_active_idx ON CommercialFiscalDocument(paymentId,kind) WHERE kind=\'CFDI_PAGO\'",',
        '"CREATE UNIQUE INDEX IF NOT EXISTS CommercialFiscalDocument_payment_active_idx ON CommercialFiscalDocument(paymentId,kind) WHERE kind=\'CFDI_PAGO\' AND status!=\'cancelled\'",',
        "payment active fiscal index",
    )
    old = '''    received_at = str(body.get("receivedAt") or _now_iso()).strip()\n    try:\n        datetime.fromisoformat(received_at.replace("Z", "+00:00"))\n    except ValueError as exc:\n        raise BillingError("BILLING_PAYMENT_DATE_INVALID", "receivedAt debe ser fecha/hora ISO valida.") from exc\n    digest = _payment_request_digest({**body, "receivedAt": received_at}, charge, amount, payment_form)\n    existing = con.execute("SELECT * FROM CommercialPayment WHERE idempotencyKey=?", (idem,)).fetchone()\n    if existing:\n'''
    new = '''    existing = con.execute("SELECT * FROM CommercialPayment WHERE idempotencyKey=?", (idem,)).fetchone()\n    received_at = str(body.get("receivedAt") or (existing["receivedAt"] if existing else _now_iso())).strip()\n    try:\n        datetime.fromisoformat(received_at.replace("Z", "+00:00"))\n    except ValueError as exc:\n        raise BillingError("BILLING_PAYMENT_DATE_INVALID", "receivedAt debe ser fecha/hora ISO valida.") from exc\n    digest = _payment_request_digest({**body, "receivedAt": received_at}, charge, amount, payment_form)\n    if existing:\n'''
    text = replace_once(text, old, new, "payment retry timestamp idempotency")
    text = replace_once(
        text,
        'existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE chargeId=? AND kind=\'CFDI_INGRESO\'", (charge["id"],)).fetchone()',
        'existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE chargeId=? AND kind=\'CFDI_INGRESO\' AND status!=\'cancelled\' ORDER BY createdAt DESC,id DESC LIMIT 1", (charge["id"],)).fetchone()',
        "income active document lookup",
    )
    text = replace_once(
        text,
        'existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE paymentId=? AND kind=\'CFDI_PAGO\'", (payment["id"],)).fetchone()',
        'existing = con.execute("SELECT * FROM CommercialFiscalDocument WHERE paymentId=? AND kind=\'CFDI_PAGO\' AND status!=\'cancelled\' ORDER BY createdAt DESC,id DESC LIMIT 1", (payment["id"],)).fetchone()',
        "payment active document lookup",
    )
    old = '    prepared = build_payment_complement_draft(payment=payment, allocations=allocations, charges=charges, income_documents=income_docs, issuer=issuer, receiver=receiver)\n    status = "ready_to_stamp" if prepared["ready"] else "draft_blocked"\n'
    new = '    prepared = build_payment_complement_draft(payment=payment, allocations=allocations, charges=charges, income_documents=income_docs, issuer=issuer, receiver=receiver)\n    if int(payment.get("unappliedCents") or 0) > 0:\n        prepared["missingPrerequisites"].append("payment.unappliedCents=0")\n        prepared["ready"] = False\n    prepared["missingPrerequisites"] = sorted(set(prepared["missingPrerequisites"]))\n    status = "ready_to_stamp" if prepared["ready"] else "draft_blocked"\n'
    text = replace_once(text, old, new, "unapplied payment complement guard")
    BILLING.write_text(text, encoding="utf-8")


def patch_cfdi() -> None:
    text = CFDI.read_text(encoding="utf-8")
    needle = '"UsoCFDI": receiver.get("cfdiUse"),'
    first = text.find(needle)
    second = text.find(needle, first + 1)
    if first < 0 or second < 0 or text.find(needle, second + 1) >= 0:
        raise SystemExit("cfdi UsoCFDI anchors changed")
    text = text[:second] + '"UsoCFDI": "CP01",' + text[second + len(needle):]
    export_needle = '"Exportacion": issuer.get("exportCode") or "01",'
    first = text.find(export_needle)
    second = text.find(export_needle, first + 1)
    if first < 0 or second < 0 or text.find(export_needle, second + 1) >= 0:
        raise SystemExit("cfdi Exportacion anchors changed")
    text = text[:second] + '"Exportacion": "01",' + text[second + len(export_needle):]
    CFDI.write_text(text, encoding="utf-8")


def patch_store() -> None:
    text = STORE.read_text(encoding="utf-8")
    anchor = '''from commercial_contracts import (\n    CommercialContractError,\n    count_commercial_contracts,\n    ensure_commercial_schema,\n    insert_commercial_contract,\n    list_commercial_contracts,\n    resolve_commercial_terms,\n)\n\n'''
    addition = anchor + '''from commercial_billing import (\n    BillingError,\n    billing_command,\n    billing_snapshot,\n    ensure_billing_schema,\n)\n\n'''
    text = replace_once(text, anchor, addition, "commercial billing import")
    old_prefix = 'PREFIX = {"client":"CLI","device":"DEV","license":"LIC","contract":"CTR","provisioning":"ALT","deactivation":"BAJ","note":"NTE","receipt":"RCP","case":"CAS","evidence":"EVD","backup":"BKP","rollback":"RBK","item":"ID"}'
    new_prefix = 'PREFIX = {"client":"CLI","device":"DEV","license":"LIC","contract":"CTR","charge":"COB","payment":"PAY","fiscal":"CFD","provisioning":"ALT","deactivation":"BAJ","note":"NTE","receipt":"RCP","case":"CAS","evidence":"EVD","backup":"BKP","rollback":"RBK","item":"ID"}'
    text = replace_once(text, old_prefix, new_prefix, "billing identity prefixes")
    text = replace_once(text, "    ensure_commercial_schema(con)\n\ndef _seed_first_customer", "    ensure_commercial_schema(con)\n    ensure_billing_schema(con)\n\ndef _seed_first_customer", "billing schema hook")
    text = replace_once(text, '        "schemaVersion": 3,\n', '        "schemaVersion": 4,\n', "bootstrap schema version")
    text = replace_once(text, '        "licensePlans": plans,\n        "counts": _counts(con),\n', '        "licensePlans": plans,\n        "billing": billing_snapshot(con),\n        "counts": _counts(con),\n', "bootstrap billing snapshot")
    old_route = '''    if path.startswith("/api/command-center/support"):\n        return support_store_payload(raw_path, method=method, body=body)\n    with db() as con:\n'''
    new_route = '''    if path.startswith("/api/command-center/support"):\n        return support_store_payload(raw_path, method=method, body=body)\n    if path.startswith("/api/command-center/billing"):\n        with db() as con:\n            try:\n                out = billing_command(con, path, method, body or {}, gen)\n            except BillingError as exc:\n                return {"ok": False, "resultCode": exc.code, "error": str(exc), "details": exc.details, "_httpStatus": exc.http_status}\n            if method == "POST" and out.get("ok"):\n                con.commit()\n            return out\n    with db() as con:\n'''
    text = replace_once(text, old_route, new_route, "billing route dispatcher")
    STORE.write_text(text, encoding="utf-8")


def patch_js() -> None:
    text = JS.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    ["contracts", "Contracts & Config", "Contrato y configuración", "Contrato actual, capacidades, diferencias visibles y resumen copiable."],\n',
        '    ["contracts", "Contracts & Config", "Contrato y configuración", "Contrato actual, capacidades, diferencias visibles y resumen copiable."],\n    ["billing", "Cobranza", "Cobranza & CFDI", "Cargos, pagos externos, recibos no fiscales, aging y borradores CFDI con gateway SAT/PAC fail-closed."],\n',
        "billing surface nav",
    )
    text = replace_once(
        text,
        'surfaceButton("entitlements","Asignar licencia"),surfaceButton("fleet","Agregar dispositivo")',
        'surfaceButton("entitlements","Asignar licencia"),surfaceButton("billing","Cobranza & CFDI"),surfaceButton("fleet","Agregar dispositivo")',
        "command billing action",
    )
    anchor = '  function renderOperations() { const c=localCounts(); const d=derived(); return ['
    billing_ui = r'''  function billingState(){ return ccStore().billing || {}; }
  function billingRows(kind){ const local=billingState().local || {}; return Array.isArray(local[kind]) ? local[kind] : []; }
  function moneyCents(value){ const n=Number(value||0); return new Intl.NumberFormat("es-MX",{style:"currency",currency:"MXN",minimumFractionDigits:2,maximumFractionDigits:2}).format(n/100); }
  function boolFlow(key){ return String(flowValue(key,"false")) === "true"; }
  function simpleSelectField(id,label,options,selected){ const effective=selected || options[0]?.[0] || ""; return `<label class="cc-field"><span>${esc(label)}</span><select data-flow-field="${esc(id)}">${options.map(([value,text])=>`<option value="${esc(value)}" ${value===effective?"selected":""}>${esc(text)}</option>`).join("")}</select></label>`; }
  function billingEntityField(id,label,rows,selected,labeler){ const options=(rows||[]).map((row)=>[row.humanCode||row.id,labeler(row)]); if(!options.length) return `<label class="cc-field"><span>${esc(label)}</span><select data-flow-field="${esc(id)}"><option value="">Sin registros disponibles</option></select></label>`; return simpleSelectField(id,label,options,selected); }
  function billingReconciliation(){ const r=billingState().reconciliation || {}; const a=r.agingCents || {}; return kvGrid([["Por cobrar",moneyCents(r.outstandingCents)],["Vencido",moneyCents(r.overdueCents)],["Cobrado registrado",moneyCents(r.collectedCents)],["Aplicado",moneyCents(r.allocatedCents)],["No aplicado",moneyCents(r.unappliedCents)],["Corriente",moneyCents(a.current)],["1-30",moneyCents(a["1_30"])],["31-60",moneyCents(a["31_60"])],["61-90",moneyCents(a["61_90"])],["90+",moneyCents(a["90_plus"])]]); }
  function billingReceiverForm(){ return `<div class="cc-flow-grid">${selectField("billingClientCode","Cliente","client",flowValue("billingClientCode"),{required:true})}${textField("billingReceiverRfc","RFC receptor",flowValue("billingReceiverRfc"),{placeholder:"RFC exacto"})}${textField("billingReceiverName","Razón social fiscal",flowValue("billingReceiverName"),{})}${textField("billingReceiverPostal","CP fiscal",flowValue("billingReceiverPostal"),{placeholder:"5 dígitos"})}${textField("billingReceiverRegime","Régimen fiscal",flowValue("billingReceiverRegime"),{placeholder:"Clave SAT"})}${textField("billingReceiverUse","Uso CFDI",flowValue("billingReceiverUse"),{placeholder:"Ej. G03"})}${textField("billingReceiverEmail","Correo facturación",flowValue("billingReceiverEmail"),{})}${textField("billingReceiverSource","Evidencia / constancia",flowValue("billingReceiverSource"),{placeholder:"Referencia documental"})}${simpleSelectField("billingReceiverConfirm","Confirmar datos fiscales",[["false","No, guardar borrador"],["true","Sí, datos cotejados"]],flowValue("billingReceiverConfirm","false"))}</div>${actions([actionButton("billing-save-receiver","Guardar receptor","primary")])}`; }
  function billingIssuerForm(){ const issuer=billingState().issuer||{}; return `<div class="cc-flow-grid">${textField("billingIssuerRfc","RFC emisor",flowValue("billingIssuerRfc",issuer.issuerRfc),{})}${textField("billingIssuerName","Razón social emisor",flowValue("billingIssuerName",issuer.legalName),{})}${textField("billingIssuerPostal","CP expedición",flowValue("billingIssuerPostal",issuer.postalCode),{})}${textField("billingIssuerRegime","Régimen fiscal",flowValue("billingIssuerRegime",issuer.fiscalRegime),{})}${textField("billingProdServ","ClaveProdServ PRISMA",flowValue("billingProdServ",issuer.productServiceCode),{placeholder:"8 dígitos; confirmar con SAT/PAC"})}${textField("billingUnitCode","ClaveUnidad",flowValue("billingUnitCode",issuer.unitCode),{})}${textField("billingUnitName","Unidad",flowValue("billingUnitName",issuer.unitName||"Unidad de servicio"),{})}${textField("billingTaxObject","ObjetoImp",flowValue("billingTaxObject",issuer.taxObjectCode),{})}${textField("billingTaxCode","Impuesto",flowValue("billingTaxCode",issuer.taxCode),{})}${textField("billingExportCode","Exportación",flowValue("billingExportCode",issuer.exportCode),{})}${simpleSelectField("billingProviderMode","Modo fiscal",[["not_configured","Sin configurar"],["manual_sat","SAT manual externo"],["pac_external","PAC externo"]],flowValue("billingProviderMode",issuer.providerMode||"not_configured"))}${textField("billingProviderName","Proveedor/PAC",flowValue("billingProviderName",issuer.providerName),{})}${simpleSelectField("billingCsdState","CSD",[["not_configured","No configurado"],["presence_only","Presencia confirmada fuera de PRISMA"],["externally_managed","Gestionado externamente"]],flowValue("billingCsdState",issuer.csdState||"not_configured"))}${textField("billingIssuerSource","Evidencia emisor",flowValue("billingIssuerSource",issuer.sourceRef),{})}${simpleSelectField("billingIssuerConfirm","Confirmar emisor",[["false","No, guardar borrador"],["true","Sí, datos cotejados"]],flowValue("billingIssuerConfirm","false"))}</div>${actions([actionButton("billing-save-issuer","Guardar emisor","primary")])}`; }
  function billingChargeForm(){ const contracts=localRows("contracts"); return `<div class="cc-flow-grid">${billingEntityField("billingContractCode","Contrato CTR",contracts,flowValue("billingContractCode"),(r)=>`${r.humanCode} · ${r.clientName||r.clientCode||"Cliente"} · ${r.planCode} · ${BILLING_PERIOD_LABELS[r.billingPeriod]||r.billingPeriod} · ${moneyMxn(r.agreedPriceMxn)} + IVA`)}${textField("billingTaxRateBps","Tasa impuesto bps",flowValue("billingTaxRateBps","1600"),{placeholder:"1600 = 16%"})}${textField("billingTaxRateSource","Fuente tasa",flowValue("billingTaxRateSource","LIVA_ART_1_GENERAL_RATE_OPERATOR_CONFIRMED"),{})}${textField("billingDueOn","Vence YYYY-MM-DD",flowValue("billingDueOn"),{placeholder:"Vacío = inicio del periodo"})}${simpleSelectField("billingConfirmTax","Tratamiento fiscal confirmado",[["false","No"],["true","Sí"]],flowValue("billingConfirmTax","false"))}</div>${actions([actionButton("billing-create-charge","Crear cargo desde CTR","primary"),actionButton("billing-reconcile","Reconciliar estados")])}`; }
  function billingPaymentForm(){ const charges=billingRows("charges"); return `<div class="cc-flow-grid">${billingEntityField("billingChargeCode","Cargo",charges,flowValue("billingChargeCode"),(r)=>`${r.humanCode} · ${r.clientName||r.clientCode||"Cliente"} · ${moneyCents(r.balanceCents)} saldo · ${r.derivedStatus||r.status}`)}${textField("billingPaymentAmount","Importe recibido MXN",flowValue("billingPaymentAmount"),{placeholder:"0.00"})}${simpleSelectField("billingPaymentForm","Forma de pago SAT",[["01","01 Efectivo"],["02","02 Cheque nominativo"],["03","03 Transferencia electrónica"],["04","04 Tarjeta de crédito"],["28","28 Tarjeta de débito"]],flowValue("billingPaymentForm","03"))}${textField("billingPaymentReceivedAt","Fecha/hora ISO",flowValue("billingPaymentReceivedAt"),{placeholder:"Vacío = ahora; se conserva para retry"})}${textField("billingPaymentReference","Referencia externa",flowValue("billingPaymentReference"),{placeholder:"Folio/recibo externo, no cuenta bancaria"})}${textField("billingPaymentEvidence","Evidencia",flowValue("billingPaymentEvidence"),{placeholder:"Referencia documental"})}${textField("billingIdempotencyKey","Idempotency key",flowValue("billingIdempotencyKey"),{placeholder:"Se genera automáticamente si queda vacío"})}${textField("billingPaymentNote","Nota operador",flowValue("billingPaymentNote"),{})}</div>${actions([actionButton("billing-register-payment","Registrar pago externo","primary")])}<div class="cc-empty"><strong>RECIBO INTERNO NO FISCAL</strong><span>PRISMA sólo registra el hecho informado; no cobra, no valida SPEI, no toma tarjetas y no custodia dinero.</span></div>`; }
  function billingCorrectionForm(){ const charges=billingRows("charges"); const payments=billingRows("payments"); return `<div class="cc-flow-grid">${billingEntityField("billingVoidChargeCode","Cargo a anular",charges,flowValue("billingVoidChargeCode"),(r)=>`${r.humanCode} · ${moneyCents(r.balanceCents)} · ${r.derivedStatus||r.status}`)}${textField("billingVoidReason","Motivo anulación",flowValue("billingVoidReason"),{})}${simpleSelectField("billingVoidConfirm","Confirmar anulación",[["false","No"],["true","Sí"]],flowValue("billingVoidConfirm","false"))}${billingEntityField("billingReversePaymentCode","Pago a revertir",payments,flowValue("billingReversePaymentCode"),(r)=>`${r.humanCode} · ${moneyCents(r.amountCents)} · ${r.status}`)}${textField("billingReverseReason","Motivo reversión",flowValue("billingReverseReason"),{})}${simpleSelectField("billingReverseConfirm","Confirmar reversión",[["false","No"],["true","Sí"]],flowValue("billingReverseConfirm","false"))}</div>${actions([actionButton("billing-void-charge","Anular cargo"),actionButton("billing-reverse-payment","Revertir registro de pago")])}`; }
  function billingFiscalForm(){ const charges=billingRows("charges"); const payments=billingRows("payments"); const docs=billingRows("fiscalDocuments"); return `<div class="cc-flow-grid">${billingEntityField("billingCfdiChargeCode","Cargo para CFDI ingreso",charges,flowValue("billingCfdiChargeCode"),(r)=>`${r.humanCode} · ${r.clientName||"Cliente"} · ${r.derivedStatus||r.status}`)}${billingEntityField("billingCfdiPaymentCode","Pago para Complemento",payments,flowValue("billingCfdiPaymentCode"),(r)=>`${r.humanCode} · ${moneyCents(r.amountCents)} · ${r.status}`)}${billingEntityField("billingFiscalDocumentCode","Documento fiscal",docs,flowValue("billingFiscalDocumentCode"),(r)=>`${r.humanCode} · ${r.kind} · ${r.status}${r.uuid?` · ${r.uuid}`:""}`)}${textField("billingFiscalUuid","UUID externo",flowValue("billingFiscalUuid"),{})}${textField("billingFiscalProvider","SAT/PAC externo",flowValue("billingFiscalProvider"),{})}${textField("billingFiscalEvidence","Evidencia fiscal",flowValue("billingFiscalEvidence"),{})}${textField("billingXmlSha","SHA-256 XML",flowValue("billingXmlSha"),{placeholder:"Opcional; no se guarda XML"})}${simpleSelectField("billingCancelReason","Motivo cancelación SAT",[["01","01 Error con relación"],["02","02 Error sin relación"],["03","03 Operación no realizada"],["04","04 Operación nominativa/global"]],flowValue("billingCancelReason","02"))}${textField("billingReplacementUuid","UUID sustituto",flowValue("billingReplacementUuid"),{placeholder:"Obligatorio para motivo 01"})}${simpleSelectField("billingCancelConfirm","Confirmar solicitud",[["false","No"],["true","Sí"]],flowValue("billingCancelConfirm","false"))}${simpleSelectField("billingCancelResult","Resultado externo",[["false","Rechazada / no cancelada"],["true","Cancelada externamente"]],flowValue("billingCancelResult","true"))}</div>${actions([actionButton("billing-prepare-income-cfdi","Preparar CFDI ingreso"),actionButton("billing-register-external-stamp","Registrar UUID timbrado externo"),actionButton("billing-prepare-payment-complement","Preparar Complemento Pagos 2.0"),actionButton("billing-request-cancellation","Registrar solicitud de cancelación"),actionButton("billing-register-cancellation-result","Registrar resultado externo")])}`; }
  function billingChargesTable(){ return table(["Cargo","Cliente","Contrato","Estado","Total","Pagado","Saldo","Vence"],billingRows("charges").map((r)=>({Cargo:r.humanCode,Cliente:r.clientName||r.clientCode,Contrato:r.contractCode,Estado:r.derivedStatus||r.status,Total:moneyCents(r.totalCents),Pagado:moneyCents(r.paidCents),Saldo:moneyCents(r.balanceCents),Vence:r.dueOn})),"Sin cargos comerciales."); }
  function billingPaymentsTable(){ return table(["Pago","Cliente","Estado","Importe","Aplicado","No aplicado","Forma","Fecha"],billingRows("payments").map((r)=>({Pago:r.humanCode,Cliente:r.clientName||r.clientCode,Estado:r.status,Importe:moneyCents(r.amountCents),Aplicado:moneyCents(r.allocatedCents),"No aplicado":moneyCents(r.unappliedCents),Forma:r.paymentForm,Fecha:r.receivedAt})),"Sin pagos externos registrados."); }
  function billingReceiptsTable(){ return table(["Recibo","Pago","Estado","Importe","Tipo"],billingRows("commercialReceipts").map((r)=>({Recibo:r.humanCode,Pago:r.paymentCode,Estado:r.status,Importe:moneyCents(r.amountCents),Tipo:"RECIBO INTERNO NO FISCAL"})),"Sin recibos internos."); }
  function billingFiscalTable(){ return table(["Documento","Tipo","Cliente","Estado","UUID","Error"],billingRows("fiscalDocuments").map((r)=>({Documento:r.humanCode,Tipo:r.kind,Cliente:r.clientName||r.clientCode,Estado:r.status,UUID:r.uuid||"-",Error:r.lastErrorCode||"-"})),"Sin documentos fiscales preparados."); }
  function renderBilling(){ const b=billingState(); const c=b.counts||{}; const g=b.gateway||{}; return [
    panel("Cobranza","Cuentas por cobrar derivadas de CTR. Vencimiento no suspende licencias automáticamente.",billingReconciliation(),{span:7,tag:`${c.charges||0} cargos`}),
    panel("Frontera financiera","PRISMA registra hechos externos y evidencia; nunca mueve ni custodia fondos.",list([["Procesa dinero",b.moneyProcessing?"SÍ - REVISAR":"NO"],["Valida banco/SPEI",b.bankValidation||b.speiValidation?"SÍ - REVISAR":"NO"],["Toma tarjetas",b.cardCapture?"SÍ - REVISAR":"NO"],["Suspensión automática",b.licenseAutoSuspension?"SÍ - REVISAR":"NO"]]),{span:5,tag:"NO BANKING"}),
    panel("Perfil fiscal receptor","Datos CFDI 4.0 del cliente. No se infieren del primer cliente ni de licensing.",billingReceiverForm(),{span:6,tag:"RECEPTOR"}),
    panel("Perfil fiscal emisor","Datos y catálogos confirmados; CSD/token/llave privada permanecen fuera de PRISMA.",billingIssuerForm(),{span:6,tag:b.issuer?.status||"MISSING"}),
    panel("Crear cargo","Genera el adeudo desde CommercialContract, con impuesto confirmado y centavos enteros.",billingChargeForm(),{span:6,tag:"CTR → COB"}),
    panel("Registrar pago externo","El operador registra evidencia de un pago ya ocurrido fuera de PRISMA.",billingPaymentForm(),{span:6,tag:"EXTERNO"}),
    panel("Correcciones auditables","Anular cargo o revertir registro sin borrar historia. CFDI timbrado bloquea atajos.",billingCorrectionForm(),{span:12,tag:"GUARDED"}),
    panel("Gateway CFDI","Prepara borradores y registra resultados externos. Timbrado/cancelación en vivo siguen bloqueados.",kvGrid([["CFDI",g.cfdiVersion||"4.0"],["Pagos",g.paymentComplementVersion||"2.0"],["Provider",g.provider||"sin configurar"],["CSD",g.csdState||"not_configured"],["Timbrado en vivo",g.liveStampingAllowed?"habilitado - revisar":"NO"],["Cancelación en vivo",g.liveCancellationAllowed?"habilitada - revisar":"NO"],["Secretos expuestos",g.secretsExposed?"SÍ - revisar":"NO"]])+billingFiscalForm(),{span:12,tag:"FAIL-CLOSED"}),
    panel("Cargos","Estado, saldo y vencimiento.",billingChargesTable(),{span:12,tag:`${c.charges||0}`}),
    panel("Pagos externos","Idempotencia, aplicado y crédito no aplicado.",billingPaymentsTable(),{span:12,tag:`${c.payments||0}`}),
    panel("Recibos internos","Evidencia administrativa separada del CFDI.",billingReceiptsTable(),{span:12,tag:"NO FISCAL"}),
    panel("Documentos fiscales","draft_blocked → ready_to_stamp → external_stamped → cancel_requested/cancelled.",billingFiscalTable(),{span:12,tag:`${c.fiscalDocuments||0} docs`}),
    panel("Auditoría comercial","Eventos append-only de cargo, pago, recibo y fiscal.",list(billingRows("billingEvents").map((e)=>[`${e.eventType} · ${e.entityCode||e.entityKind}`,e.summary]),"Sin eventos de cobranza."),{span:12,tag:`${c.billingEvents||0} eventos`}),
    resultPanel()
  ].join(""); }

'''
    text = replace_once(text, anchor, billing_ui + anchor, "billing renderer injection")
    text = replace_once(
        text,
        '    contracts: renderContracts,\n    operations: renderOperations,\n',
        '    contracts: renderContracts,\n    billing: renderBilling,\n    operations: renderOperations,\n',
        "billing renderer map",
    )
    action_anchor = '      } else if (action === "prepare-client") { result = await postAction("/api/command-center/draft-client", { ...state.flow, other: collectOtherValues() });'
    billing_action = r'''      } else if (action.startsWith("billing-")) {
        if (action === "billing-register-payment") {
          if (!flowValue("billingIdempotencyKey")) state.flow.billingIdempotencyKey = `pay-${Date.now()}-${globalThis.crypto?.randomUUID?.() || Math.random().toString(36).slice(2)}`;
          if (!flowValue("billingPaymentReceivedAt")) state.flow.billingPaymentReceivedAt = new Date().toISOString();
        }
        const specs = {
          "billing-save-receiver": ["/api/command-center/billing/receiver-profile", {clientCode:flowValue("billingClientCode"),rfc:flowValue("billingReceiverRfc"),legalName:flowValue("billingReceiverName"),postalCode:flowValue("billingReceiverPostal"),fiscalRegime:flowValue("billingReceiverRegime"),cfdiUse:flowValue("billingReceiverUse"),email:flowValue("billingReceiverEmail"),sourceRef:flowValue("billingReceiverSource"),confirmFiscalData:boolFlow("billingReceiverConfirm")}],
          "billing-save-issuer": ["/api/command-center/billing/issuer-profile", {issuerRfc:flowValue("billingIssuerRfc"),legalName:flowValue("billingIssuerName"),postalCode:flowValue("billingIssuerPostal"),fiscalRegime:flowValue("billingIssuerRegime"),productServiceCode:flowValue("billingProdServ"),unitCode:flowValue("billingUnitCode"),unitName:flowValue("billingUnitName"),taxObjectCode:flowValue("billingTaxObject"),taxCode:flowValue("billingTaxCode"),exportCode:flowValue("billingExportCode"),providerMode:flowValue("billingProviderMode","not_configured"),providerName:flowValue("billingProviderName"),csdState:flowValue("billingCsdState","not_configured"),sourceRef:flowValue("billingIssuerSource"),confirmIssuerData:boolFlow("billingIssuerConfirm")}],
          "billing-create-charge": ["/api/command-center/billing/create-charge", {contractCode:flowValue("billingContractCode"),taxRateBps:flowValue("billingTaxRateBps","1600"),taxRateSource:flowValue("billingTaxRateSource"),dueOn:flowValue("billingDueOn"),confirmTax:boolFlow("billingConfirmTax")}],
          "billing-reconcile": ["/api/command-center/billing/reconcile", {}],
          "billing-register-payment": ["/api/command-center/billing/register-payment", {chargeCode:flowValue("billingChargeCode"),amountMxn:flowValue("billingPaymentAmount"),currency:"MXN",paymentForm:flowValue("billingPaymentForm","03"),receivedAt:flowValue("billingPaymentReceivedAt"),externalReference:flowValue("billingPaymentReference"),evidenceRef:flowValue("billingPaymentEvidence"),idempotencyKey:flowValue("billingIdempotencyKey"),operatorNote:flowValue("billingPaymentNote")}],
          "billing-void-charge": ["/api/command-center/billing/void-charge", {chargeCode:flowValue("billingVoidChargeCode"),reason:flowValue("billingVoidReason"),confirmVoid:boolFlow("billingVoidConfirm")}],
          "billing-reverse-payment": ["/api/command-center/billing/reverse-payment", {paymentCode:flowValue("billingReversePaymentCode"),reason:flowValue("billingReverseReason"),confirmReverse:boolFlow("billingReverseConfirm")}],
          "billing-prepare-income-cfdi": ["/api/command-center/billing/prepare-income-cfdi", {chargeCode:flowValue("billingCfdiChargeCode")}],
          "billing-register-external-stamp": ["/api/command-center/billing/register-external-stamp", {documentCode:flowValue("billingFiscalDocumentCode"),uuid:flowValue("billingFiscalUuid"),provider:flowValue("billingFiscalProvider"),providerEvidenceRef:flowValue("billingFiscalEvidence"),xmlSha256:flowValue("billingXmlSha")}],
          "billing-prepare-payment-complement": ["/api/command-center/billing/prepare-payment-complement", {paymentCode:flowValue("billingCfdiPaymentCode")}],
          "billing-request-cancellation": ["/api/command-center/billing/request-cancellation", {documentCode:flowValue("billingFiscalDocumentCode"),reason:flowValue("billingCancelReason","02"),replacementUuid:flowValue("billingReplacementUuid"),confirmCancellationRequest:boolFlow("billingCancelConfirm")}],
          "billing-register-cancellation-result": ["/api/command-center/billing/register-cancellation-result", {documentCode:flowValue("billingFiscalDocumentCode"),cancelled:String(flowValue("billingCancelResult","true"))==="true",evidenceRef:flowValue("billingFiscalEvidence")}]
        };
        const spec = specs[action];
        if (!spec) throw new Error(`Acción de cobranza no mapeada: ${action}`);
        result = await safePost(spec[0], spec[1]);
        setResult("Cobranza & CFDI", result.message || (result.ok ? "Operación comercial registrada." : `${result.resultCode||"REVIEW"}: ${result.error||"Revisar datos"}`), result, { kind: result.ok ? "ok" : "warn", surface: "billing" });
        toast(result.ok ? "Cobranza actualizada" : "Cobranza a revisar");
        if (result.ok) await loadAll();
''' + action_anchor
    text = replace_once(text, action_anchor, billing_action, "billing action dispatcher")
    JS.write_text(text, encoding="utf-8")


def patch_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    setup_anchor = '''      - uses: actions/setup-python@v6\n        with:\n          python-version: '3.11'\n\n'''
    setup_new = setup_anchor + '''      - uses: actions/setup-node@v4\n        with:\n          node-version: '22'\n\n'''
    text = replace_once(text, setup_anchor, setup_new, "setup node")
    upload_anchor = '      - name: Upload governance evidence\n'
    checks = '''      - name: Compile commercial billing modules\n        run: >-\n          python -m py_compile\n          "apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/py/cfdi_gateway.py"\n          "apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/py/commercial_billing.py"\n          "apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/py/commercial_contracts.py"\n          "apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/py/command_center_store.py"\n          apps/terminal-de-venta-system/tools/verify-commercial-billing-cfdi-01.py\n\n      - name: Check Cloud Center JavaScript syntax\n        run: node --check "apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/cloud_command_center.js"\n\n      - name: Verify commercial billing and CFDI behavior\n        run: >-\n          python apps/terminal-de-venta-system/tools/verify-commercial-billing-cfdi-01.py\n          --out-dir apps/terminal-de-venta-system/.governance/current\n\n      - name: Guard no CSS and no payment-processing copy\n        shell: python\n        run: |\n          import subprocess\n          from pathlib import Path\n          changed = subprocess.check_output(['git','diff','--name-only','origin/main...HEAD'], text=True).splitlines()\n          css = [path for path in changed if path.lower().endswith('.css')]\n          if css:\n              raise SystemExit('Billing task must not change CSS: ' + ', '.join(css))\n          js = Path('apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/cloud_command_center.js').read_text(encoding='utf-8')\n          for phrase in ('Pagar ahora', 'Ingresar tarjeta', 'Confirmar pago bancario'):\n              if phrase in js:\n                  raise SystemExit('Forbidden payment-processing copy: ' + phrase)\n          print('PASS_NO_CSS_NO_PAYMENT_PROCESSING_COPY')\n\n'''
    text = replace_once(text, upload_anchor, checks + upload_anchor, "billing validation steps")
    text = replace_once(
        text,
        '            apps/terminal-de-venta-system/.governance/current/COMMERCIAL_BILLING_LAYERS_MAP.md\n',
        '            apps/terminal-de-venta-system/.governance/current/COMMERCIAL_BILLING_LAYERS_MAP.md\n            apps/terminal-de-venta-system/.governance/current/COMMERCIAL_BILLING_VERIFY.json\n            apps/terminal-de-venta-system/.governance/current/COMMERCIAL_BILLING_VERIFY.md\n',
        "upload behavioral evidence",
    )
    WORKFLOW.write_text(text, encoding="utf-8")


def main() -> int:
    patch_billing()
    patch_cfdi()
    patch_store()
    patch_js()
    patch_workflow()
    print("PASS_GUARDED_COMMERCIAL_BILLING_INTEGRATION_PATCH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
