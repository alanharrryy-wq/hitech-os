"use client";

import { useMemo, useState } from "react";
import type { ChartPoint, ChartViewModel } from "@/lib/prisma-app/mobile-intelligence";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import styles from "./prisma-crystal-command.module.css";

type Props = {
  clientSnapshot: PrismaMobileClientSnapshot;
  mode: "home" | "operation" | "alerts" | "health" | "timeline" | "brief";
};

const severityClass: Record<string, string> = {
  critical: styles.severityCritical,
  high: styles.severityHigh,
  medium: styles.severityMedium,
  low: styles.severityLow,
  info: styles.severityInfo
};

function money(cents: number | null): string {
  if (cents === null) return "No disponible";
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}

function percent(value: number | null): string {
  return value === null ? "Sin dato" : `${Math.round(value)}%`;
}

function useSelectedPoint(chart: ChartViewModel | null) {
  const [selected, setSelected] = useState<ChartPoint | null>(null);
  const active = selected ?? chart?.points.find((point) => point.y !== null) ?? null;
  return { active, setSelected };
}

function chartByKey(charts: ChartViewModel[], key: string): ChartViewModel | null {
  return charts.find((chart) => chart.chartKey === key) ?? null;
}

function EmptyState({ chart }: { chart: ChartViewModel | null }) {
  return (
    <div className={styles.emptyState}>
      <strong>{chart?.emptyState ?? "Sin datos disponibles."}</strong>
      <span>PRISMA no rellena esta vista con números falsos.</span>
    </div>
  );
}

function EvidenceStrip({ chart }: { chart: ChartViewModel | null }) {
  if (!chart) return null;
  return (
    <div className={styles.evidenceStrip}>
      <span>{chart.source ?? "Snapshot"}</span>
      <span>{typeof chart.confidence === "number" ? `${Math.round(chart.confidence * 100)}% confianza` : "confianza no disponible"}</span>
      <span>{chart.evidence[0]?.summary ?? "evidencia limitada"}</span>
    </div>
  );
}

function HealthGauge({ chart, runtimeMode }: { chart: ChartViewModel | null; runtimeMode: string }) {
  const score = chart?.points[0]?.y ?? null;
  const circumference = 282;
  const offset = score === null ? circumference : circumference - (Math.max(0, Math.min(100, score)) / 100) * circumference;
  return (
    <section className={`${styles.crystalPanel} ${styles.heroGauge}`} aria-label="Operational Health Gauge">
      <header>
        <span>Operational Health</span>
        <h3>{chart?.title ?? "Salud operativa"}</h3>
      </header>
      <button
        type="button"
        className={styles.gaugeButton}
        aria-label={`Abrir Health Radar, salud ${score ?? "desconocida"}`}
        onClick={() => window.dispatchEvent(new CustomEvent("prisma:open-health-radar"))}
      >
        <svg viewBox="0 0 120 72" role="img" aria-hidden="true">
          <path className={styles.gaugeTrack} d="M15 62a45 45 0 0 1 90 0" pathLength={circumference} />
          <path className={styles.gaugeValue} d="M15 62a45 45 0 0 1 90 0" pathLength={circumference} style={{ strokeDashoffset: offset }} />
        </svg>
        <strong>{score === null ? "N/D" : Math.round(score)}</strong>
        <span>{runtimeMode}</span>
      </button>
      <p>{chart?.summary ?? "Sin fuentes suficientes para calcular salud."}</p>
      <EvidenceStrip chart={chart} />
    </section>
  );
}

function SalesRhythmChart({ chart }: { chart: ChartViewModel | null }) {
  const { active, setSelected } = useSelectedPoint(chart);
  const max = Math.max(1, ...(chart?.points.map((point) => point.y ?? 0) ?? [0]));
  return (
    <section className={styles.crystalPanel} aria-label="Sales Rhythm Chart">
      <header>
        <span>Sales Rhythm</span>
        <h3>{chart?.title ?? "Ritmo de ventas"}</h3>
      </header>
      {chart && chart.points.length > 0 ? (
        <div className={styles.barChart}>
          {chart.points.map((point) => (
            <button key={point.x} type="button" onClick={() => setSelected(point)} aria-label={`${point.label}: ${money(point.y)}`}>
              <i style={{ height: `${Math.max(8, ((point.y ?? 0) / max) * 100)}%` }} />
              <span>{point.label}</span>
            </button>
          ))}
        </div>
      ) : <EmptyState chart={chart} />}
      <div className={styles.tooltipLine}>
        <strong>{active ? `${active.label}: ${money(active.y)}` : "Sin punto seleccionado"}</strong>
        <span>{active ? `${active.meta.tickets ?? 0} tickets` : chart?.summary}</span>
      </div>
      <EvidenceStrip chart={chart} />
    </section>
  );
}

function MomentumSparkline({ chart }: { chart: ChartViewModel | null }) {
  const points = chart?.points ?? [];
  const max = Math.max(1, ...points.map((point) => point.y ?? 0));
  const path = points.map((point, index) => {
    const x = points.length <= 1 ? 0 : (index / (points.length - 1)) * 100;
    const y = 42 - (((point.y ?? 0) / max) * 36);
    return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
  }).join(" ");
  const last = points[points.length - 1]?.y ?? null;
  return (
    <section className={`${styles.crystalPanel} ${styles.sparkCard}`} aria-label="Revenue Momentum Sparkline">
      <header>
        <span>Revenue Momentum</span>
        <h3>{chart?.title ?? "Momentum"}</h3>
      </header>
      {points.length > 0 ? (
        <svg viewBox="0 0 100 48" role="img" aria-label={chart?.summary}>
          <path d={path} />
        </svg>
      ) : <EmptyState chart={chart} />}
      <strong>{money(last)}</strong>
      <p>{chart?.summary}</p>
    </section>
  );
}

function InventoryRiskRanking({ chart }: { chart: ChartViewModel | null }) {
  return (
    <section className={styles.crystalPanel} aria-label="Inventory Risk Ranking">
      <header>
        <span>Inventory Risk</span>
        <h3>{chart?.title ?? "Inventario"}</h3>
      </header>
      {chart && chart.points.length > 0 ? (
        <div className={styles.rankingList}>
          {chart.points.map((point) => (
            <button key={point.x} type="button" aria-label={`${point.label}: riesgo ${percent(point.y)}`}>
              <div>
                <strong>{point.label}</strong>
                <span>{point.x} · {point.meta.stockQty ?? "?"} pzas · {point.meta.daysToStockOut ?? "sin velocidad"} días</span>
              </div>
              <i><b style={{ width: `${Math.max(4, point.y ?? 0)}%` }} /></i>
              <em>{percent(point.y)}</em>
            </button>
          ))}
        </div>
      ) : <EmptyState chart={chart} />}
      <EvidenceStrip chart={chart} />
    </section>
  );
}

function AlertSeverityDonut({ chart }: { chart: ChartViewModel | null }) {
  const [filter, setFilter] = useState<string>("all");
  const points = chart?.points ?? [];
  const total = points.reduce((sum, point) => sum + (point.y ?? 0), 0);
  let offset = 0;
  const slices = points.map((point) => {
    const value = point.y ?? 0;
    const dash = total > 0 ? (value / total) * 100 : 0;
    const slice = { point, dash, offset };
    offset += dash;
    return slice;
  });
  return (
    <section className={styles.crystalPanel} aria-label="Alert Severity Donut">
      <header>
        <span>Alert Severity</span>
        <h3>{chart?.title ?? "Alertas"}</h3>
      </header>
      <div className={styles.donutLayout}>
        <svg viewBox="0 0 44 44" role="img" aria-label={chart?.summary}>
          <circle className={styles.donutBase} cx="22" cy="22" r="15.9" />
          {slices.map(({ point, dash, offset: sliceOffset }) => (
            <circle
              key={point.x}
              className={`${styles.donutSlice} ${severityClass[point.x] ?? ""}`}
              cx="22"
              cy="22"
              r="15.9"
              strokeDasharray={`${dash} ${100 - dash}`}
              strokeDashoffset={-sliceOffset}
            />
          ))}
        </svg>
        <div>
          <strong>{total}</strong>
          <span>{filter === "all" ? "alertas" : filter}</span>
        </div>
      </div>
      <div className={styles.segmented}>
        <button type="button" className={filter === "all" ? styles.segmentActive : undefined} onClick={() => setFilter("all")}>Todas</button>
        {points.map((point) => (
          <button key={point.x} type="button" className={filter === point.x ? styles.segmentActive : undefined} onClick={() => setFilter(point.x)}>
            {point.label} {point.y ?? 0}
          </button>
        ))}
      </div>
      <EvidenceStrip chart={chart} />
    </section>
  );
}

function SyncFreshnessChart({ chart }: { chart: ChartViewModel | null }) {
  return (
    <section className={styles.crystalPanel} aria-label="Sync Freshness Outbox Chart">
      <header>
        <span>Sync Freshness</span>
        <h3>{chart?.title ?? "Sync"}</h3>
      </header>
      {chart ? (
        <div className={styles.syncGrid}>
          {chart.points.map((point) => (
            <article key={point.x} data-status={point.status}>
              <span>{point.label}</span>
              <strong>{point.y === null ? "N/D" : point.y}</strong>
            </article>
          ))}
        </div>
      ) : <EmptyState chart={chart} />}
      <p>{chart?.summary}</p>
      <EvidenceStrip chart={chart} />
    </section>
  );
}

function CashVarianceBullet({ chart }: { chart: ChartViewModel | null }) {
  const point = chart?.points[0] ?? null;
  const value = point?.y ?? null;
  const magnitude = value === null ? 0 : Math.min(100, Math.abs(value) / 2000);
  return (
    <section className={styles.crystalPanel} aria-label="Cash Variance Bullet Chart">
      <header>
        <span>Cash Variance</span>
        <h3>{chart?.title ?? "Caja"}</h3>
      </header>
      <div className={styles.bulletTrack}>
        <i />
        <b style={{ width: `${Math.max(3, magnitude)}%` }} />
      </div>
      <strong>{money(value)}</strong>
      <p>{chart?.summary}</p>
    </section>
  );
}

function HealthRadarMini({ chart }: { chart: ChartViewModel | null }) {
  return (
    <section className={styles.crystalPanel} aria-label="Health Radar Chart">
      <header>
        <span>Health Radar</span>
        <h3>{chart?.title ?? "Radar"}</h3>
      </header>
      {chart && chart.points.length > 0 ? (
        <div className={styles.radarGrid}>
          {chart.points.map((point) => (
            <article key={point.x}>
              <span>{point.label}</span>
              <strong>{point.y === null ? "N/D" : `${point.y}`}</strong>
              <i><b style={{ width: `${Math.max(4, point.y ?? 0)}%` }} /></i>
            </article>
          ))}
        </div>
      ) : <EmptyState chart={chart} />}
      <EvidenceStrip chart={chart} />
    </section>
  );
}

function TimelinePreview({ clientSnapshot }: { clientSnapshot: PrismaMobileClientSnapshot }) {
  const events = clientSnapshot.snapshot.timeline.slice(0, 5);
  return (
    <section className={styles.crystalPanel} aria-label="Pulse Timeline">
      <header>
        <span>Pulse Timeline</span>
        <h3>Qué pasó y por qué importa</h3>
      </header>
      <div className={styles.timelineList}>
        {events.map((event) => (
          <button key={event.id} type="button">
            <i />
            <span>{event.source}</span>
            <strong>{event.title}</strong>
            <p>{event.whyItMatters}</p>
          </button>
        ))}
      </div>
    </section>
  );
}

function DailyBriefPreview({ clientSnapshot }: { clientSnapshot: PrismaMobileClientSnapshot }) {
  const report = clientSnapshot.snapshot.reports;
  return (
    <section className={styles.crystalPanel} aria-label="Daily Brief">
      <header>
        <span>Daily Brief</span>
        <h3>Guía de cierre</h3>
      </header>
      <div className={styles.briefGrid}>
        <article><span>Highlights</span>{report.highlights.map((item) => <p key={item}>{item}</p>)}</article>
        <article><span>Riesgos</span>{report.risks.map((item) => <p key={item}>{item}</p>)}</article>
        <article><span>Acciones</span>{report.recommendedActions.slice(0, 4).map((item) => <p key={item}>{item}</p>)}</article>
      </div>
    </section>
  );
}

export function PrismaMobileCrystalCommand({ clientSnapshot, mode }: Props) {
  const snapshot = clientSnapshot.snapshot;
  const charts = snapshot.chartViewModels;
  const chart = useMemo(() => ({
    gauge: chartByKey(charts, "operational-health-gauge"),
    sales: chartByKey(charts, "sales-rhythm-hourly"),
    momentum: chartByKey(charts, "revenue-momentum"),
    inventory: chartByKey(charts, "inventory-risk-ranking"),
    alerts: chartByKey(charts, "alert-severity-donut"),
    sync: chartByKey(charts, "sync-freshness-outbox"),
    cash: chartByKey(charts, "cash-variance-bullet"),
    radar: chartByKey(charts, "health-radar-dimensions")
  }), [charts]);

  if (mode === "home") {
    return (
      <section className={styles.crystalCommand} data-prisma-zone="mobile-crystal-command">
        <HealthGauge chart={chart.gauge} runtimeMode={snapshot.meta.runtimeMode} />
        <MomentumSparkline chart={chart.momentum} />
        <SalesRhythmChart chart={chart.sales} />
        <InventoryRiskRanking chart={chart.inventory} />
        <AlertSeverityDonut chart={chart.alerts} />
        <SyncFreshnessChart chart={chart.sync} />
      </section>
    );
  }

  if (mode === "operation") {
    return (
      <section className={styles.crystalCommand} data-prisma-zone="mobile-crystal-operation">
        <SalesRhythmChart chart={chart.sales} />
        <InventoryRiskRanking chart={chart.inventory} />
        <SyncFreshnessChart chart={chart.sync} />
        <CashVarianceBullet chart={chart.cash} />
      </section>
    );
  }

  if (mode === "alerts") {
    return (
      <section className={styles.crystalCommand} data-prisma-zone="mobile-crystal-alerts">
        <AlertSeverityDonut chart={chart.alerts} />
        <InventoryRiskRanking chart={chart.inventory} />
      </section>
    );
  }

  if (mode === "health") {
    return (
      <section className={styles.crystalCommand} data-prisma-zone="mobile-crystal-health">
        <HealthGauge chart={chart.gauge} runtimeMode={snapshot.meta.runtimeMode} />
        <HealthRadarMini chart={chart.radar} />
        <SyncFreshnessChart chart={chart.sync} />
      </section>
    );
  }

  if (mode === "timeline") {
    return (
      <section className={styles.crystalCommand} data-prisma-zone="mobile-crystal-timeline">
        <TimelinePreview clientSnapshot={clientSnapshot} />
        <AlertSeverityDonut chart={chart.alerts} />
      </section>
    );
  }

  return (
    <section className={styles.crystalCommand} data-prisma-zone="mobile-crystal-brief">
      <DailyBriefPreview clientSnapshot={clientSnapshot} />
      <HealthGauge chart={chart.gauge} runtimeMode={snapshot.meta.runtimeMode} />
    </section>
  );
}
