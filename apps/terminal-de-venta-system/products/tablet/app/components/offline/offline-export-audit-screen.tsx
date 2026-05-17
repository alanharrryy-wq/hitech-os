"use client";

import { useEffect, useMemo, useState } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { requestJson } from "@/lib/pos/cart-state";
import styles from "./offline-export-audit.module.css";

type ExportLinks = Record<
  "salesCsv" | "salesJson" | "eventsCsv" | "eventsJson" | "inventoryMovementsCsv" | "inventoryMovementsJson",
  string
>;

type OfflineAudit = {
  generatedAt: string;
  businessId: string;
  terminalId: string | null;
  report: {
    date: string;
    salesCount: number;
    completedSalesCount: number;
    grossTotalCents: number;
    totalUnitsSold: number;
    averageTicketCents: number;
    pendingOutboxCount: number;
    failedOutboxCount: number;
    lowStockCount: number;
    recentMovementsCount: number;
  };
  outbox: {
    count: number;
    pending: number;
    failed: number;
    events: Array<{ id: string; topic: string; aggregateId: string; status: string; attempts: number; createdAt: string }>;
  };
  inventory: {
    recentMovementsCount: number;
    recentMovements: Array<{ id: string; sku: string; productName: string; quantityDelta: number; reason: string; createdAt: string }>;
    lowStockCount: number;
    lowStockProducts: Array<{ id: string; sku: string; name: string; stockOnHand: number; lowStockThreshold: number }>;
  };
  exports: ExportLinks;
  diagnostics: string[];
};

type ScreenState = "loading" | "ready" | "empty" | "error";

function money(cents: number) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format(cents / 100);
}

function readError(error: unknown) {
  if (error && typeof error === "object" && "message" in error) return String((error as { message?: string }).message);
  return "No pude cargar la auditoría offline local.";
}

function statusTone(status: string): "ok" | "warn" | "danger" | "neutral" {
  const normalized = status.toLowerCase();
  if (normalized === "failed" || normalized === "conflict") return "danger";
  if (normalized === "pending") return "warn";
  if (normalized === "sent" || normalized === "acked") return "ok";
  return "neutral";
}

export function OfflineExportAuditScreen() {
  const [audit, setAudit] = useState<OfflineAudit | null>(null);
  const [state, setState] = useState<ScreenState>("loading");
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setState("loading");
    setError(null);
    try {
      const response = await requestJson<{ audit: OfflineAudit }>("/api/pos/offline/audit?limit=40");
      setAudit(response.data.audit);
      setState("ready");
    } catch (caught) {
      setError(readError(caught));
      setState("error");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const headline = useMemo(() => {
    if (!audit) return "Revisando datos locales";
    if (audit.outbox.failed > 0) return `${audit.outbox.failed} eventos fallidos`;
    if (audit.outbox.pending > 0) return `${audit.outbox.pending} pendientes por sincronizar`;
    return "Operación local sana";
  }, [audit]);

  const tone = audit?.outbox.failed ? "danger" : audit?.outbox.pending ? "warn" : "ok";

  return (
    <PrismaTabletShellUnified
      currentPath="/offline"
      title="Sin conexión y exportación"
      subtitle="Todo lo que la Tablet guarda localmente cuando vende sola."
      status={<TabletShellStatusPill tone={tone}>{headline}</TabletShellStatusPill>}
    >
      <main className={styles.page}>
        <section className={styles.hero}>
          <div>
            <span>Tablet vende sola</span>
            <h1>Auditoría local operativa</h1>
            <p>Ventas, eventos pendientes, movimientos de inventario, stock bajo y descargas, todo desde la base local.</p>
          </div>
          <button type="button" onClick={() => void load()} disabled={state === "loading"}>
            {state === "loading" ? "Actualizando…" : "Actualizar"}
          </button>
        </section>

        {state === "error" ? <div className={styles.alert}>{error}</div> : null}

        <section className={styles.kpis}>
          <article><span>Tickets</span><strong>{audit?.report.completedSalesCount ?? 0}</strong><small>cerrados hoy</small></article>
          <article><span>Vendido</span><strong>{money(audit?.report.grossTotalCents ?? 0)}</strong><small>total local</small></article>
          <article><span>Outbox</span><strong>{audit?.outbox.pending ?? 0}</strong><small>pendientes</small></article>
          <article><span>Stock bajo</span><strong>{audit?.inventory.lowStockCount ?? 0}</strong><small>productos</small></article>
        </section>

        <section className={styles.exportCard}>
          <div>
            <span>Exportar evidencia</span>
            <h2>Descarga ventas, eventos y movimientos</h2>
            <p>Útil para respaldo, revisión externa o sincronización manual cuando PC todavía no está conectada.</p>
          </div>
          <div className={styles.actions}>
            {audit ? (
              Object.entries({
                "Ventas CSV": audit.exports.salesCsv,
                "Ventas JSON": audit.exports.salesJson,
                "Eventos CSV": audit.exports.eventsCsv,
                "Eventos JSON": audit.exports.eventsJson,
                "Movimientos CSV": audit.exports.inventoryMovementsCsv,
                "Movimientos JSON": audit.exports.inventoryMovementsJson
              }).map(([label, href]) => <a key={href} href={href} target="_blank" rel="noreferrer">{label}</a>)
            ) : (
              <span className={styles.muted}>Cargando enlaces…</span>
            )}
          </div>
        </section>

        <section className={styles.columns}>
          <article className={styles.panel}>
            <h2>Outbox reciente</h2>
            {audit && audit.outbox.events.length ? audit.outbox.events.map((event) => (
              <div className={styles.row} key={event.id}>
                <div><strong>{event.topic}</strong><span>{event.aggregateId} · {new Date(event.createdAt).toLocaleString("es-MX")}</span></div>
                <em className={styles[statusTone(event.status)]}>{event.status}</em>
              </div>
            )) : <p className={styles.empty}>Sin eventos visibles todavía.</p>}
          </article>

          <article className={styles.panel}>
            <h2>Movimientos recientes</h2>
            {audit && audit.inventory.recentMovements.length ? audit.inventory.recentMovements.map((movement) => (
              <div className={styles.row} key={movement.id}>
                <div><strong>{movement.productName}</strong><span>{movement.sku} · {movement.reason}</span></div>
                <em>{movement.quantityDelta}</em>
              </div>
            )) : <p className={styles.empty}>Sin movimientos recientes.</p>}
          </article>
        </section>

        <section className={styles.panel}>
          <h2>Diagnóstico</h2>
          <div className={styles.diagnostics}>{audit?.diagnostics.map((item) => <span key={item}>{item}</span>) ?? <span>Cargando diagnóstico local...</span>}</div>
        </section>
      </main>
    </PrismaTabletShellUnified>
  );
}
