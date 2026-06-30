"use client";

import { useEffect, useMemo, useState, type KeyboardEvent } from "react";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { getPrismaMobileDataReadiness, type PrismaMobileHealthTone } from "@/lib/prisma-app/prisma-mobile-view-model";
import { sourceLabel } from "@/lib/prisma-app/prisma-mobile-api-client";
import { formatRelativeFetchLabel, formatSignedMxnFromCents } from "@/lib/prisma-app/prisma-mobile-formatters";
import { PrismaMobileCommandCenter } from "./PrismaMobileCommandCenter";
import { PrismaMobileActionInbox } from "./PrismaMobileActionInbox";
import { PrismaMobileDailyBrief } from "./PrismaMobileDailyBrief";
import { PrismaMobileDecisionLedger } from "./PrismaMobileDecisionLedger";
import { PrismaMobilePulseTimeline } from "./PrismaMobilePulseTimeline";
import { PrismaMobileHealthRadar } from "./PrismaMobileHealthRadar";
import { PrismaMobileMetricCard } from "./PrismaMobileMetricCard";
import { PrismaMobileCrystalCommand } from "./PrismaMobileCrystalCommand";
import {
  PrismaMobileActionPanel,
  PrismaMobileAlertsPanel,
  PrismaMobileBranchesPanel,
  PrismaMobileCashPanel,
  PrismaMobileInventoryPanel,
  PrismaMobileReportsPanel,
  PrismaMobileSalesChart
} from "./PrismaMobilePanels";
import styles from "./prisma-mobile-dashboard.module.css";

type LoadState = "idle" | "loading" | "ready" | "refreshing" | "error";

type PremiumTabId = "resumen" | "caja" | "alertas" | "inventario" | "sync";

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
};

const healthToneClass: Record<PrismaMobileHealthTone, string> = {
  sano: styles.healthOk,
  revisar: styles.healthReview,
  urgente: styles.healthUrgent,
  offline: styles.healthOffline
};

const TAB_ORDER: PremiumTabId[] = ["resumen", "caja", "alertas", "inventario", "sync"];

function focusTab(id: PremiumTabId) {
  window.requestAnimationFrame(() => {
    document.getElementById(`prisma-mobile-tab-${id}`)?.focus();
  });
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
    <section
      className={styles.dataReadinessPanel}
      data-readiness-level={readiness.level}
      data-prisma-zone={readinessZone}
      aria-label="Madurez y calidad de datos"
    >
      <header>
        <span>{readiness.label}</span>
        <h4>{readiness.headline}</h4>
        <p>{readiness.detail}</p>
      </header>

      {/* MOBILE_PREMIUM_POLISH_PHASE_2 */}
      <div className={styles.premiumPolishRailNote} data-prisma-zone="mobile-premium-polish-rail">
        <span>Modo supervisor</span>
        <strong>No opera POS core.</strong>
        <p>Si Tablet está local/offline, Mobile degrada a lectura, cache o estado no disponible.</p>
      </div>
      <div className={styles.dataReadinessMeta}>
        <span>{readiness.sourceSummary}</span>
        <span>Ventas: {readiness.salesState === "with_sales" ? "con tickets" : readiness.salesState === "empty" ? "sin tickets hoy" : "no disponible"}</span>
        <span>Inventario: {readiness.inventoryState === "with_items" ? "con SKUs" : readiness.inventoryState === "empty" ? "sin SKUs" : "no disponible"}</span>
        <span>Sync: {readiness.syncState}</span>
      </div>
      <div className={styles.dataReadinessGrid}>
        <article>
          <strong>Hechos</strong>
          <ul>{readiness.facts.map((fact) => <li key={fact}>{fact}</li>)}</ul>
        </article>
        <article>
          <strong>Siguiente acción</strong>
          <ul>{readiness.actions.map((action) => <li key={`${action.title}:${action.owner}`}><b>{action.title}</b><small>{action.detail}</small></li>)}</ul>
        </article>
      </div>
    </section>
  );
}

export function PrismaMobilePremiumNavigator({ clientSnapshot, operations, loadState, onRefresh, onClearCache }: Props) {
  const [activeTab, setActiveTab] = useState<PremiumTabId>("resumen");
  const snapshot = clientSnapshot.snapshot;
  const salesRhythmChart = snapshot.chartViewModels.find((chart) => chart.chartKey === "sales-rhythm-hourly") ?? null;
  const badUpstreams = snapshot.health.upstreams.filter((upstream) => !upstream.ok).length;
  const syncSignals = clientSnapshot.errors.length + badUpstreams + (clientSnapshot.stale ? 1 : 0);

  useEffect(() => {
    function openHealthRadar() {
      setActiveTab("sync");
      focusTab("sync");
    }
    function openAlerts() {
      setActiveTab("alertas");
      focusTab("alertas");
    }
    function openCash() {
      setActiveTab("caja");
      focusTab("caja");
    }
    window.addEventListener("prisma:open-health-radar", openHealthRadar);
    window.addEventListener("prisma:open-alerts", openAlerts);
    window.addEventListener("prisma:open-cash", openCash);
    return () => {
      window.removeEventListener("prisma:open-health-radar", openHealthRadar);
      window.removeEventListener("prisma:open-alerts", openAlerts);
      window.removeEventListener("prisma:open-cash", openCash);
    };
  }, []);

  const tabs = useMemo(() => ([
    {
      id: "resumen" as const,
      label: "Resumen",
      eyebrow: "Vista ejecutiva",
      title: "Pulso del negocio sin abrir PC",
      detail: "Venta, tickets, salud general y acciones recomendadas en una sola lectura.",
      badge: snapshot.summary.urgentAlerts > 0 ? snapshot.summary.urgentAlerts.toString() : "hoy"
    },
    {
      id: "caja" as const,
      label: "Caja",
      eyebrow: "Lectura de caja",
      title: "Caja como vista de supervisión, no corte POS",
      detail: "Lectura móvil opcional para revisar flujo. Tablet Solo mantiene cobro, corte, ticket y operación offline.",
      badge: snapshot.salesToday.tickets > 0 ? snapshot.salesToday.tickets.toString() : "0"
    },
    {
      id: "alertas" as const,
      label: "Alertas",
      eyebrow: "Bandeja priorizada",
      title: "Excepciones con dueño y siguiente acción",
      detail: "Cada alerta conserva dueño, evidencia y siguiente paso operativo.",
      badge: snapshot.alerts.counts.total > 0 ? snapshot.alerts.counts.total.toString() : "ok"
    },
    {
      id: "inventario" as const,
      label: "Inventario",
      eyebrow: "Stock y sucursales",
      title: "Productos y tiendas que pueden pegarle a venta",
      detail: "Señales de reabasto, quiebre, sobrestock y salud por sucursal.",
      badge: (snapshot.inventoryWatchlist.counts.critical + snapshot.inventoryWatchlist.counts.reorder).toString()
    },
    {
      id: "sync" as const,
      label: "Sync",
      eyebrow: "Conexión y confianza",
      title: "Radar de salud, timeline y calidad del dato",
      detail: "Estado de fuentes, eventos, evidencia y próximas revisiones sin abrir reportes largos.",
      badge: syncSignals > 0 ? syncSignals.toString() : "ok"
    }
  ]), [snapshot, syncSignals]);

  const activeIndex = TAB_ORDER.indexOf(activeTab);
  const active = tabs.find((tab) => tab.id === activeTab) ?? tabs[0];

  function selectTab(nextTab: PremiumTabId) {
    setActiveTab(nextTab);
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
    setActiveTab(nextTab);
    focusTab(nextTab);
  }

  return (
    <section className={styles.premiumNavigator} aria-labelledby="prisma-mobile-premium-nav-title">
      <header className={styles.premiumNavigatorHeader}>
        <div>
          <span>PRISMA App · Pulso operativo</span>
          <h2 id="prisma-mobile-premium-nav-title">Pulso por prioridad</h2>
          <p>Mobile supervisa. Tablet Solo vende sola. Esta vista premium ordena señales, alertas y reportes sin ser requisito para vender, cobrar, cortar caja ni operar offline.</p>
        </div>
        <aside data-prisma-zone="mobile-sync-state">
          <span>Fuente activa</span>
          <strong>{sourceLabel(clientSnapshot.source)}</strong>
          <small>{formatRelativeFetchLabel(clientSnapshot.fetchedAt)}{clientSnapshot.stale ? " · respaldo local" : " · lectura fresca"}</small>
        </aside>
      </header>

      {/* MOBILE_OPTIONAL_ADDER_BOUNDARY_PHASE_1 */}
      <section className={styles.optionalAdderBoundaryCompact} data-prisma-zone="mobile-optional-adder-boundary">
        <strong>Mobile supervisa.</strong>
        <span>Tablet Solo vende sola. PC y Mobile son adders opcionales; Cloudflare y soporte remoto son opcionales.</span>
      </section>

      <nav className={styles.premiumTabRail} role="tablist" aria-label="Secciones operativas PRISMA" onKeyDown={handleTabKeyDown}>
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

      <section
        id={`prisma-mobile-panel-${active.id}`}
        className={styles.premiumTabPanel}
        role="tabpanel"
        aria-labelledby={`prisma-mobile-tab-${active.id}`}
      >
        <header className={styles.premiumPanelIntro}>
          <span>{active.eyebrow}</span>
          <h3>{active.title}</h3>
          <p>{active.detail}</p>
        </header>

        {activeTab === "resumen" ? (
          <div className={styles.premiumPanelStack}>
            <PrismaMobileReadinessPanel clientSnapshot={clientSnapshot} />
            <section className={styles.controlPanel} aria-label="Controles móviles" data-prisma-zone="mobile-sync-state">
              <div><span>Fuente activa</span><strong>{sourceLabel(clientSnapshot.source)}</strong></div>
              <div><span>Caja</span><strong>{snapshot.cashCurrent.status}</strong></div>
              <div><span>Diferencia</span><strong>{formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents)}</strong></div>
              <button type="button" onClick={onRefresh} disabled={loadState === "refreshing"}>{loadState === "refreshing" ? "Actualizando..." : "Actualizar"}</button>
              <button type="button" className={styles.secondaryButton} onClick={onClearCache}>Limpiar caché</button>
            </section>
            <PrismaMobileCommandCenter clientSnapshot={clientSnapshot} />
            <section className={styles.metricGrid} aria-label="KPIs principales" data-prisma-zone="mobile-kpi-grid">
              {snapshot.summary.kpis.map((metric) => <PrismaMobileMetricCard key={metric.key} metric={metric} />)}
            </section>
            <section className={styles.operationsGrid} aria-label="Semáforo operativo">
              {operations.map((item) => <article key={item.label} className={healthToneClass[item.tone]}><span>{item.label}</span><strong>{item.value}</strong><small>{item.detail}</small></article>)}
            </section>
            <PrismaMobileActionPanel actions={snapshot.summary.quickActions} />
          </div>
        ) : null}

        {activeTab === "caja" ? (
          <div className={styles.premiumPanelStack}>
            <PrismaMobileCrystalCommand clientSnapshot={clientSnapshot} mode="operation" />
            <PrismaMobileCashPanel cash={snapshot.cashCurrent} />
            <PrismaMobileSalesChart chart={salesRhythmChart} />
            <PrismaMobileReportsPanel cards={snapshot.reportsDaily.cards} />
            <PrismaMobileDailyBrief clientSnapshot={clientSnapshot} />
            <PrismaMobileCrystalCommand clientSnapshot={clientSnapshot} mode="brief" />
          </div>
        ) : null}

        {activeTab === "alertas" ? (
          <div className={styles.premiumPanelStack}>
            <PrismaMobileCrystalCommand clientSnapshot={clientSnapshot} mode="alerts" />
            <PrismaMobileActionInbox clientSnapshot={clientSnapshot} />
            <PrismaMobileAlertsPanel alerts={snapshot.alerts.alerts} />
            <PrismaMobileDecisionLedger clientSnapshot={clientSnapshot} />
          </div>
        ) : null}

        {activeTab === "inventario" ? (
          <div className={styles.premiumPanelStack}>
            <PrismaMobileCrystalCommand clientSnapshot={clientSnapshot} mode="operation" />
            <PrismaMobileInventoryPanel items={snapshot.inventoryWatchlist.items} />
            <PrismaMobileBranchesPanel branches={snapshot.branches.branches} />
          </div>
        ) : null}

        {activeTab === "sync" ? (
          <div className={styles.premiumPanelStack}>
            <PrismaMobileCrystalCommand clientSnapshot={clientSnapshot} mode="health" />
            <PrismaMobileReadinessPanel clientSnapshot={clientSnapshot} />
            {clientSnapshot.errors.length > 0 ? (
              <section className={styles.warningPanel} aria-label="Advertencias de carga" data-prisma-zone="mobile-error-state">
                <strong>La app está usando respaldo porque una lectura falló.</strong>
                <ul>{clientSnapshot.errors.slice(0, 3).map((error) => <li key={error}>{error}</li>)}</ul>
              </section>
            ) : null}
            <PrismaMobileHealthRadar clientSnapshot={clientSnapshot} />
            <PrismaMobileCrystalCommand clientSnapshot={clientSnapshot} mode="timeline" />
            <PrismaMobilePulseTimeline clientSnapshot={clientSnapshot} />
          </div>
        ) : null}
      </section>
    </section>
  );
}
