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

function statusCopy(status: string) {
  const normalized = status.toLowerCase();
  if (normalized === "failed" || normalized === "conflict") return "Requiere revisión";
  if (normalized === "pending") return "Pendiente por enviar";
  if (normalized === "sent" || normalized === "acked") return "Confirmado";
  return "Guardado localmente";
}

function movementTitle(topic: string) {
  const normalized = topic.toLowerCase();
  if (normalized.includes("sale")) return "Venta guardada";
  if (normalized.includes("return")) return "Devolución guardada";
  if (normalized.includes("cash")) return "Movimiento de caja";
  if (normalized.includes("stock") || normalized.includes("inventory")) return "Movimiento de existencia";
  return "Movimiento local";
}

function movementReasonCopy(reason: string) {
  const normalized = reason.toLowerCase();
  if (normalized.includes("return")) return "Devolución registrada";
  if (normalized.includes("sale")) return "Venta registrada";
  if (normalized.includes("adjust")) return "Ajuste de existencia";
  return reason || "Movimiento local";
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
    if (audit.outbox.failed > 0) return `${audit.outbox.failed} pendiente(s) por revisar`;
    if (audit.outbox.pending > 0) return `${audit.outbox.pending} pendientes por enviar`;
    return "Operación local sana";
  }, [audit]);

  const tone = audit?.outbox.failed ? "danger" : audit?.outbox.pending ? "warn" : "ok";

  return (
    <PrismaTabletShellUnified
      currentPath="/offline"
      title="Sin conexión y respaldo"
      subtitle="No pierdes ventas: la Tablet guarda los movimientos y los envia cuando vuelve la conexión."
      status={<TabletShellStatusPill tone={tone}>{headline}</TabletShellStatusPill>}
    >
      <main className={styles.page}>
        <section className={styles.hero}>
          <div>
            <span>Tablet vende sola</span>
            <h1>Tus movimientos están guardados en esta Tablet.</h1>
            <p>Ventas, pendientes por enviar, movimientos de existencias, productos bajos y respaldos quedan disponibles aun sin conexión.</p>
          </div>
          <button type="button" onClick={() => void load()} disabled={state === "loading"}>
            {state === "loading" ? "Actualizando…" : "Actualizar"}
          </button>
        </section>

        {state === "error" ? <div className={styles.alert}>{error}</div> : null}

        <section className={styles.kpis}>
          <article><span>Tickets</span><strong>{audit?.report.completedSalesCount ?? 0}</strong><small>cerrados hoy</small></article>
          <article><span>Vendido</span><strong>{money(audit?.report.grossTotalCents ?? 0)}</strong><small>total local</small></article>
          <article><span>Pendientes</span><strong>{audit?.outbox.pending ?? 0}</strong><small>por enviar a PC</small></article>
          <article><span>Existencias bajas</span><strong>{audit?.inventory.lowStockCount ?? 0}</strong><small>productos</small></article>
        </section>

        <details className={styles.exportCard}>
          <summary className={styles.exportSummary}>
            <span>Respaldo</span>
            <strong>Descargar archivos</strong>
            <small>Ventas, pendientes y movimientos cuando necesites respaldo manual.</small>
          </summary>
          <div className={styles.actions}>
            {audit ? (
              Object.entries({
                "Ventas CSV": audit.exports.salesCsv,
                "Ventas JSON": audit.exports.salesJson,
                "Pendientes CSV": audit.exports.eventsCsv,
                "Pendientes JSON": audit.exports.eventsJson,
                "Movimientos CSV": audit.exports.inventoryMovementsCsv,
                "Movimientos JSON": audit.exports.inventoryMovementsJson
              }).map(([label, href]) => <a key={href} href={href} target="_blank" rel="noreferrer">{label}</a>)
            ) : (
              <span className={styles.muted}>Cargando enlaces…</span>
            )}
          </div>
        </details>

        <section className={styles.columns}>
          <article className={styles.panel}>
            <h2>Pendientes recientes</h2>
            {audit && audit.outbox.events.length ? audit.outbox.events.map((event) => (
              <div className={styles.row} key={event.id}>
                <div><strong>{movementTitle(event.topic)}</strong><span>Creado {new Date(event.createdAt).toLocaleString("es-MX")}. Puedes seguir vendiendo.</span></div>
                <em className={styles[statusTone(event.status)]}>{statusCopy(event.status)}</em>
              </div>
            )) : <p className={styles.empty}>Sin pendientes por enviar. La Tablet está al día.</p>}
          </article>

          <article className={styles.panel}>
            <h2>Movimientos recientes</h2>
            {audit && audit.inventory.recentMovements.length ? audit.inventory.recentMovements.map((movement) => (
              <div className={styles.row} key={movement.id}>
                <div><strong>{movement.productName}</strong><span>{movement.sku} · {movementReasonCopy(movement.reason)}</span></div>
                <em>{movement.quantityDelta}</em>
              </div>
            )) : <p className={styles.empty}>Sin movimientos recientes.</p>}
          </article>
        </section>

        <details className={styles.panel}>
          <summary className={styles.exportSummary}>
            <span>Soporte</span>
            <strong>Detalle de respaldo</strong>
            <small>Información adicional para revisión administrativa.</small>
          </summary>
          <div className={styles.diagnostics}>{audit?.diagnostics.map((item) => <span key={item}>{item}</span>) ?? <span>Cargando diagnóstico local...</span>}</div>
        </details>
      </main>
    </PrismaTabletShellUnified>
  );
}
