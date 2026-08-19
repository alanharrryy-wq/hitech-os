"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { PrismaInsightEnvelope, SyncCommandLifecycleEvent, TabletCatalogFreshnessGridRow } from "@prisma-charts/prismaChartContracts";
import styles from "./pc-sync-chart-promotion-panel.module.css";

const FRESHNESS_ENDPOINT = "/api/charts/pc/tablet-catalog-freshness-grid";
const LIFECYCLE_ENDPOINT = "/api/charts/pc/sync-command-lifecycle-timeline";

type ApiOk<T> = {
  ok: true;
  data: T;
  meta: Record<string, unknown>;
};

type ApiFail = {
  ok: false;
  code: string;
  message: string;
  details: Record<string, unknown>;
};

type ChartState = {
  loading: boolean;
  error: string | null;
  refreshedAt: string | null;
  freshness: PrismaInsightEnvelope<TabletCatalogFreshnessGridRow[]> | null;
  lifecycle: PrismaInsightEnvelope<SyncCommandLifecycleEvent[]> | null;
};

function isApiOk<T>(value: ApiOk<T> | ApiFail): value is ApiOk<T> {
  return value.ok === true;
}

async function loadChart<T>(endpoint: string) {
  const response = await fetch(endpoint, { method: "GET", cache: "no-store" });
  const payload = await response.json().catch(() => null) as ApiOk<PrismaInsightEnvelope<T>> | ApiFail | null;
  if (!response.ok || !payload || !isApiOk(payload)) {
    throw new Error("No pudimos cargar el estado de sincronización. Intenta de nuevo.");
  }
  return payload.data;
}

function dateLabel(value: string | null | undefined) {
  if (!value) return "sin registro";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "sin registro";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function statusLabel(value: string) {
  const normalized = value.toLowerCase();
  if (["fresh", "healthy", "ok", "success", "applied", "completed"].includes(normalized)) return "al día";
  if (["stale", "warning", "partial"].includes(normalized)) return "requiere revisión";
  if (["failed", "error", "rejected"].includes(normalized)) return "con problema";
  if (["pending", "queued", "received", "sent"].includes(normalized)) return "pendiente";
  if (["conflict", "conflicted"].includes(normalized)) return "con conflicto";
  return value.replaceAll("_", " ");
}

function entityLabel(value: string) {
  const labels: Record<string, string> = {
    Product: "Productos",
    Barcode: "Códigos",
    Brand: "Marcas",
    TaxRate: "Impuestos",
    Supplier: "Proveedores",
    ProductSupplier: "Productos por proveedor",
    PriceList: "Listas de precio",
    PriceListItem: "Precios",
    DropdownCatalog: "Opciones",
    DropdownOption: "Valores"
  };
  return labels[value] ?? value.replace(/([a-z])([A-Z])/g, "$1 $2");
}

function commandLabel(value: string) {
  const normalized = value.toLowerCase();
  if (normalized.includes("catalog")) return "Actualización de catálogo";
  if (normalized.includes("sync")) return "Sincronización";
  if (normalized.includes("pull")) return "Recepción de cambios";
  if (normalized.includes("push")) return "Envío de cambios";
  return "Actualización operativa";
}

function rowStatusClass(status: string) {
  return styles[status as keyof typeof styles] ?? "";
}

function sumLifecycle(events: SyncCommandLifecycleEvent[], key: keyof SyncCommandLifecycleEvent["resultCounts"]) {
  return events.reduce((total, event) => total + (event.resultCounts[key] ?? 0), 0);
}

function FreshnessChart({ envelope }: { envelope: PrismaInsightEnvelope<TabletCatalogFreshnessGridRow[]> | null }) {
  const rows = envelope?.data ?? [];
  if (!envelope) return <div className={styles.stateBox}>Cargando estado del catálogo.</div>;
  if (!rows.length) return <div className={styles.stateBox}>No hay equipos con información reciente del catálogo.</div>;
  return (
    <div className={styles.freshnessRows} data-chart-id="pc.tablet-catalog-freshness-grid">
      {rows.map((row) => (
        <article className={styles.freshnessRow} key={row.terminalId}>
          <div className={styles.terminalBlock}>
            <span className={styles.terminalName}>{row.terminalLabel}</span>
            <span className={`${styles.statusPill} ${rowStatusClass(row.freshnessStatus)}`}>{statusLabel(row.freshnessStatus)}</span>
            <span className={styles.terminalMeta}>Última actualización correcta: {dateLabel(row.lastSuccessfulPullAt)}</span>
            <div className={styles.countsLine}>
              <span className={styles.miniPill}>aplicados {row.counts.applied}</span>
              <span className={styles.miniPill}>rechazados {row.counts.rejected}</span>
              <span className={styles.miniPill}>conflictos {row.counts.conflicted}</span>
              <span className={styles.miniPill}>duplicados {row.counts.duplicated}</span>
            </div>
            {row.lastErrorSummary ? <span className={styles.terminalMeta}>La última actualización reportó un problema. Reintenta o revisa el equipo.</span> : null}
          </div>
          <div className={styles.entityGrid}>
            {row.entityStatuses.map((entity) => (
              <div className={`${styles.entityCell} ${rowStatusClass(entity.status)}`} key={`${row.terminalId}:${entity.entityType}`}>
                <span className={styles.entityName}>{entityLabel(entity.entityType)}</span>
                <span className={styles.entityCounts}>{statusLabel(entity.status)}</span>
                <span className={styles.entityCounts}>{entity.appliedCount} aplicados · {entity.rejectedCount} rechazados · {entity.conflictedCount} conflictos</span>
              </div>
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}

function LifecycleChart({ envelope }: { envelope: PrismaInsightEnvelope<SyncCommandLifecycleEvent[]> | null }) {
  const events = envelope?.data ?? [];
  if (!envelope) return <div className={styles.stateBox}>Cargando actividad de sincronización.</div>;
  if (!events.length) return <div className={styles.stateBox}>No hay actividad reciente de sincronización.</div>;
  return (
    <div className={styles.timelineRows} data-chart-id="pc.sync-command-lifecycle-timeline">
      {events.slice(0, 14).map((event) => (
        <article className={styles.timelineItem} key={`${event.commandId}:${event.timestamp}`}>
          <span className={`${styles.timelineMarker} ${rowStatusClass(event.status)}`} aria-hidden="true" />
          <div className={styles.timelineCard}>
            <div className={styles.timelineTop}>
              <span>{commandLabel(event.commandType)}</span>
              <span className={`${styles.statusPill} ${rowStatusClass(event.status)}`}>{statusLabel(event.status)}</span>
            </div>
            <div className={styles.timelineMeta}>{dateLabel(event.timestamp)} · {event.terminalLabel ?? "Todos los equipos"}</div>
            <div className={styles.countsLine}>
              <span className={styles.miniPill}>aplicados {event.resultCounts.applied}</span>
              <span className={styles.miniPill}>rechazados {event.resultCounts.rejected}</span>
              <span className={styles.miniPill}>conflictos {event.resultCounts.conflicted}</span>
              <span className={styles.miniPill}>duplicados {event.resultCounts.duplicated}</span>
            </div>
            {event.reason ? <div className={styles.timelineMeta}>La operación incluye una observación que requiere revisión.</div> : null}
          </div>
        </article>
      ))}
    </div>
  );
}

export function PcSyncChartPromotionPanel() {
  const [state, setState] = useState<ChartState>({ loading: true, error: null, refreshedAt: null, freshness: null, lifecycle: null });

  const refresh = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const [freshness, lifecycle] = await Promise.all([
        loadChart<TabletCatalogFreshnessGridRow[]>(FRESHNESS_ENDPOINT),
        loadChart<SyncCommandLifecycleEvent[]>(LIFECYCLE_ENDPOINT)
      ]);
      setState({ loading: false, error: null, refreshedAt: new Date().toISOString(), freshness, lifecycle });
    } catch {
      setState((current) => ({ ...current, loading: false, error: "No pudimos cargar el estado de sincronización. Intenta de nuevo.", freshness: current.freshness, lifecycle: current.lifecycle }));
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const lifecycleSummary = useMemo(() => {
    const events = state.lifecycle?.data ?? [];
    return {
      applied: sumLifecycle(events, "applied"),
      rejected: sumLifecycle(events, "rejected"),
      conflicted: sumLifecycle(events, "conflicted"),
      duplicated: sumLifecycle(events, "duplicated")
    };
  }, [state.lifecycle]);

  return (
    <section className="card" data-pc-sync-chart-promotion="true">
      <div className={styles.panel}>
        <div className={styles.header}>
          <div className={styles.headerText}>
            <p className={styles.eyebrow}>sincronización de catálogo</p>
            <h2 className={styles.title}>Estado del catálogo por equipo</h2>
            <p className={styles.copy}>Revisa qué equipos están al día, cuáles tienen conflictos y cómo avanzaron las últimas actualizaciones.</p>
          </div>
          <button className={styles.refreshButton} type="button" onClick={() => void refresh()} disabled={state.loading} aria-busy={state.loading}>
            {state.loading ? "Actualizando" : "Actualizar"}
          </button>
        </div>

        <div className={styles.statusLine} role={state.error ? "alert" : "status"}>
          <span className={styles.statusPill}>{state.loading ? "cargando" : state.error ? "con problema" : "actualizado"}</span>
          <span>Última lectura: {dateLabel(state.refreshedAt)}</span>
          {state.error ? <span>{state.error}</span> : null}
        </div>

        <div className={styles.charts}>
          <article className={styles.chartCard}>
            <header className={styles.chartHeader}>
              <div>
                <h3>Estado por equipo</h3>
              </div>
              <span>{state.freshness?.data.length ?? 0} equipos</span>
            </header>
            <div className={styles.chartBody}>
              <FreshnessChart envelope={state.freshness} />
            </div>
          </article>

          <article className={styles.chartCard}>
            <header className={styles.chartHeader}>
              <div>
                <h3>Actividad reciente</h3>
              </div>
              <span>{state.lifecycle?.data.length ?? 0} eventos</span>
            </header>
            <div className={styles.chartBody}>
              <LifecycleChart envelope={state.lifecycle} />
            </div>
            <footer className={styles.footer}>
              <span>Aplicados {lifecycleSummary.applied} · rechazados {lifecycleSummary.rejected}</span>
              <span>Conflictos {lifecycleSummary.conflicted} · duplicados {lifecycleSummary.duplicated}</span>
            </footer>
          </article>
        </div>
      </div>
    </section>
  );
}
