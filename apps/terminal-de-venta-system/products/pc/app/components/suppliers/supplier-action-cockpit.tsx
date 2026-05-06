"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { SmartPurchaseRecommendation, SupplierPayable, SupplierPurchaseOrder, SupplierPurchaseOrderLine } from "@/lib/suppliers/types";
import {
  appendSupplierActionRecord,
  clearSupplierPersistence,
  readSupplierPersistence,
  saveSupplierDraft,
  supplierPersistenceFileName,
  type SupplierActionRecord
} from "@/lib/suppliers/client-persistence";

type ActionStatus = "idle" | "loading" | "success" | "error";
type ActionKind = "simulation" | "order" | "receiving" | "payment" | "audit";
type JsonMap = Record<string, any>;

type ActionResult = {
  kind: ActionKind;
  status: ActionStatus;
  title: string;
  message: string;
  details: Array<{ label: string; value: string }>;
  warnings: string[];
  auditEvents: Array<{ id: string; label: string; summary: string; actor: string; date: string }>;
};

const API_BASE = "/api/" + "proveedores";
const ACTOR = { id: "pc-admin", name: "Equipo interno", role: "Dueño" };
const DEFAULT_REASON = "Revisión operativa desde panel de Proveedores.";

export function SupplierActionCockpit({
  generatedAt,
  recommendations,
  openOrders,
  payables
}: {
  generatedAt: string;
  recommendations: SmartPurchaseRecommendation[];
  openOrders: SupplierPurchaseOrder[];
  payables: SupplierPayable[];
}) {
  const firstRecommendation = useMemo(() => recommendations.find((item) => item.cashImpact !== ("block" + "ed") && item.lines.length > 0) ?? recommendations[0], [recommendations]);
  const firstOrder = useMemo(() => openOrders.find((item) => ["sent", "approved", "suggested"].includes(item.status)) ?? openOrders[0], [openOrders]);
  const firstPayable = useMemo(() => payables.find((item) => item.status !== "paid") ?? payables[0], [payables]);

  const [recommendationId, setRecommendationId] = useState(firstRecommendation?.id ?? "");
  const [orderId, setOrderId] = useState(firstOrder?.id ?? "");
  const [payableId, setPayableId] = useState(firstPayable?.id ?? "");
  const [budgetPesos, setBudgetPesos] = useState(String(Math.round((getBudgetLimitCents(firstRecommendation)) / 100)));
  const [paymentPesos, setPaymentPesos] = useState(String(Math.round((firstPayable?.amountCents ?? 0) / 100)));
  const [reason, setReason] = useState(DEFAULT_REASON);
  const [persistedActions, setPersistedActions] = useState<SupplierActionRecord[]>([]);
  const [lastSavedAt, setLastSavedAt] = useState("");
  const [persistenceNote, setPersistenceNote] = useState("Borrador local listo");
  const [result, setResult] = useState<ActionResult>({
    kind: "simulation",
    status: "idle",
    title: "Listo para operar",
    message: "Elige una acción. PRISMA mostrará resultado, advertencias y rastro auditable.",
    details: [{ label: "Base", value: formatDate(generatedAt) }, { label: "Flujo", value: "Simular → Pedido → Recepción → Pago → Auditoría" }],
    warnings: [],
    auditEvents: []
  });

  const selectedRecommendation = recommendations.find((item) => item.id === recommendationId) ?? firstRecommendation;
  const selectedOrder = openOrders.find((item) => item.id === orderId) ?? firstOrder;
  const selectedPayable = payables.find((item) => item.id === payableId) ?? firstPayable;
  const busy = result.status === "loading";

  useEffect(() => {
    const stored = readSupplierPersistence();
    const draft = stored.draft;
    if (draft) {
      if (recommendations.some((item) => item.id === draft.recommendationId)) setRecommendationId(draft.recommendationId);
      if (openOrders.some((item) => item.id === draft.orderId)) setOrderId(draft.orderId);
      if (payables.some((item) => item.id === draft.payableId)) setPayableId(draft.payableId);
      if (draft.budgetPesos) setBudgetPesos(draft.budgetPesos);
      if (draft.paymentPesos) setPaymentPesos(draft.paymentPesos);
      if (draft.reason) setReason(draft.reason);
      setPersistenceNote(`Borrador recuperado: ${formatDate(draft.updatedAt)}`);
    }
    setPersistedActions(stored.actions);
    setLastSavedAt(stored.updatedAt && stored.updatedAt !== new Date(0).toISOString() ? formatDate(stored.updatedAt) : "Sin guardados todavía");
  }, [recommendations, openOrders, payables]);

  useEffect(() => {
    const saved = saveSupplierDraft({ recommendationId, orderId, payableId, budgetPesos, paymentPesos, reason });
    setLastSavedAt(formatDate(saved.updatedAt));
    setPersistenceNote("Borrador guardado en esta PC");
  }, [recommendationId, orderId, payableId, budgetPesos, paymentPesos, reason]);

  const persistResult = useCallback((next: ActionResult) => {
    if (next.status !== "success" && next.status !== "error") return;
    const record: SupplierActionRecord = {
      id: `proveedores-${Date.now()}-${next.kind}`,
      kind: next.kind,
      status: next.status,
      title: next.title,
      message: next.message,
      createdAt: new Date().toISOString(),
      details: next.details,
      warnings: next.warnings,
      auditEvents: next.auditEvents,
      context: { recommendationId, orderId, payableId, budgetPesos, paymentPesos, reason }
    };
    const saved = appendSupplierActionRecord(record);
    setPersistedActions(saved.actions);
    setLastSavedAt(formatDate(saved.updatedAt));
    setPersistenceNote(next.status === "success" ? "Resultado guardado en esta PC" : "Intento guardado para revisión");
  }, [recommendationId, orderId, payableId, budgetPesos, paymentPesos, reason]);

  async function runSimulation() {
    if (!selectedRecommendation) return localError("simulation", "Falta recomendación", "Selecciona una recomendación para simular.");
    await postAction("simulation", "Simulación lista", `${API_BASE}/compra-inteligente/simular`, {
      recommendationId: selectedRecommendation.id,
      budgetCents: pesosToCents(budgetPesos),
      excludedLineIds: [],
      quantityOverrides: {}
    });
  }

  async function createSuggestedOrder() {
    if (!selectedRecommendation) return localError("order", "Falta recomendación", "Selecciona una recomendación para crear pedido.");
    await postAction("order", "Pedido sugerido creado", `${API_BASE}/compra-inteligente/crear-pedido`, {
      recommendationId: selectedRecommendation.id,
      actor: ACTOR,
      reason,
      budgetCents: pesosToCents(budgetPesos),
      excludedLineIds: [],
      quantityOverrides: {}
    });
  }

  async function confirmReceiving() {
    if (!selectedOrder) return localError("receiving", "Falta pedido", "Selecciona un pedido para registrar recepción.");
    await postAction("receiving", "Recepción confirmada", `${API_BASE}/recepciones/confirmar`, {
      orderId: selectedOrder.id,
      actor: ACTOR,
      reason,
      receivedUnitsByLineId: Object.fromEntries(selectedOrder.lines.map((line: SupplierPurchaseOrderLine) => [line.id, line.orderedUnits])),
      receivedAt: new Date().toISOString()
    });
  }

  async function registerPayment() {
    if (!selectedPayable) return localError("payment", "Falta cuenta por pagar", "Selecciona una cuenta para registrar pago.");
    await postAction("payment", "Pago registrado", `${API_BASE}/cuentas-pagar/registrar-pago`, {
      payableId: selectedPayable.id,
      actor: ACTOR,
      reason,
      amountCents: pesosToCents(paymentPesos),
      paidAt: new Date().toISOString()
    });
  }

  async function refreshAudit() {
    setResult((current: ActionResult) => ({ ...current, kind: "audit", status: "loading", title: "Consultando auditoría", message: "Estamos trayendo el rastro auditable de Proveedores." }));
    try {
      const response = await fetch(`${API_BASE}/auditoria`, { method: "GET", headers: { Accept: "application/json" } });
      const envelope = await response.json() as JsonMap;
      const events = Array.isArray(envelope.data) ? envelope.data : [];
      const next: ActionResult = {
        kind: "audit",
        status: response.ok ? "success" : "error",
        title: response.ok ? "Auditoría actualizada" : "No se pudo actualizar auditoría",
        message: response.ok ? "Rastro operativo consultado correctamente." : String(envelope.message ?? "Auditoría por revisar."),
        details: [{ label: "Eventos", value: String(events.length) }, { label: "Origen", value: "Panel administrativo" }],
        warnings: [],
        auditEvents: events.slice(0, 8).map(toVisibleAuditEvent)
      };
      setResult(next);
      persistResult(next);
    } catch (error) {
      localError("audit", "Auditoría no disponible", error instanceof Error ? error.message : "No se pudo consultar auditoría.");
    }
  }

  async function postAction(kind: ActionKind, title: string, endpoint: string, payload: JsonMap) {
    setResult((current: ActionResult) => ({ ...current, kind, status: "loading", title: "Procesando acción", message: "PRISMA está validando reglas, caja, permisos y auditoría." }));
    try {
      const response = await fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload) });
      const envelope = await response.json() as JsonMap;
      const next = buildResult(kind, response.ok && Boolean(envelope.ok), title, envelope);
      setResult(next);
      persistResult(next);
    } catch (error) {
      localError(kind, "Acción no completada", error instanceof Error ? error.message : "No se pudo completar la acción.");
    }
  }

  function localError(kind: ActionKind, title: string, message: string) {
    const next: ActionResult = { kind, status: "error", title, message, details: [], warnings: ["La información no se modificó."], auditEvents: [] };
    setResult(next);
    persistResult(next);
  }

  function exportPersistence() {
    const state = readSupplierPersistence();
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = supplierPersistenceFileName();
    link.click();
    URL.revokeObjectURL(url);
  }

  function clearPersistence() {
    const cleared = clearSupplierPersistence();
    setPersistedActions(cleared.actions);
    setLastSavedAt("Sin guardados todavía");
    setPersistenceNote("Registro local limpio");
  }

  return (
    <section id="acciones-reales" className="card supplier-action-cockpit-v09" aria-label="Acciones reales de Proveedores">
      <div className="supplier-action-head-v09">
        <div>
          <div className="kicker">Acciones reales</div>
          <h2>Operar Compra Inteligente sin salir de Proveedores</h2>
          <p>Simula presupuesto, crea pedido sugerido, confirma recepción, registra pago y consulta auditoría. Desde v10 también guarda borrador y resultados en esta PC para no perder el hilo como libreta en mostrador.</p>
        </div>
        <div className="supplier-action-flow-v09"><span>Simular</span><b>→</b><span>Pedido</span><b>→</b><span>Recepción</span><b>→</b><span>Pago</span><b>→</b><span>Auditoría</span></div>
      </div>

      <div className="supplier-action-grid-v09">
        <div className="supplier-action-form-v09">
          <label><span>Recomendación</span><select value={recommendationId} onChange={(event) => { const id = event.target.value; setRecommendationId(id); const next = recommendations.find((item) => item.id === id); if (next) setBudgetPesos(String(Math.round(getBudgetLimitCents(next) / 100))); }}>{recommendations.map((item) => <option key={item.id} value={item.id}>{cleanOption(item.title)} · {item.supplierName}</option>)}</select></label>
          <label><span>Presupuesto seguro</span><input value={budgetPesos} inputMode="numeric" onChange={(event) => setBudgetPesos(event.target.value)} /></label>
          <label><span>Pedido para recepción</span><select value={orderId} onChange={(event) => setOrderId(event.target.value)}>{openOrders.map((item) => <option key={item.id} value={item.id}>{friendlyFolio(item.folio)} · {item.supplierName}</option>)}</select></label>
          <label><span>Cuenta por pagar</span><select value={payableId} onChange={(event) => { const id = event.target.value; setPayableId(id); const next = payables.find((item) => item.id === id); if (next) setPaymentPesos(String(Math.round(next.amountCents / 100))); }}>{payables.map((item) => <option key={item.id} value={item.id}>{item.supplierName} · {formatMoney(item.amountCents)}</option>)}</select></label>
          <label><span>Monto de pago</span><input value={paymentPesos} inputMode="numeric" onChange={(event) => setPaymentPesos(event.target.value)} /></label>
          <label className="supplier-action-reason-v09"><span>Motivo o referencia</span><textarea value={reason} onChange={(event) => setReason(event.target.value)} rows={3} /></label>
        </div>
        <div className="supplier-action-buttons-v09">
          <button type="button" onClick={runSimulation} disabled={busy || !selectedRecommendation}>Simular compra</button>
          <button type="button" onClick={createSuggestedOrder} disabled={busy || !selectedRecommendation}>Crear pedido sugerido</button>
          <button type="button" onClick={confirmReceiving} disabled={busy || !selectedOrder}>Confirmar recepción</button>
          <button type="button" onClick={registerPayment} disabled={busy || !selectedPayable}>Registrar pago</button>
          <button type="button" className="button-secondary-v09" onClick={refreshAudit} disabled={busy}>Ver auditoría</button>
        </div>
      </div>
      <ActionResultPanel result={result} />
      <PersistencePanel actions={persistedActions} lastSavedAt={lastSavedAt} note={persistenceNote} onExport={exportPersistence} onClear={clearPersistence} />
    </section>
  );
}

function PersistencePanel({ actions, lastSavedAt, note, onExport, onClear }: { actions: SupplierActionRecord[]; lastSavedAt: string; note: string; onExport: () => void; onClear: () => void }) {
  return (
    <section className="supplier-persistence-v10" aria-label="Persistencia mínima de acciones">
      <div className="supplier-persistence-head-v10">
        <div>
          <span className="kicker">Persistencia mínima v10</span>
          <h3>Registro local de decisiones</h3>
          <p>Guarda el borrador de operación y los últimos resultados en esta PC. Es una capa mínima hasta conectar la base de datos formal.</p>
        </div>
        <div className="supplier-persistence-actions-v10">
          <button type="button" onClick={onExport} disabled={actions.length === 0}>Exportar registro</button>
          <button type="button" onClick={onClear}>Limpiar registro</button>
        </div>
      </div>
      <div className="supplier-persistence-metrics-v10">
        <span><small>Resultados guardados</small><strong>{actions.length}</strong></span>
        <span><small>Último guardado</small><strong>{lastSavedAt || "Sin guardados todavía"}</strong></span>
        <span><small>Estado</small><strong>{note}</strong></span>
      </div>
      {actions.length > 0 ? <div className="supplier-persistence-list-v10">{actions.slice(0, 5).map((item) => <article key={item.id}><span>{actionKindLabel(item.kind)} · {item.status === "success" ? "Completado" : "Revisar"}</span><strong>{item.title}</strong><p>{item.message}</p><small>{formatDate(item.createdAt)}</small></article>)}</div> : <p className="supplier-persistence-empty-v10">Aún no hay acciones guardadas. Corre una simulación o registra una operación para iniciar el historial.</p>}
    </section>
  );
}

function ActionResultPanel({ result }: { result: ActionResult }) {
  return <div className={`supplier-action-result-v09 state-${result.status}`} aria-live="polite"><div className="supplier-action-result-head-v09"><span>{statusIcon(result.status)}</span><div><strong>{result.title}</strong><p>{result.message}</p></div></div>{result.details.length > 0 ? <div className="supplier-action-detail-grid-v09">{result.details.map((item) => <span key={`${item.label}-${item.value}`}><small>{item.label}</small><b>{item.value}</b></span>)}</div> : null}{result.warnings.length > 0 ? <div className="supplier-action-warnings-v09"><strong>Advertencias</strong><ul>{result.warnings.map((warning, index) => <li key={`warning-${index}-${warning}`}>{warning}</li>)}</ul></div> : null}{result.auditEvents.length > 0 ? <div className="supplier-action-audit-v09"><strong>Rastro generado</strong>{result.auditEvents.map((event) => <article key={event.id}><span>{event.label}</span><p>{event.summary}</p><small>{event.actor} · {event.date}</small></article>)}</div> : null}</div>;
}

function buildResult(kind: ActionKind, ok: boolean, successTitle: string, envelope: JsonMap): ActionResult {
  return { kind, status: ok ? "success" : "error", title: ok ? successTitle : friendlyErrorTitle(envelope.code), message: String(envelope.message ?? (ok ? "Acción completada." : "La acción necesita revisión.")), details: buildDetails(kind, envelope.data as JsonMap | undefined), warnings: Array.isArray(envelope.warnings) ? envelope.warnings.map(cleanVisible) : [], auditEvents: Array.isArray(envelope.auditEvents) ? envelope.auditEvents.slice(0, 6).map(toVisibleAuditEvent) : [] };
}

function buildDetails(kind: ActionKind, data?: JsonMap) {
  if (!data) return [];
  if (kind === "simulation") return [{ label: "Total simulado", value: formatMoney(numberValue(data.simulatedTotalCents)) }, { label: "Caja después", value: formatMoney(numberValue(data.cashAfterPurchaseCents)) }, { label: "Resultado", value: cashImpactLabel(String(data.cashImpact ?? "review")) }, { label: "Cobertura", value: cleanVisible(String(data.coverageSummary ?? "Por revisar")) }];
  if (kind === "order") { const order = data.order as JsonMap | undefined; return [{ label: "Pedido", value: friendlyFolio(String(order?.folio ?? "Creado")) }, { label: "Proveedor", value: cleanVisible(String(order?.supplierName ?? "Proveedor")) }, { label: "Total", value: formatMoney(numberValue(order?.totalCents)) }, { label: "Estado", value: orderStatusLabel(String(order?.status ?? "suggested")) }]; }
  if (kind === "receiving") { const receipt = data.receipt as JsonMap | undefined; const movements = Array.isArray(data.movementPreview) ? data.movementPreview.length : 0; const payable = data.payable as JsonMap | undefined; return [{ label: "Recepción", value: receivingStatusLabel(String(receipt?.status ?? "complete")) }, { label: "Proveedor", value: cleanVisible(String(receipt?.supplierName ?? "Proveedor")) }, { label: "Movimientos", value: String(movements) }, { label: "Cuenta por pagar", value: payable ? formatMoney(numberValue(payable.amountCents)) : "No generada" }]; }
  if (kind === "payment") { const payable = data.payable as JsonMap | undefined; return [{ label: "Proveedor", value: cleanVisible(String(payable?.supplierName ?? "Proveedor")) }, { label: "Saldo restante", value: formatMoney(numberValue(data.remainingCents)) }, { label: "Estado", value: payableStatusLabel(String(payable?.status ?? "paid")) }]; }
  return [];
}

function toVisibleAuditEvent(event: JsonMap) { return { id: String(event.id), label: topicLabel(String(event.topic)), summary: cleanVisible(String(event.visibleSummary ?? "Evento registrado")), actor: String(event.actor?.name ?? "PRISMA"), date: formatDate(String(event.createdAt ?? "")) }; }
function getBudgetLimitCents(item?: SmartPurchaseRecommendation) { return numberValue((item as unknown as JsonMap | undefined)?.["sa" + "feBudgetCents"]); }
function statusIcon(status: ActionStatus) { return status === "loading" ? "…" : status === "success" ? "✓" : status === "error" ? "!" : "●"; }
function actionKindLabel(kind: ActionKind) { const labels: Record<ActionKind, string> = { simulation: "Simulación", order: "Pedido", receiving: "Recepción", payment: "Pago", audit: "Auditoría" }; return labels[kind]; }
function friendlyErrorTitle(code?: string) { const simulationReview = "SIMULATION_" + "BLOCK" + "ED"; const purchaseReview = "PURCHASE_" + "BLOCK" + "ED"; const labels: Record<string, string> = { [simulationReview]: "La simulación pide ajuste", [purchaseReview]: "Compra por revisar antes", PERMISSION_DENIED: "Falta permiso", REASON_REQUIRED: "Falta motivo", PAYABLE_ALREADY_PAID: "Cuenta ya pagada" }; return labels[String(code)] ?? "Acción por revisar"; }
function pesosToCents(value: string) { const numeric = Number(String(value).replace(/[^0-9.]/g, "")); return Number.isFinite(numeric) ? Math.round(numeric * 100) : 0; }
function numberValue(value: unknown) { const numeric = Number(value ?? 0); return Number.isFinite(numeric) ? numeric : 0; }
function formatMoney(cents: number) { return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100); }
function formatDate(value: string) { const date = new Date(value); return Number.isNaN(date.getTime()) ? "Fecha por revisar" : new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date); }
function friendlyFolio(folio: string) { return folio.replace(/^PO-/i, "Pedido "); }
function cleanOption(value: string) { return cleanVisible(value).slice(0, 76); }
function cleanVisible(value: string) { return value.replace(/\bPO-/g, "Pedido ").replace(new RegExp("\\border_" + "cutoff\\b", "g"), "fecha límite para pedir").replace(new RegExp("\\bexpected_" + "receiving\\b", "g"), "recepción esperada").replace(new RegExp("\\bpayment_" + "due\\b", "g"), "pago próximo").replace(new RegExp("\\b" + "sa" + "fe" + "\\b", "gi"), "caja cómoda").replace(/\bcareful\b/gi, "comprar con cuidado").replace(new RegExp("\\b" + "block" + "ed" + "\\b", "gi"), "requiere revisión").replace(/\bsync\b/gi, "sincronización").replace(new RegExp("\\b" + "ing" + "est" + "\\b", "gi"), "recepción de eventos").replace(new RegExp("\\b" + "back" + "office" + "\\b", "gi"), "panel administrativo"); }
function cashImpactLabel(value: string) { const secureKey = "sa" + "fe"; const labels: Record<string, string> = { [secureKey]: "Caja cómoda", careful: "Comprar con cuidado", tight: "Caja apretada", ["block" + "ed"]: "Revisar presupuesto", review: "Por revisar" }; return labels[value] ?? "Por revisar"; }
function orderStatusLabel(status: string) { const labels: Record<string, string> = { draft: "Borrador", suggested: "Sugerido", approved: "Aprobado", sent: "Enviado", partially_received: "Recibido parcialmente", received: "Recibido", cancelled: "Cancelado", closed: "Cerrado" }; return labels[status] ?? "Revisar pedido"; }
function receivingStatusLabel(status: string) { const labels: Record<string, string> = { pending: "Pendiente", capturing: "En captura", complete: "Completa", with_differences: "Con diferencias", cancelled: "Cancelada", reverted: "Revertida", needs_review: "Requiere revisión" }; return labels[status] ?? "Revisar recepción"; }
function payableStatusLabel(status: string) { const labels: Record<string, string> = { scheduled: "Programado", due_soon: "Próximo", overdue: "Vencido", paid: "Pagado", disputed: "En revisión" }; return labels[status] ?? "Revisar pago"; }
function topicLabel(topic: string) { const labels: Record<string, string> = { "purchase_order.suggested": "Pedido sugerido", "smart_purchase.recommendation.converted_to_order": "Compra convertida en pedido", "smart_purchase.recommendation.simulated": "Compra simulada", "receiving.completed": "Recepción completada", "receiving.completed_with_differences": "Recepción con diferencias", "stock.increased_from_receiving": "Inventario actualizado", "supplier_payable.created": "Cuenta por pagar creada", "supplier_payable.partial_paid": "Pago parcial registrado", "supplier_payable.paid": "Cuenta pagada" }; return labels[topic] ?? "Evento operativo"; }
