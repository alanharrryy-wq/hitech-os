"use client";

import { useEffect, useMemo, useState, type KeyboardEvent, type ReactNode } from "react";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { getPrismaMobileDataReadiness, type PrismaMobileHealthTone } from "@/lib/prisma-app/prisma-mobile-view-model";
import { sourceLabel } from "@/lib/prisma-app/prisma-mobile-api-client";
import { formatRelativeFetchLabel } from "@/lib/prisma-app/prisma-mobile-formatters";
import { PrismaMobileCommandCenter } from "./PrismaMobileCommandCenter";
import { PrismaMobileActionInbox } from "./PrismaMobileActionInbox";
import { PrismaMobileDailyBrief } from "./PrismaMobileDailyBrief";
import { PrismaMobileDecisionLedger } from "./PrismaMobileDecisionLedger";
import { PrismaMobilePulseTimeline } from "./PrismaMobilePulseTimeline";
import { PrismaMobileHealthRadar } from "./PrismaMobileHealthRadar";
import styles from "./prisma-mobile-dashboard.module.css";

type LoadState = "idle" | "loading" | "ready" | "refreshing" | "error";

type PremiumTabId = "inicio" | "ventas" | "operacion" | "alertas" | "stock" | "sistema";

type OperationItem = {
  readonly label: string;
  readonly value: string;
  readonly detail: string;
  readonly tone: PrismaMobileHealthTone;
};

type Props = {
  clientSnapshot: PrismaMobileClientSnapshot;
  operations: readonly OperationItem[];
  loadState: LoadState;
  onRefresh: () => void;
  onClearCache: () => void;
  systemCrystalHome: ReactNode;
  systemContextSwitcher: ReactNode;
};

const TAB_ORDER: PremiumTabId[] = ["inicio", "ventas", "operacion", "alertas", "stock", "sistema"];

const toneClass: Record<PrismaMobileHealthTone, string> = {
  sano: styles.healthOk,
  revisar: styles.healthReview,
  urgente: styles.healthUrgent,
  offline: styles.healthOffline
};

const alertToneClass: Record<string, string> = {
  critica: styles.alertCritical,
  alta: styles.alertHigh,
  media: styles.alertMedium,
  info: styles.alertInfo
};

const inventoryToneClass: Record<string, string> = {
  critico: styles.inventoryCritical,
  reponer: styles.inventoryReorder,
  normal: styles.inventoryNormal,
  sobrestock: styles.inventoryOverstock
};

function initialTabFromHash(): PremiumTabId {
  if (typeof window === "undefined") return "inicio";
  const hash = window.location.hash.replace("#", "") as PremiumTabId;
  return TAB_ORDER.includes(hash) ? hash : "inicio";
}

function focusTab(id: PremiumTabId) {
  window.requestAnimationFrame(() => {
    document.getElementById(`prisma-mobile-tab-${id}`)?.focus();
  });
}

function CompactMetric({ label, value, detail, primary }: { label: string; value: string | number; detail?: string; primary?: boolean }) {
  return (
    <article className={primary ? styles.primaryMetricCard : styles.compactMetricCard} data-prisma-zone={primary ? "mobile-primary-metric" : "mobile-kpi-card"}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </article>
  );
}

function PrismaMobileReadinessPanel({ clientSnapshot }: { clientSnapshot: PrismaMobileClientSnapshot }) {
  const readiness = getPrismaMobileDataReadiness(clientSnapshot.snapshot);
  const readinessZone = readiness.level === "ready"
    ? "mobile-success-state"
    : readiness.level === "empty"
      ? "mobile-empty-state"
      : readiness.level === "offline" || readiness.level === "blocked"
        ? "mobile-offline-state"
        : "mobile-sync-state";

  return (
    <section className={styles.dataReadinessPanel} data-readiness-level={readiness.level} data-prisma-zone={readinessZone} aria-label="Madurez y calidad de datos">
      <header>
        <span>{readiness.label}</span>
        <h4>{readiness.headline}</h4>
        <p>{readiness.detail}</p>
      </header>
      <div className={styles.dataReadinessMeta}>
        <span>{readiness.sourceSummary}</span>
        <span>Ventas: {readiness.salesState === "with_sales" ? "con tickets" : readiness.salesState === "empty" ? "sin tickets hoy" : "no disponible"}</span>
        <span>Sync: {readiness.syncState}</span>
      </div>
      <div className={styles.dataReadinessGrid}>
        <article>
          <strong>Hechos</strong>
          <p>{readiness.facts[0] ?? "Sin diagnostico adicional."}</p>
        </article>
        <article>
          <strong>Siguiente accion</strong>
          <p>{readiness.actions[0]?.title ?? "Actualizar lectura"}</p>
        </article>
      </div>
    </section>
  );
}

export function PrismaMobilePremiumNavigator({ clientSnapshot, operations, loadState, onRefresh, onClearCache, systemCrystalHome, systemContextSwitcher }: Props) {
  const [activeTab, setActiveTab] = useState<PremiumTabId>(() => initialTabFromHash());
  const snapshot = clientSnapshot.snapshot;
  const readiness = getPrismaMobileDataReadiness(snapshot);
  const primaryAction = snapshot.summary.quickActions[0] ?? null;
  const topAlert = snapshot.alerts.alerts[0] ?? null;
  const visibleAlerts = snapshot.alerts.alerts.slice(0, 4);
  const visibleStock = snapshot.inventoryWatchlist.items.slice(0, 3);
  const visibleSales = snapshot.salesToday.timeline.slice(-6);
  const urgentStock = snapshot.inventoryWatchlist.counts.critical + snapshot.inventoryWatchlist.counts.reorder;
  const badUpstreams = snapshot.health.upstreams.filter((upstream) => !upstream.ok).length;
  const syncSignals = clientSnapshot.errors.length + badUpstreams + (clientSnapshot.stale ? 1 : 0);

  useEffect(() => {
    function openSales() {
      selectTab("ventas");
      focusTab("ventas");
    }
    function openHealthRadar() {
      selectTab("sistema");
      focusTab("sistema");
    }
    function openAlerts() {
      selectTab("alertas");
      focusTab("alertas");
    }
    function openCash() {
      selectTab("ventas");
      focusTab("ventas");
    }
    function onHashChange() {
      setActiveTab(initialTabFromHash());
    }
    window.addEventListener("prisma:open-sales", openSales);
    window.addEventListener("prisma:open-health-radar", openHealthRadar);
    window.addEventListener("prisma:open-alerts", openAlerts);
    window.addEventListener("prisma:open-cash", openCash);
    window.addEventListener("hashchange", onHashChange);
    return () => {
      window.removeEventListener("prisma:open-sales", openSales);
      window.removeEventListener("prisma:open-health-radar", openHealthRadar);
      window.removeEventListener("prisma:open-alerts", openAlerts);
      window.removeEventListener("prisma:open-cash", openCash);
      window.removeEventListener("hashchange", onHashChange);
    };
  }, []);

  const tabs = useMemo(() => ([
    { id: "inicio" as const, label: "Inicio", eyebrow: "INICIO", title: "Pulso movil del negocio", detail: `${sourceLabel(clientSnapshot.source)} · ${readiness.sourceSummary}`, badge: snapshot.summary.urgentAlerts > 0 ? snapshot.summary.urgentAlerts.toString() : "ok" },
    { id: "ventas" as const, label: "Ventas", eyebrow: "VENTAS", title: "Ventas visibles", detail: snapshot.salesToday.tickets > 0 ? "Actividad real disponible en snapshot." : "Sin ventas reales disponibles todavia.", badge: snapshot.salesToday.tickets.toString() },
    { id: "operacion" as const, label: "Operacion", eyebrow: "OPERACION", title: "Operacion", detail: "Tablet, PC, Mobile y sync en una matriz corta.", badge: operations.filter((item) => item.tone !== "sano").length > 0 ? operations.filter((item) => item.tone !== "sano").length.toString() : "ok" },
    { id: "alertas" as const, label: "Alertas", eyebrow: "ALERTAS", title: "Alertas", detail: snapshot.alerts.counts.total > 0 ? "Priorizadas por severidad y siguiente accion." : "Sin alertas activas.", badge: snapshot.alerts.counts.total > 0 ? snapshot.alerts.counts.total.toString() : "ok" },
    { id: "stock" as const, label: "Stock", eyebrow: "STOCK", title: "Stock operativo", detail: visibleStock.length > 0 ? "Senales de inventario disponibles." : "Stock movil pendiente de Tablet POS.", badge: urgentStock.toString() },
    { id: "sistema" as const, label: "Sistema", eyebrow: "SISTEMA", title: "Sistema", detail: "Contratos, fuente y diagnostico subordinados.", badge: syncSignals > 0 ? syncSignals.toString() : "ok" }
  ]), [operations, readiness.headline, snapshot, syncSignals, urgentStock, visibleStock.length]);

  const activeIndex = TAB_ORDER.indexOf(activeTab);
  const active = tabs.find((tab) => tab.id === activeTab) ?? tabs[0];

  function selectTab(nextTab: PremiumTabId) {
    setActiveTab(nextTab);
    if (typeof window !== "undefined" && window.location.hash !== `#${nextTab}`) {
      window.history.replaceState(null, "", `#${nextTab}`);
    }
  }

  function handleTabKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (!["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const currentIndex = activeIndex < 0 ? 0 : activeIndex;
    const nextIndex = event.key === "Home"
      ? 0
      : event.key === "End"
        ? TAB_ORDER.length - 1
        : event.key === "ArrowRight"
          ? (currentIndex + 1) % TAB_ORDER.length
          : (currentIndex - 1 + TAB_ORDER.length) % TAB_ORDER.length;
    const nextTab = TAB_ORDER[nextIndex];
    selectTab(nextTab);
    focusTab(nextTab);
  }

  return (
    <section className={styles.premiumNavigator} aria-labelledby="prisma-mobile-premium-nav-title">
      <section id={`prisma-mobile-panel-${active.id}`} className={styles.premiumTabPanel} role="tabpanel" aria-labelledby={`prisma-mobile-tab-${active.id}`}>
        <header className={styles.screenHeader}>
          <span>{active.eyebrow}</span>
          <h2 id="prisma-mobile-premium-nav-title">{active.title}</h2>
          <p>{active.detail}</p>
        </header>

        {activeTab === "inicio" ? (
          <div className={styles.screenGrid}>
            <section className={styles.metricStrip} data-prisma-zone="mobile-kpi-grid">
              <CompactMetric primary label="Venta hoy" value={snapshot.salesToday.totalSalesLabel} detail={`${snapshot.salesToday.tickets} tickets`} />
              <CompactMetric label="Alertas" value={snapshot.alerts.counts.total} detail={snapshot.alerts.counts.total > 0 ? "activas" : "sin urgentes"} />
              <CompactMetric label="Stock" value={urgentStock} detail={urgentStock > 0 ? "senales" : "estable"} />
            </section>
            <section className={styles.primaryInsightCard}>
              <span>Insight principal</span>
              <strong>{topAlert?.title ?? primaryAction?.title ?? readiness.label}</strong>
              <p>{topAlert?.detail ?? primaryAction?.detail ?? readiness.detail}</p>
            </section>
            <section className={styles.quickActionPills}>
              <button type="button" onClick={onRefresh}>{loadState === "refreshing" ? "Actualizando..." : "Actualizar"}</button>
              <button type="button" onClick={() => selectTab("alertas")}>Ver alertas</button>
              <button type="button" onClick={() => selectTab("sistema")}>Sistema</button>
            </section>
          </div>
        ) : null}

        {activeTab === "ventas" ? (
          <div className={styles.screenGrid}>
            <section className={styles.metricStrip}>
              <CompactMetric primary label="Venta hoy" value={snapshot.salesToday.totalSalesLabel} />
              <CompactMetric label="Tickets" value={snapshot.salesToday.tickets} />
              <CompactMetric label="Ticket prom." value={snapshot.salesToday.averageTicketLabel} />
            </section>
            <section className={styles.salesPulseCard}>
              <header>
                <span>Ritmo de venta</span>
                <strong>{snapshot.salesToday.tickets > 0 ? snapshot.salesToday.strongCategory : "Sin ventas reales disponibles todavia"}</strong>
              </header>
              <div className={styles.miniBars} aria-label="Ritmo de venta por horario">
                {visibleSales.map((point) => <i key={point.hour} style={{ height: point.height }} title={`${point.label}: ${point.amount}`} />)}
              </div>
            </section>
            <section className={styles.sourceSummaryCard}>
              <span>Ultimo dato confiable</span>
              <strong>{formatRelativeFetchLabel(clientSnapshot.fetchedAt)}</strong>
              <p>{readiness.sourceSummary}</p>
            </section>
          </div>
        ) : null}

        {activeTab === "operacion" ? (
          <div className={styles.screenGrid}>
            <section className={styles.statusMatrix}>
              <article><span>Tablet</span><strong>{snapshot.summary.account.tabletDeviceLabel}</strong><small>Base operativa local</small></article>
              <article><span>PC</span><strong>{readiness.pcState === "connected" ? "Conectado" : "No disponible"}</strong><small>{snapshot.summary.account.pcDeviceLabel}</small></article>
              <article><span>Mobile</span><strong>{sourceLabel(clientSnapshot.source)}</strong><small>{clientSnapshot.stale ? "respaldo local" : "lectura fresca"}</small></article>
              <article><span>Sync</span><strong>{readiness.syncState}</strong><small>{readiness.sourceSummary}</small></article>
            </section>
            <section className={styles.signalCard}>
              <span>Senal clave</span>
              <strong>{operations[0]?.value ?? readiness.label}</strong>
              <p>{operations[0]?.detail ?? readiness.detail}</p>
            </section>
            <section className={styles.quickActionPills}>
              <button type="button" onClick={onRefresh}>{loadState === "refreshing" ? "Actualizando..." : "Actualizar"}</button>
              <button type="button" onClick={() => selectTab("sistema")}>Diagnostico</button>
            </section>
          </div>
        ) : null}

        {activeTab === "alertas" ? (
          <div className={styles.screenGrid}>
            <section className={styles.alertCompactList}>
              {visibleAlerts.length > 0 ? visibleAlerts.map((alert) => (
                <article key={alert.id} className={alertToneClass[alert.severity] ?? styles.alertInfo}>
                  <span>{alert.severity}</span>
                  <strong>{alert.title}</strong>
                  <p>{alert.recommendedAction ?? alert.action}</p>
                </article>
              )) : (
                <article>
                  <span>OK</span>
                  <strong>Sin alertas activas</strong>
                  <p>El snapshot no trae excepciones para revisar.</p>
                </article>
              )}
            </section>
          </div>
        ) : null}

        {activeTab === "stock" ? (
          <div className={styles.screenGrid}>
            <section className={styles.metricStrip}>
              <CompactMetric primary label="Critico" value={snapshot.inventoryWatchlist.counts.critical} />
              <CompactMetric label="Reponer" value={snapshot.inventoryWatchlist.counts.reorder} />
              <CompactMetric label="Normal" value={snapshot.inventoryWatchlist.counts.normal} />
            </section>
            <section className={styles.stockCompactList}>
              {visibleStock.length > 0 ? visibleStock.map((item) => (
                <article key={item.sku} className={inventoryToneClass[item.state] ?? styles.inventoryNormal}>
                  <div>
                    <span>{item.sku}</span>
                    <strong>{item.name}</strong>
                    <p>{item.category} · {item.weeklyUnitsSold} u/semana</p>
                  </div>
                  <em>{item.stock}</em>
                </article>
              )) : (
                <article>
                  <div>
                    <span>Inventario</span>
                    <strong>Stock movil pendiente de Tablet POS</strong>
                    <p>Cuando el snapshot entregue SKUs reales, se mostraran aqui.</p>
                  </div>
                </article>
              )}
            </section>
          </div>
        ) : null}

        {activeTab === "sistema" ? (
          <div className={styles.screenGrid}>
            <PrismaMobileReadinessPanel clientSnapshot={clientSnapshot} />
            <section className={styles.systemSignalGrid}>
              <article><span>Fuente</span><strong>{sourceLabel(clientSnapshot.source)}</strong><small>{clientSnapshot.stale ? "respaldo local" : "lectura fresca"}</small></article>
              <article><span>Upstreams</span><strong>{badUpstreams > 0 ? `${badUpstreams} revisar` : "ok"}</strong><small>{formatRelativeFetchLabel(clientSnapshot.fetchedAt)}</small></article>
            </section>
            <details className={styles.systemContractDrawer}>
              <summary><span>Contratos tecnicos</span><strong>Crystal y contexto preservados</strong></summary>
              <div className={styles.systemContractPreview}>
                {systemCrystalHome}
                {systemContextSwitcher}
              </div>
            </details>
            <section className={styles.quickActionPills}>
              <button type="button" onClick={onRefresh}>{loadState === "refreshing" ? "Actualizando..." : "Actualizar"}</button>
              <button type="button" onClick={onClearCache}>Limpiar cache</button>
            </section>
          </div>
        ) : null}
      </section>

      <nav className={styles.premiumTabRail} role="tablist" aria-label="Pantallas operativas PRISMA" onKeyDown={handleTabKeyDown}>
        {tabs.map((tab) => {
          const selected = tab.id === activeTab;
          return (
            <button
              id={`prisma-mobile-tab-${tab.id}`}
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={selected}
              aria-controls={`prisma-mobile-panel-${tab.id}`}
              tabIndex={selected ? 0 : -1}
              className={selected ? styles.premiumTabActive : undefined}
              onClick={() => selectTab(tab.id)}
            >
              <span>{tab.label}</span>
              <strong>{tab.badge}</strong>
            </button>
          );
        })}
      </nav>

      <section className={styles.optionalAdderBoundaryCompact} data-prisma-zone="mobile-optional-adder-boundary">
        <strong>Mobile no es requisito para vender.</strong>
        <span>Mobile supervisa. Tablet Solo vende sola. PC y Mobile son adders opcionales. Cloudflare y soporte remoto son opcionales. Internet no es requisito para venta base Tablet Solo.</span>
      </section>

      <div className={styles.contractMountShelf} aria-hidden="true">
        <PrismaMobileCommandCenter clientSnapshot={clientSnapshot} />
        <PrismaMobileActionInbox clientSnapshot={clientSnapshot} />
        <PrismaMobileDailyBrief clientSnapshot={clientSnapshot} />
        <PrismaMobileDecisionLedger clientSnapshot={clientSnapshot} />
        <PrismaMobileHealthRadar clientSnapshot={clientSnapshot} />
        <PrismaMobilePulseTimeline clientSnapshot={clientSnapshot} />
      </div>
    </section>
  );
}
