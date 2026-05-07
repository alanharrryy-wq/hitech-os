"use client";

import { useEffect, useState } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { formatMoney, requestJson } from "@/lib/pos/cart-state";
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
  businessId?: string;
  terminalId: string;
  cashier: string;
  status: string;
  createdAt: string;
  completedAt?: string | null;
  subtotalCents?: number;
  discountCents?: number;
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

function DetailStateCard({ title, message }: { title: string; message: string }) {
  return (
    <section className={styles.stateCard}>
      <h2>{title}</h2>
      <p>{message}</p>
      <div className={styles.actionsRow}>
        <a className={styles.secondary} href="/sales/today">Volver a ventas</a>
        <a className={styles.primary} href="/pos">Nueva venta</a>
      </div>
    </section>
  );
}

export function SalesTicketDetailScreen({ saleId, businessId }: { saleId: string; businessId?: string }) {
  const [state, setState] = useState<DetailState>({ status: "loading" });

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
  }, [saleId, businessId]);

  return (
    <PrismaTabletShellUnified
      currentPath="/sales/today"
      title="Detalle de ticket"
      subtitle="Detalle operativo del ticket cerrado."
      status={<TabletShellStatusPill tone="ok">Ticket cerrado</TabletShellStatusPill>}
    >
      <main className={styles.salesPage}>
        {state.status === "loading" ? (
          <DetailStateCard title="Cargando detalle…" message="Estoy buscando el ticket en la base local de Tablet." />
        ) : null}

        {state.status === "not_found" ? (
          <DetailStateCard title="Ticket no encontrado" message={state.message} />
        ) : null}

        {state.status === "error" ? (
          <DetailStateCard title="No se pudo abrir el detalle" message={state.message} />
        ) : null}

        {state.status === "ready" ? (
          <section className={styles.detailGrid}>
            <article className={styles.panel}>
              <div className={styles.detailHeader}>
                <span>Ticket cerrado</span>
                <h1>{state.ticket.folio}</h1>
                <p>{formatDateTime(state.ticket.completedAt || state.ticket.createdAt)}</p>
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
              <p>Terminal: {state.ticket.terminalId}</p>
              {typeof state.ticket.subtotalCents === "number" ? <p>Subtotal: {formatMoney(state.ticket.subtotalCents)}</p> : null}
              {typeof state.ticket.discountCents === "number" && state.ticket.discountCents > 0 ? (
                <p>Descuento: {formatMoney(state.ticket.discountCents)}</p>
              ) : null}
              <div className={styles.actionsStack}>
                <a className={styles.primary} href={`/sales/today/${encodeURIComponent(state.ticket.saleId)}/return`}>Hacer devolución</a>
                <a className={styles.secondary} href="/pos">Nueva venta</a>
                <a className={styles.secondary} href="/sales/today">Volver</a>
              </div>
            </aside>
          </section>
        ) : null}
      </main>
    </PrismaTabletShellUnified>
  );
}
