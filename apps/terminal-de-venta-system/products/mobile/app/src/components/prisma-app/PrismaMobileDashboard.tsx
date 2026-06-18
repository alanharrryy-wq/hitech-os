"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { sourceLabel, loadPrismaMobileSnapshot } from "@/lib/prisma-app/prisma-mobile-api-client";
import { clearCachedPrismaMobileSnapshot } from "@/lib/prisma-app/prisma-mobile-cache";
import { formatRelativeFetchLabel } from "@/lib/prisma-app/prisma-mobile-formatters";
import { prismaMobileErrorMessage } from "@/lib/prisma-app/prisma-mobile-error";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { buildPrismaMobileOperationsList, derivePrismaMobileHero, type PrismaMobileHealthTone } from "@/lib/prisma-app/prisma-mobile-view-model";
import { PrismaMobilePremiumNavigator } from "./PrismaMobilePremiumNavigator";
import { PrismaMobileCrystalCommand } from "./PrismaMobileCrystalCommand";
import { PrismaMobileMultiContextSwitcher } from "./PrismaMobileMultiContextSwitcher";
import styles from "./prisma-mobile-dashboard.module.css";

type LoadState = "idle" | "loading" | "ready" | "refreshing" | "error";

const healthToneClass: Record<PrismaMobileHealthTone, string> = {
  sano: styles.healthOk,
  revisar: styles.healthReview,
  urgente: styles.healthUrgent,
  offline: styles.healthOffline
};

const LOADING_SHELL_COPY = "Consultando fuentes conectadas y respaldo local cuando no hay señal. Mobile supervisa. Tablet Solo vende sola.";
const CRYSTAL_SHELL_BACKGROUND =
  "radial-gradient(circle at 12% 8%, rgba(100,216,255,0.24), transparent 24rem), radial-gradient(circle at 90% 4%, rgba(255,216,137,0.18), transparent 22rem), linear-gradient(180deg, #f5f8fc 0%, #eef3f8 58%, #e8f0f8 100%)";

function readinessZone(level: string) {
  if (level === "ready") return "mobile-success-state";
  if (level === "empty") return "mobile-empty-state";
  if (level === "offline" || level === "blocked") return "mobile-offline-state";
  return "mobile-sync-state";
}

function LoadingShell() {
  return (
    <main
      className={styles.mobileRoot}
      data-prisma-product="mobile"
      data-prisma-state="loading"
      data-prisma-zone="mobile-app-shell"
      style={{ background: CRYSTAL_SHELL_BACKGROUND, color: "#102033", width: "100%" }}
    >
      <section className={styles.loadingShell} aria-label="Cargando PRISMA App" data-prisma-zone="mobile-loading-state">
        <div className={styles.loadingPhone}>
          <i />
          <i />
          <i />
          <i />
        </div>
        <div>
          <span>PRISMA App</span>
          <h1>Cargando operación móvil</h1>
          <p suppressHydrationWarning>{LOADING_SHELL_COPY}</p>
        </div>
      </section>
    </main>
  );
}

export function PrismaMobileDashboard() {
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [clientSnapshot, setClientSnapshot] = useState<PrismaMobileClientSnapshot | null>(null);
  const [manualError, setManualError] = useState<string | null>(null);

  const load = useCallback(async (mode: "initial" | "refresh" = "initial") => {
    setLoadState((current) => (mode === "refresh" && current === "ready" ? "refreshing" : "loading"));
    setManualError(null);
    try {
      const nextSnapshot = await loadPrismaMobileSnapshot();
      setClientSnapshot(nextSnapshot);
      setLoadState("ready");
    } catch (error) {
      setManualError(prismaMobileErrorMessage(error, "No se pudo cargar PRISMA App."));
      setLoadState("error");
    }
  }, []);

  useEffect(() => {
    let alive = true;
    async function boot() {
      setLoadState("loading");
      try {
        const nextSnapshot = await loadPrismaMobileSnapshot();
        if (alive) {
          setClientSnapshot(nextSnapshot);
          setLoadState("ready");
        }
      } catch (error) {
        if (alive) {
          setManualError(prismaMobileErrorMessage(error, "No se pudo cargar PRISMA App."));
          setLoadState("error");
        }
      }
    }
    void boot();
    return () => {
      alive = false;
    };
  }, []);

  const hero = useMemo(() => (clientSnapshot ? derivePrismaMobileHero(clientSnapshot.snapshot) : null), [clientSnapshot]);
  const operations = useMemo(() => (clientSnapshot ? buildPrismaMobileOperationsList(clientSnapshot.snapshot) : []), [clientSnapshot]);
  const clearCacheAndRefresh = useCallback(() => {
    clearCachedPrismaMobileSnapshot();
    void load("refresh");
  }, [load]);

  if (!clientSnapshot || !hero) {
    if (loadState === "error") {
      return (
        <main
          className={styles.mobileRoot}
          data-prisma-product="mobile"
          data-prisma-state="error"
          data-prisma-zone="mobile-app-shell"
          style={{ background: CRYSTAL_SHELL_BACKGROUND, color: "#102033", width: "100%" }}
        >
          <section className={styles.errorShell} data-prisma-zone="mobile-error-state">
            <span>PRISMA App</span>
            <h1>No se pudo cargar la supervisión móvil</h1>
            <p>{manualError ?? "Error desconocido al preparar la vista móvil."}</p>
            <p className={styles.optionalAdderBoundaryMicro}>Tablet Solo puede seguir vendiendo localmente sin Mobile, PC, Cloudflare ni internet.</p>
            <button type="button" onClick={() => void load("refresh")}>Reintentar</button>
          </section>
        </main>
      );
    }
    return <LoadingShell />;
  }

  const snapshot = clientSnapshot.snapshot;
  const readiness = snapshot.summary.dataReadiness;
  const commandMetrics = [
    { label: "Tickets", value: snapshot.salesToday.tickets.toString(), detail: snapshot.salesToday.averageTicketLabel },
    { label: "Alertas", value: hero.urgentAlerts.toString(), detail: snapshot.alerts.counts.total > 0 ? `${snapshot.alerts.counts.total} activas` : "sin alertas activas" },
    { label: "Stock critico", value: hero.inventoryCriticalCount.toString(), detail: `${snapshot.inventoryWatchlist.counts.reorder} por reponer` }
  ];
  const primaryAction = snapshot.summary.quickActions[0] ?? null;
  const bridgeLabel = readiness.level === "ready"
    ? "Bridge listo"
    : readiness.level === "offline" || readiness.level === "blocked"
      ? "Bridge no disponible"
      : "Datos parciales";

  return (
    <main
      className={styles.mobileRoot}
      data-prisma-panel="mobile.workspace"
      data-prisma-product="mobile"
      data-prisma-surface="mobile"
      data-prisma-route="/"
      data-prisma-readiness={snapshot.summary.dataReadiness.level}
      data-prisma-source={clientSnapshot.source}
      data-prisma-stale={clientSnapshot.stale ? "true" : "false"}
      data-prisma-zone="mobile-app-shell"
      style={{ background: CRYSTAL_SHELL_BACKGROUND, color: "#102033", width: "100%" }}
    >
      <section className={styles.dashboardShell} aria-labelledby="prisma-mobile-dashboard-title">
        <header className={styles.brandHeader} data-prisma-zone="mobile-brand-header">
          <div className={styles.brandIdentity}>
            <span className={styles.brandLogo} data-prisma-zone="mobile-logo" aria-hidden="true">
              <img src="/prisma-mobile-premium-mark.svg" alt="" />
            </span>
            <div className={styles.brandText}>
              <p>PRISMA</p>
              <h1 id="prisma-mobile-dashboard-title">Crystal Command</h1>
              <span>Supervision operativa movil</span>
            </div>
          </div>
          <div className={styles.brandMeta}>
            <span className={`${styles.statusChip} ${healthToneClass[hero.health]}`} data-prisma-zone="mobile-status-chip">{bridgeLabel}</span>
            <span>{formatRelativeFetchLabel(clientSnapshot.fetchedAt)}</span>
            <span>{snapshot.alerts.counts.total} alertas</span>
          </div>
        </header>

        <section className={styles.crystalFirstViewport} aria-label="Resumen operativo PRISMA Crystal Command" data-prisma-zone="mobile-crystal-first-viewport">
          <div className={styles.crystalDecisionHeader}>
            <div>
              <span>Resumen operativo</span>
              <h2>{hero.headline}</h2>
              <p>{hero.subline}</p>
            </div>
            <span className={`${styles.statusChip} ${healthToneClass[hero.health]}`} data-prisma-zone={readinessZone(readiness.level)}>
              {readiness.label}
            </span>
          </div>

          <PrismaMobileMultiContextSwitcher clientSnapshot={clientSnapshot} />

          <PrismaMobileCrystalCommand clientSnapshot={clientSnapshot} mode="home" />

          <div className={styles.crystalQuickRead} data-prisma-zone="mobile-kpi-grid">
            <article data-prisma-zone="mobile-primary-metric">
              <span>Venta hoy</span>
              <strong>{snapshot.salesToday.totalSalesLabel}</strong>
              <small>{hero.salesDelta} · ticket promedio {snapshot.salesToday.averageTicketLabel}</small>
            </article>
            {commandMetrics.map((metric) => (
              <article key={metric.label} data-prisma-zone="mobile-kpi-card">
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
                <small>{metric.detail}</small>
              </article>
            ))}
          </div>

          <div className={styles.crystalActionStrip} aria-label="Accion recomendada principal">
            <div>
              <span>Accion recomendada</span>
              <strong>{primaryAction?.title ?? "Sin acciones urgentes"}</strong>
              <p>{primaryAction?.detail ?? "La operacion no requiere una accion inmediata desde Mobile."}</p>
            </div>
            <div className={styles.commandMetaStrip} aria-label="Estado de datos moviles">
              <span className={styles.sourceChip}>{sourceLabel(clientSnapshot.source)}</span>
              <span data-prisma-zone="mobile-sync-state">{clientSnapshot.stale ? "Mostrando respaldo local" : "Lectura fresca"}</span>
              <span>{readiness.sourceSummary}</span>
            </div>
          </div>
        </section>

        <PrismaMobilePremiumNavigator
          clientSnapshot={clientSnapshot}
          operations={operations}
          loadState={loadState}
          onRefresh={() => void load("refresh")}
          onClearCache={clearCacheAndRefresh}
        />
      </section>
    </main>
  );
}
