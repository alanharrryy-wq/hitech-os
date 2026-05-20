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

type DetailState =
  | { status: "loading" }
  | { status: "ready"; ticket: TicketDetail }
  | { status: "not_found"; message: string }
  | { status: "error"; message: string };

function asHumanError(error: unknown) {
  if (error && typeof error === "object") {
    const maybe = error as { code?: string; message?: string };
    if (maybe.code === "SALE_NOT_FOUND") return { status: "not_found" as const, message: maybe.message || "No encontré ese ticket." };
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

function DetailStateCard({ title, message, canSell, onRetry }: { title: string; message: string; canSell: boolean; onRetry?: () => void }) {
  return (
    <section className={styles.stateCard}>
      <h2>{title}</h2>
      <p>{message}</p>
      <div className={styles.actionsRow}>
        {onRetry ? <button className={styles.primary} type="button" onClick={onRetry}>Reintentar lectura</button> : null}
        <a className={styles.secondary} href="/sales/today">Volver a ventas</a>
        <a className={onRetry ? styles.secondary : styles.primary} href={canSell ? "/pos" : "/shift"}>{canSell ? "Nueva venta" : "Abrir turno"}</a>
      </div>
    </section>
  );
}

export function SalesTicketDetailScreen({ saleId, businessId, runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT }: { saleId: string; businessId?: string; runtimeSnapshot?: TabletRuntimeSnapshot }) {
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
      currentPath="/sales/today"
      title="Detalle de ticket"
      subtitle="Detalle operativo del ticket cerrado."
      status={<TabletShellStatusPill tone="ok">Ticket cerrado</TabletShellStatusPill>}
      runtimeSnapshot={runtimeSnapshot}
    >
      <main className={styles.salesPage}>
        {state.status === "loading" ? (
          <DetailStateCard title="Cargando detalle…" message="Estoy buscando el ticket en la base local de Tablet." canSell={gate.canShowSellNavigation} />
        ) : null}

        {state.status === "not_found" ? (
          <DetailStateCard title="Ticket no encontrado" message={state.message} canSell={gate.canShowSellNavigation} onRetry={() => setReloadToken((value) => value + 1)} />
        ) : null}

        {state.status === "error" ? (
          <DetailStateCard title="No se pudo abrir el detalle" message={state.message} canSell={gate.canShowSellNavigation} onRetry={() => setReloadToken((value) => value + 1)} />
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
                <span>Venta local: {state.ticket.saleId}</span>
                <span>Contrato: {state.ticket.evidence?.contract ?? "SALE_AS_TICKET_EVIDENCE_V1"}</span>
                {state.ticket.clientRequestId ? <span>Solicitud: {state.ticket.clientRequestId}</span> : null}
                {state.ticket.lookupAliases?.length ? <span>Alias: {state.ticket.lookupAliases.join(" / ")}</span> : null}
              </div>

              {state.ticket.lines.length ? (
                <div className={styles.linesList}>
                  {state.ticket.lines.map((line) => (
                    <div className={styles.line} key={line.id}>
                      <div>
                        <strong>{line.productName}</strong>
                        <span>
                          {line.sku || "SKU sin registrar"} · {line.qty} pzas · {formatMoney(line.priceCents)} c/u
                        </span>
                      </div>
                      <strong>{formatMoney(line.totalCents)}</strong>
                    </div>
                  ))}
                </div>
              ) : (
                <div className={styles.empty}>Este ticket no trae líneas visibles. Revisa la venta o el smoke de datos durables.</div>
              )}
            </article>

            <aside className={styles.panel}>
              <span className={styles.panelEyebrow}>Total cobrado</span>
              <h2>{formatMoney(state.ticket.totalCents)}</h2>
              <p>Operador: {state.ticket.cashier}</p>
              <p>Negocio: {state.ticket.businessName ?? state.ticket.businessId ?? "Negocio local"}</p>
              {state.ticket.storeId ? <p>Tienda: {state.ticket.storeName ?? state.ticket.storeId}</p> : null}
              <p>Terminal: {state.ticket.terminalName ?? state.ticket.terminalId}</p>
              {state.ticket.cashSessionId ? <p>Turno/caja: {state.ticket.cashSession?.cashier ?? state.ticket.cashSessionId}</p> : null}
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
                    <span key={event.id}>{event.topic} · {event.status}</span>
                  ))}
                </div>
              ) : null}
              <div className={styles.actionsStack}>
                <a className={styles.primary} href={`/sales/today/${encodeURIComponent(state.ticket.saleId)}/return`}>Hacer devolución</a>
                <a className={styles.secondary} href={gate.canShowSellNavigation ? "/pos" : gate.actionHref}>{gate.canShowSellNavigation ? "Nueva venta" : gate.actionLabel}</a>
                <a className={styles.secondary} href="/sales/today">Volver</a>
              </div>
            </aside>
          </section>
        ) : null}
      </main>
    </PrismaTabletShellUnified>
  );
}
