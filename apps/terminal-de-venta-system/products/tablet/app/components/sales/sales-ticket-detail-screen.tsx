"use client";

import { useEffect, useState } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { formatMoney, requestJson } from "@/lib/pos/cart-state";
import { paymentMethodLabel } from "@/lib/pos/payment-state";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { decideCanSellFromRuntimeSnapshot } from "@/lib/operational-gate/can-sell";
import styles from "./sales.module.css";

type TicketLine = {
  id: string;
  productId: string;
  sku: string;
  productName: string;
  qty: number;
  priceCents: number;
  totalCents: number;
  returnedQty?: number;
  returnAvailableQty?: number;
  returnedCents?: number;
  returnStatus?: "available" | "partial_returned" | "fully_returned";
};

type TicketDetail = {
  saleId: string;
  folio: string;
  canonicalTicketId?: string;
  lookupAliases?: string[];
  resolvedBy?: string;
  businessId?: string;
  businessName?: string | null;
  storeId?: string | null;
  storeName?: string | null;
  terminalId: string;
  terminalName?: string | null;
  cashSessionId?: string | null;
  cashSession?: {
    id: string;
    storeId: string;
    cashierId: string;
    cashier: string;
    status: string;
    openedAt: string;
    closedAt?: string | null;
  } | null;
  clientRequestId?: string | null;
  cashier: string;
  status: string;
  createdAt: string;
  completedAt?: string | null;
  subtotalCents?: number;
  discountCents?: number;
  paymentMethod?: string;
  cashReceivedCents?: number | null;
  changeCents?: number;
  paymentTenders?: Array<{
    id: string;
    tenderType: string;
    amountCents: number;
    reference?: string | null;
    recordedAt: string;
    source?: string;
  }>;
  returns?: Array<{
    id: string;
    saleFolio: string;
    reason: string;
    amountCents: number;
    status: string;
    cashier: string;
    createdAt: string;
    lines: Array<{
      id: string;
      saleLineId?: string | null;
      productId: string;
      sku: string;
      productName: string;
      qty: number;
      amountCents: number;
      restoreStock: boolean;
      beforeQty?: number | null;
      afterQty?: number | null;
      stockMovedAt?: string | null;
    }>;
  }>;
  evidence?: {
    contract: string;
    local: boolean;
    outboxEvents: Array<{ id: string; topic: string; status: string; createdAt: string; lastError?: string | null }>;
    auditEvents: Array<unknown>;
    evidenceEventIds: string[];
    evidenceTopics: string[];
  };
  totalCents: number;
  lines: TicketLine[];
};

type TicketLookupDiagnostic = {
  requestedId: string;
  businessId: string;
  attemptedFields: string[];
  scopedTicketCount: number;
  totalTicketCount: number;
  scopedPartialMatches: Array<{
    saleId: string;
    folio: string;
    businessId: string;
    terminalId: string;
    clientRequestId?: string | null;
    status: string;
    createdAt: string;
    totalCents: number;
  }>;
  latestTickets: Array<{
    saleId: string;
    folio: string;
    businessId: string;
    terminalId: string;
    clientRequestId?: string | null;
    status: string;
    createdAt: string;
    totalCents: number;
  }>;
  matchedOutboxEvents: Array<{ id: string; topic: string; aggregateId: string; status: string; createdAt: string; lastError?: string | null }>;
  latestOutboxEvents: Array<{ id: string; topic: string; aggregateId: string; status: string; createdAt: string; lastError?: string | null }>;
  serverAdapters: string[];
  nextActions: string[];
};

type DetailState =
  | { status: "loading" }
  | { status: "ready"; ticket: TicketDetail }
  | { status: "not_found"; message: string; diagnostic?: TicketLookupDiagnostic }
  | { status: "error"; message: string };

function asHumanError(error: unknown) {
  if (error && typeof error === "object") {
    const maybe = error as { code?: string; message?: string; details?: { diagnostic?: TicketLookupDiagnostic } };
    if (maybe.code === "SALE_NOT_FOUND") {
      return {
        status: "not_found" as const,
        message: maybe.message || "No encontré ese ticket.",
        diagnostic: maybe.details?.diagnostic
      };
    }
    if (maybe.message) return { status: "error" as const, message: maybe.message };
  }
  return { status: "error" as const, message: "No pude cargar el detalle del ticket." };
}

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Fecha no disponible";
  return new Intl.DateTimeFormat("es-MX", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function ticketStatusCopy(status: string) {
  const value = status.toLowerCase();
  if (value.includes("closed") || value.includes("complete")) return "Cerrado";
  if (value.includes("cancel")) return "Cancelado";
  if (value.includes("pending")) return "Pendiente";
  return "Registrado";
}

function syncStatusCopy(status: string) {
  const value = status.toLowerCase();
  if (value.includes("sent") || value.includes("acked") || value.includes("sync") || value.includes("confirmed")) {
    return "Confirmado";
  }
  if (value.includes("failed") || value.includes("conflict") || value.includes("error")) return "Requiere revisión";
  return "Pendiente de enviar a PC";
}

function ticketSyncSummary(ticket: TicketDetail) {
  const events = ticket.evidence?.outboxEvents ?? [];
  if (!events.length) return "Guardado en esta Tablet";
  if (events.some((event) => syncStatusCopy(event.status) === "Requiere revisión")) return "Requiere revisión";
  if (events.every((event) => syncStatusCopy(event.status) === "Confirmado")) return "Confirmado";
  return "Pendiente de enviar a PC";
}

function returnedLineCopy(line: TicketLine) {
  const returnedQty = Number(line.returnedQty ?? 0);
  if (!Number.isFinite(returnedQty) || returnedQty <= 0) return null;
  const availableQty = Number(line.returnAvailableQty ?? Math.max(0, line.qty - returnedQty));
  if (availableQty > 0) return `Devolución parcial: ${returnedQty} de ${line.qty} pzas. Disponible: ${availableQty}.`;
  return `Devolución registrada: ${returnedQty} de ${line.qty} pzas.`;
}

function returnStatusCopy(status: string) {
  const value = status.toLowerCase();
  if (value.includes("cancel")) return "Cancelada";
  if (value.includes("closed") || value.includes("complete")) return "Confirmada";
  return "Registrada";
}

function returnStockCopy(line: NonNullable<TicketDetail["returns"]>[number]["lines"][number]) {
  if (!line.restoreStock) return "No movió existencias.";
  if (typeof line.beforeQty === "number" && typeof line.afterQty === "number") {
    return `Existencia: ${line.beforeQty} -> ${line.afterQty}.`;
  }
  return "Regresó a existencias locales.";
}

function DetailStateCard({ title, message, canSell, backHref, onRetry }: { title: string; message: string; canSell: boolean; backHref: string; onRetry?: () => void }) {
  return (
    <section className={styles.stateCard}>
      <h2>{title}</h2>
      <p>{message}</p>
      <div className={styles.actionsRow}>
        {onRetry ? <button className={styles.primary} type="button" onClick={onRetry}>Reintentar lectura</button> : null}
        <a className={styles.secondary} href={backHref}>Volver a ventas</a>
        <a className={onRetry ? styles.secondary : styles.primary} href={canSell ? "/pos" : "/shift"}>{canSell ? "Nueva venta" : "Abrir turno"}</a>
      </div>
    </section>
  );
}

function TicketNotFoundDiagnostic({ message, diagnostic, canSell, backHref, onRetry }: { message: string; diagnostic?: TicketLookupDiagnostic; canSell: boolean; backHref: string; onRetry: () => void }) {
  return (
    <section className={styles.stateCard} data-prisma-ticket-resolution="not-found-diagnostic">
      <div className={styles.diagnosticHeader}>
        <div>
          <h2>No encontramos ese ticket en esta Tablet</h2>
          <p>{message}</p>
          <p>Puede ser un folio de otra terminal, una venta aún no sincronizada o un identificador incompleto. La devolución necesita el ticket correcto para no afectar caja ni inventario.</p>
        </div>
        <span>Soporte puede revisar evidencia</span>
      </div>

      {diagnostic ? (
        <>
          <div className={styles.diagnosticGrid}>
            <DiagnosticMetric label="Búsqueda local" value="sin coincidencia" />
            <DiagnosticMetric label="Campos revisados" value={String(diagnostic.attemptedFields.length)} />
            <DiagnosticMetric label="Tickets negocio" value={String(diagnostic.scopedTicketCount)} />
            <DiagnosticMetric label="Tickets locales" value={String(diagnostic.totalTicketCount)} />
          </div>

          <details className={styles.lockedDiagnostic}>
            <summary>Detalle para revisión</summary>
            <p>Bloqueado para caja. El administrador puede revisar el caso desde sus herramientas de revisión.</p>
          </details>
        </>
      ) : (
        <div className={styles.diagnosticSection}>
          <strong>Detalle protegido</strong>
          <span>No se muestran IDs internos ni errores crudos en caja. Reintenta, vuelve a ventas o comparte este caso con soporte.</span>
        </div>
      )}

      <div className={styles.actionsRow}>
        <button className={styles.primary} type="button" onClick={onRetry}>Reintentar lectura</button>
        <a className={styles.secondary} href={backHref}>Volver a ventas</a>
        <a className={styles.secondary} href={canSell ? "/pos" : "/shift"}>{canSell ? "Nueva venta" : "Abrir turno"}</a>
      </div>
    </section>
  );
}

function DiagnosticMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.diagnosticMetric}>
      <small>{label}</small>
      <strong>{value || "-"}</strong>
    </div>
  );
}

export function SalesTicketDetailScreen({
  saleId,
  businessId,
  runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT,
  currentPath = "/sales/today",
  backHref = "/sales/today"
}: {
  saleId: string;
  businessId?: string;
  runtimeSnapshot?: TabletRuntimeSnapshot;
  currentPath?: "/sales/today" | "/sales/history";
  backHref?: string;
}) {
  const [state, setState] = useState<DetailState>({ status: "loading" });
  const [reloadToken, setReloadToken] = useState(0);
  const gate = decideCanSellFromRuntimeSnapshot(runtimeSnapshot);

  useEffect(() => {
    let alive = true;
    const params = new URLSearchParams({ saleId });
    if (businessId) params.set("businessId", businessId);
    setState({ status: "loading" });

    requestJson<{ ticket: TicketDetail }>(`/api/pos/sales/detail?${params.toString()}`)
      .then((response) => {
        if (!alive) return;
        setState({ status: "ready", ticket: response.data.ticket });
      })
      .catch((error) => {
        if (!alive) return;
        setState(asHumanError(error));
      });

    return () => {
      alive = false;
    };
  }, [saleId, businessId, reloadToken]);

  return (
    <PrismaTabletShellUnified
      currentPath={currentPath}
      title="Detalle de ticket"
      subtitle="Detalle operativo del ticket cerrado."
      status={<TabletShellStatusPill tone="ok">Ticket cerrado</TabletShellStatusPill>}
      runtimeSnapshot={runtimeSnapshot}
    >
      <main className={styles.salesPage}>
        {state.status === "loading" ? (
          <DetailStateCard title="Cargando detalle…" message="Estoy buscando el ticket en la base local de Tablet." canSell={gate.canShowSellNavigation} backHref={backHref} />
        ) : null}

        {state.status === "not_found" ? (
          <TicketNotFoundDiagnostic message={state.message} diagnostic={state.diagnostic} canSell={gate.canShowSellNavigation} backHref={backHref} onRetry={() => setReloadToken((value) => value + 1)} />
        ) : null}

        {state.status === "error" ? (
          <DetailStateCard title="No se pudo abrir el detalle" message={state.message} canSell={gate.canShowSellNavigation} backHref={backHref} onRetry={() => setReloadToken((value) => value + 1)} />
        ) : null}

        {state.status === "ready" ? (
          <section className={styles.detailGrid}>
            <article className={styles.panel}>
              <div className={styles.detailHeader}>
                <span>Ticket cerrado</span>
                <h1>{state.ticket.folio}</h1>
                <p>{formatDateTime(state.ticket.completedAt || state.ticket.createdAt)}</p>
              </div>
              <div className={styles.metaGrid}>
                <span>Folio: {state.ticket.folio}</span>
                <span>Estado: {ticketStatusCopy(state.ticket.status)}</span>
                <span>Guardado en esta Tablet</span>
                <span>Sincronización: {ticketSyncSummary(state.ticket)}</span>
              </div>

              {state.ticket.lines.length ? (
                <div className={styles.linesList}>
                  {state.ticket.lines.map((line) => {
                    const returnedCopy = returnedLineCopy(line);
                    return (
                      <div className={styles.line} key={line.id}>
                        <div>
                          <strong>{line.productName}</strong>
                          <span>
                            {line.sku || "SKU sin registrar"} · {line.qty} pzas · {formatMoney(line.priceCents)} c/u
                          </span>
                          {returnedCopy ? <span>{returnedCopy}</span> : null}
                        </div>
                        <strong>{formatMoney(line.totalCents)}</strong>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className={styles.empty}>Este ticket no trae líneas visibles. Revisa la venta antes de continuar.</div>
              )}

              {state.ticket.returns?.length ? (
                <section className={styles.returnSummary} aria-label="Devoluciones relacionadas">
                  <div className={styles.returnSummaryHeader}>
                    <span>Devolución relacionada</span>
                    <strong>{formatMoney(state.ticket.returns.reduce((sum, item) => sum + item.amountCents, 0))}</strong>
                  </div>
                  {state.ticket.returns.map((saleReturn) => (
                    <article className={styles.returnCard} key={saleReturn.id}>
                      <div>
                        <strong>{returnStatusCopy(saleReturn.status)} · {formatMoney(saleReturn.amountCents)}</strong>
                        <span>Motivo: {saleReturn.reason}. Referencia: {saleReturn.id.slice(0, 12)}. Registró: {saleReturn.cashier}.</span>
                        <small>{formatDateTime(saleReturn.createdAt)}</small>
                      </div>
                      <div className={styles.returnLines}>
                        {saleReturn.lines.map((line) => (
                          <span key={line.id}>
                            {line.productName} · {line.qty} pzas · {formatMoney(line.amountCents)} · {returnStockCopy(line)}
                          </span>
                        ))}
                      </div>
                    </article>
                  ))}
                </section>
              ) : null}
            </article>

            <aside className={styles.panel}>
              <span className={styles.panelEyebrow}>Total cobrado</span>
              <h2>{formatMoney(state.ticket.totalCents)}</h2>
              <p>Operador: {state.ticket.cashier}</p>
              <p>Negocio: {state.ticket.businessName ?? "Negocio local"}</p>
              {state.ticket.storeId || state.ticket.storeName ? <p>Tienda: {state.ticket.storeName ?? "Tienda local"}</p> : null}
              <p>Terminal: {state.ticket.terminalName ?? "Terminal local"}</p>
              {state.ticket.cashSessionId ? <p>Turno/caja: {state.ticket.cashSession?.cashier ? `Caja de ${state.ticket.cashSession.cashier}` : "Turno de venta"}</p> : null}
              <p>Pago: {paymentMethodLabel(state.ticket.paymentMethod)} · {formatMoney(state.ticket.totalCents)}</p>
              {typeof state.ticket.cashReceivedCents === "number" ? <p>Recibido: {formatMoney(state.ticket.cashReceivedCents)}</p> : null}
              {typeof state.ticket.changeCents === "number" && state.ticket.changeCents > 0 ? <p>Cambio: {formatMoney(state.ticket.changeCents)}</p> : null}
              {typeof state.ticket.subtotalCents === "number" ? <p>Subtotal: {formatMoney(state.ticket.subtotalCents)}</p> : null}
              {typeof state.ticket.discountCents === "number" && state.ticket.discountCents > 0 ? (
                <p>Descuento: {formatMoney(state.ticket.discountCents)}</p>
              ) : null}
              {state.ticket.paymentTenders?.length ? (
                <div className={styles.auditList}>
                  <strong>Pagos registrados</strong>
                  {state.ticket.paymentTenders.map((tender) => (
                    <span key={tender.id}>{paymentMethodLabel(tender.tenderType)} · {formatMoney(tender.amountCents)}</span>
                  ))}
                </div>
              ) : null}
              {state.ticket.evidence?.outboxEvents.length ? (
                <div className={styles.auditList}>
                  <strong>Evidencia local</strong>
                  {state.ticket.evidence.outboxEvents.slice(0, 4).map((event) => (
                    <span key={event.id}>Movimiento de venta · {syncStatusCopy(event.status)}</span>
                  ))}
                </div>
              ) : null}
              <div className={styles.actionsStack}>
                <a className={styles.primary} href={`/sales/today/${encodeURIComponent(state.ticket.saleId)}/return`}>Hacer devolución</a>
                <a className={styles.secondary} href={gate.canShowSellNavigation ? "/pos" : gate.actionHref}>{gate.canShowSellNavigation ? "Nueva venta" : gate.actionLabel}</a>
                <a className={styles.secondary} href={backHref}>Volver</a>
              </div>
            </aside>
          </section>
        ) : null}
      </main>
    </PrismaTabletShellUnified>
  );
}
