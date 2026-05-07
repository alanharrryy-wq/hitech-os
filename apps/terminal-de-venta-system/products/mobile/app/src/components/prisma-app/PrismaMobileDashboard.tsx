"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { sourceLabel, loadPrismaMobileSnapshot } from "@/lib/prisma-app/prisma-mobile-api-client";
import { clearCachedPrismaMobileSnapshot } from "@/lib/prisma-app/prisma-mobile-cache";
import { formatRelativeFetchLabel } from "@/lib/prisma-app/prisma-mobile-formatters";
import { prismaMobileErrorMessage } from "@/lib/prisma-app/prisma-mobile-error";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { buildPrismaMobileOperationsList, derivePrismaMobileHero, type PrismaMobileHealthTone } from "@/lib/prisma-app/prisma-mobile-view-model";
import { PrismaMobilePremiumNavigator } from "./PrismaMobilePremiumNavigator";
import styles from "./prisma-mobile-dashboard.module.css";

type LoadState = "idle" | "loading" | "ready" | "refreshing" | "error";

const healthToneClass: Record<PrismaMobileHealthTone, string> = {
  sano: styles.healthOk,
  revisar: styles.healthReview,
  urgente: styles.healthUrgent,
  offline: styles.healthOffline
};

const LOADING_SHELL_COPY = "Consultando fuentes conectadas y respaldo local cuando no hay señal.";
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
            <h1>No se pudo cargar el tablero móvil</h1>
            <p>{manualError ?? "Error desconocido al preparar la vista móvil."}</p>
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
    { label: "Stock critico", value: hero.inventoryCriticalCount.toString(), detail: `${snapshot.inventoryWatchlist.counts.reorder} por reponer` },
    { label: "Sync", value: readiness.syncState, detail: readiness.label }
  ];

  return (
    <main
      className={styles.mobileRoot}
      data-prisma-product="mobile"
      data-prisma-surface="prisma.mobile.app"
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
              <img src="/icons/prisma-app-icon.svg" alt="" />
            </span>
            <div className={styles.brandText}>
              <p>PRISMA App</p>
              <h1 id="prisma-mobile-dashboard-title">PRISMA Pulso</h1>
              <span>Supervisión operativa</span>
            </div>
          </div>
          <div className={styles.brandMeta}>
            <span className={`${styles.statusChip} ${healthToneClass[hero.health]}`} data-prisma-zone="mobile-status-chip">{hero.healthLabel}</span>
            <span>{hero.businessName}</span>
          </div>
        </header>

        <section className={styles.commandCard} aria-label="Estado del negocio" data-prisma-zone="mobile-command-card">
          <div className={styles.commandCardHeader}>
            <div>
              <span>Estado del negocio</span>
              <h2>{hero.headline}</h2>
              <p>{hero.subline}</p>
            </div>
            <span className={`${styles.statusChip} ${healthToneClass[hero.health]}`} data-prisma-zone={readinessZone(readiness.level)}>
              {readiness.label}
            </span>
          </div>

          <div className={styles.commandPrimaryMetric} data-prisma-zone="mobile-primary-metric">
            <span>Venta de hoy</span>
            <strong>{snapshot.salesToday.totalSalesLabel}</strong>
            <small>{hero.salesDelta} · ticket promedio {snapshot.salesToday.averageTicketLabel}</small>
          </div>

          <div className={styles.commandSecondaryGrid} data-prisma-zone="mobile-kpi-grid">
            {commandMetrics.map((metric) => (
              <article key={metric.label} data-prisma-zone="mobile-kpi-card">
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
                <small>{metric.detail}</small>
              </article>
            ))}
          </div>

          <div className={styles.commandMetaStrip} aria-label="Estado de datos móviles">
            <span className={styles.sourceChip}>{sourceLabel(clientSnapshot.source)}</span>
            <span>{formatRelativeFetchLabel(clientSnapshot.fetchedAt)}</span>
            <span data-prisma-zone="mobile-sync-state">{clientSnapshot.stale ? "respaldo local activo" : "lectura fresca"}</span>
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
