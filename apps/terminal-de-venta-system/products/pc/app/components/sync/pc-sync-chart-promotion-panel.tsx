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
    const message = payload && "message" in payload ? payload.message : `HTTP ${response.status}`;
    throw new Error(message);
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
  return value.replaceAll("_", " ");
}

function rowStatusClass(status: string) {
  return styles[status as keyof typeof styles] ?? "";
}

function sumLifecycle(events: SyncCommandLifecycleEvent[], key: keyof SyncCommandLifecycleEvent["resultCounts"]) {
  return events.reduce((total, event) => total + (event.resultCounts[key] ?? 0), 0);
}

function FreshnessChart({ envelope }: { envelope: PrismaInsightEnvelope<TabletCatalogFreshnessGridRow[]> | null }) {
  const rows = envelope?.data ?? [];
  if (!envelope) return <div className={styles.stateBox}>Cargando frescura de catalogo.</div>;
  if (!rows.length) return <div className={styles.stateBox}>Sin Tablets con heartbeat o checkpoint de catalogo visibles en PC.</div>;
  return (
    <div className={styles.freshnessRows} data-chart-id="pc.tablet-catalog-freshness-grid">
      {rows.map((row) => (
        <article className={styles.freshnessRow} key={row.terminalId}>
          <div className={styles.terminalBlock}>
            <span className={styles.terminalName}>{row.terminalLabel}</span>
            <span className={styles.terminalMeta}>{row.terminalId}</span>
            <span className={`${styles.statusPill} ${rowStatusClass(row.freshnessStatus)}`}>{statusLabel(row.freshnessStatus)}</span>
            <span className={styles.terminalMeta}>pull ok: {dateLabel(row.lastSuccessfulPullAt)}</span>
            <span className={styles.terminalMeta}>cursor: {row.checkpointCursor ?? "sin cursor"}</span>
            <div className={styles.countsLine}>
              <span className={styles.miniPill}>aplicados {row.counts.applied}</span>
              <span className={styles.miniPill}>rechazados {row.counts.rejected}</span>
              <span className={styles.miniPill}>conflictos {row.counts.conflicted}</span>
              <span className={styles.miniPill}>duplicados {row.counts.duplicated}</span>
              <span className={styles.miniPill}>accion {row.recommendedAction}</span>
            </div>
            {row.lastErrorSummary ? <span className={styles.terminalMeta}>error: {row.lastErrorSummary}</span> : null}
          </div>
          <div className={styles.entityGrid}>
            {row.entityStatuses.map((entity) => (
              <div className={`${styles.entityCell} ${rowStatusClass(entity.status)}`} key={`${row.terminalId}:${entity.entityType}`}>
                <span className={styles.entityName}>{entity.entityType}</span>
                <span className={styles.entityCounts}>PC {entity.pcRowCount} / exp {entity.exportedCount}</span>
                <span className={styles.entityCounts}>ok {entity.appliedCount} · rej {entity.rejectedCount} · con {entity.conflictedCount} · dup {entity.duplicatedCount}</span>
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
  if (!envelope) return <div className={styles.stateBox}>Cargando timeline de comandos.</div>;
  if (!events.length) return <div className={styles.stateBox}>Sin eventos de lifecycle PC-visible para catalogo.</div>;
  return (
    <div className={styles.timelineRows} data-chart-id="pc.sync-command-lifecycle-timeline">
      {events.slice(0, 14).map((event) => (
        <article className={styles.timelineItem} key={`${event.commandId}:${event.timestamp}`}>
          <span className={`${styles.timelineMarker} ${rowStatusClass(event.status)}`} aria-hidden="true" />
          <div className={styles.timelineCard}>
            <div className={styles.timelineTop}>
              <span>{event.commandType}</span>
              <span className={`${styles.statusPill} ${rowStatusClass(event.status)}`}>{statusLabel(event.status)}</span>
            </div>
            <div className={styles.timelineMeta}>{dateLabel(event.timestamp)} · {event.terminalLabel ?? event.terminalId ?? "all"} · {event.source}</div>
            <div className={styles.countsLine}>
              <span className={styles.miniPill}>aplicados {event.resultCounts.applied}</span>
              <span className={styles.miniPill}>rechazados {event.resultCounts.rejected}</span>
              <span className={styles.miniPill}>conflictos {event.resultCounts.conflicted}</span>
              <span className={styles.miniPill}>duplicados {event.resultCounts.duplicated}</span>
              <span className={styles.miniPill}>accion {event.recommendedAction}</span>
            </div>
            {event.reason ? <div className={styles.timelineMeta}>razon: {event.reason}</div> : null}
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
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error instanceof Error ? error.message : "No fue posible cargar charts de sync PC." }));
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
            <p className={styles.eyebrow}>charts promovidos</p>
            <h2 className={styles.title}>Catalogo PC a Tablet</h2>
            <p className={styles.copy}>Frescura por Tablet, cursor, entidades, conflictos, duplicados y lifecycle de comandos desde endpoints PC reales.</p>
          </div>
          <button className={styles.refreshButton} type="button" onClick={() => void refresh()} disabled={state.loading} aria-busy={state.loading}>
            {state.loading ? "Actualizando" : "Actualizar"}
          </button>
        </div>

        <div className={styles.statusLine} role={state.error ? "alert" : "status"}>
          <span className={styles.statusPill}>{state.loading ? "cargando" : state.error ? "error" : "actualizado"}</span>
          <span>Ultima lectura: {dateLabel(state.refreshedAt)}</span>
          {state.freshness ? <span>{state.freshness.quality.sourceLabel}</span> : null}
          {state.error ? <span>{state.error}</span> : null}
        </div>

        <div className={styles.charts}>
          <article className={styles.chartCard}>
            <header className={styles.chartHeader}>
              <div>
                <span>pc.tablet-catalog-freshness-grid</span>
                <h3>Frescura de catalogo por Tablet</h3>
              </div>
              <span>{state.freshness?.quality.dataStatus ?? "partial"}</span>
            </header>
            <div className={styles.chartBody}>
              <FreshnessChart envelope={state.freshness} />
            </div>
            <footer className={styles.footer}>
              <span>{state.freshness?.quality.confidence.level ?? "low"} confianza</span>
              <span>{state.freshness?.quality.fallbackReason ?? "server partial"}</span>
            </footer>
          </article>

          <article className={styles.chartCard}>
            <header className={styles.chartHeader}>
              <div>
                <span>pc.sync-command-lifecycle-timeline</span>
                <h3>Lifecycle de comandos catalogo</h3>
              </div>
              <span>{state.lifecycle?.data.length ?? 0} eventos</span>
            </header>
            <div className={styles.chartBody}>
              <LifecycleChart envelope={state.lifecycle} />
            </div>
            <footer className={styles.footer}>
              <span>ok {lifecycleSummary.applied} / rej {lifecycleSummary.rejected}</span>
              <span>con {lifecycleSummary.conflicted} / dup {lifecycleSummary.duplicated}</span>
            </footer>
          </article>
        </div>
      </div>
    </section>
  );
}
