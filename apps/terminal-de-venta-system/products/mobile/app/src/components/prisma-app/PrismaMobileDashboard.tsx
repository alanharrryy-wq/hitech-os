"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { sourceLabel, loadPrismaMobileSnapshot } from "@/lib/prisma-app/prisma-mobile-api-client";
import { clearCachedPrismaMobileSnapshot } from "@/lib/prisma-app/prisma-mobile-cache";
import { formatRelativeFetchLabel } from "@/lib/prisma-app/prisma-mobile-formatters";
import { prismaMobileErrorMessage } from "@/lib/prisma-app/prisma-mobile-error";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { buildPrismaMobileOperationsList, derivePrismaMobileHero, type PrismaMobileHealthTone } from "@/lib/prisma-app/prisma-mobile-view-model";
import { PrismaMobileCrystalCommand } from "./PrismaMobileCrystalCommand";
import { PrismaMobileMultiContextSwitcher } from "./PrismaMobileMultiContextSwitcher";
import { PrismaMobilePremiumNavigator } from "./PrismaMobilePremiumNavigator";
import styles from "./prisma-mobile-dashboard.module.css";

type LoadState = "idle" | "loading" | "ready" | "refreshing" | "error";

const healthToneClass: Record<PrismaMobileHealthTone, string> = {
  sano: styles.healthOk,
  revisar: styles.healthReview,
  urgente: styles.healthUrgent,
  offline: styles.healthOffline
};

const LOADING_SHELL_COPY = "Consultando fuentes conectadas y respaldo local cuando no hay senal. Mobile supervisa. Tablet Solo vende sola.";

function readinessZone(level: string) {
  if (level === "ready") return "mobile-success-state";
  if (level === "empty") return "mobile-empty-state";
  if (level === "offline" || level === "blocked") return "mobile-offline-state";
  return "mobile-sync-state";
}

function LoadingShell() {
  return (
    <main
      className={`${styles.mobileRoot} ${styles.atmosphericCloudglassRoot}`}
      data-prisma-product="mobile"
      data-prisma-state="loading"
      data-prisma-zone="mobile-app-shell"
      data-prisma-visual="mobile-cloud-center-premium"
    >
      <section className={styles.loadingShell} aria-label="Cargando PRISMA App" data-prisma-zone="mobile-loading-state">
        <div className={styles.loadingSignalStack} aria-hidden="true">
          <i />
          <i />
          <i />
        </div>
        <div>
          <span>PRISMA App</span>
          <h1>Cargando operacion movil</h1>
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
          className={`${styles.mobileRoot} ${styles.atmosphericCloudglassRoot}`}
          data-prisma-product="mobile"
          data-prisma-state="error"
          data-prisma-zone="mobile-app-shell"
          data-prisma-visual="mobile-cloud-center-premium"
        >
          <section className={styles.errorShell} data-prisma-zone="mobile-error-state">
            <span>PRISMA App</span>
            <h1>No hay datos frescos para supervision movil</h1>
            <p>{manualError ?? "Error desconocido al preparar la vista movil."}</p>
            <div className={styles.errorSignalGrid} aria-label="Que puede hacer el usuario ahora">
              <article>
                <span>1 · Reintentar</span>
                <strong>Pedir snapshot nuevo</strong>
                <p>Vuelve a consultar `/api/mobile/snapshot` sin tocar procesos ni puertos.</p>
              </article>
              <article>
                <span>2 · Respaldo</span>
                <strong>Limpiar cache local</strong>
                <p>Evita quedarse viendo una lectura vieja cuando la fuente ya cambio.</p>
              </article>
              <article>
                <span>3 · Operacion base</span>
                <strong>Tablet sigue vendiendo</strong>
                <p>Mobile supervisa sin convertirse en requisito operativo.</p>
              </article>
            </div>
            <div className={styles.errorActionGrid}>
              <button type="button" onClick={() => void load("refresh")}>Reintentar snapshot</button>
              <button type="button" className={styles.secondaryButton} onClick={clearCacheAndRefresh}>Limpiar cache y reintentar</button>
            </div>
            <p className={styles.optionalAdderBoundaryMicro}>Si el problema sigue, revisa fuentes Tablet/PC. La pantalla no oculta fallas detras del polish visual.</p>
          </section>
        </main>
      );
    }
    return <LoadingShell />;
  }

  const snapshot = clientSnapshot.snapshot;
  const readiness = snapshot.summary.dataReadiness;
  const account = snapshot.summary.account;
  const bridgeLabel = readiness.level === "ready"
    ? "Bridge ok"
    : readiness.level === "offline" || readiness.level === "blocked"
      ? "Sin bridge"
      : "Parcial";

  return (
    <main
      className={`${styles.mobileRoot} ${styles.atmosphericCloudglassRoot}`}
      data-prisma-panel="mobile.workspace"
      data-prisma-product="mobile"
      data-prisma-surface="mobile"
      data-prisma-route="/prisma-app"
      data-prisma-readiness={readiness.level}
      data-prisma-source={clientSnapshot.source}
      data-prisma-stale={clientSnapshot.stale ? "true" : "false"}
      data-prisma-zone="mobile-app-shell"
      data-prisma-visual="mobile-cloud-center-premium"
    >
      <section className={styles.dashboardShell} aria-labelledby="prisma-mobile-dashboard-title">
        <header className={styles.brandHeader} data-prisma-zone="mobile-brand-header">
          <div className={styles.brandIdentity}>
            <span className={styles.brandLogo} data-prisma-zone="mobile-logo" aria-hidden="true">
              <img src="/prisma-mobile-premium-mark.svg" alt="" />
            </span>
            <div className={styles.brandText}>
              <p>Mobile · 3140</p>
              <h1 id="prisma-mobile-dashboard-title">Prisma Mobile Cloud</h1>
              <span>{account.customerName}</span>
            </div>
          </div>
          <div className={styles.brandMeta}>
            <span className={`${styles.statusChip} ${healthToneClass[hero.health]}`} data-prisma-zone="mobile-status-chip" data-prisma-readiness-zone={readinessZone(readiness.level)}>{bridgeLabel}</span>
            <span>{formatRelativeFetchLabel(clientSnapshot.fetchedAt)}</span>
          </div>
        </header>

        <section className={styles.mainScreenHost} data-prisma-zone="mobile-crystal-first-viewport">
          <PrismaMobilePremiumNavigator
            clientSnapshot={clientSnapshot}
            operations={operations}
            loadState={loadState}
            onRefresh={() => void load("refresh")}
            onClearCache={clearCacheAndRefresh}
            systemCrystalHome={<PrismaMobileCrystalCommand clientSnapshot={clientSnapshot} mode="home" />}
            systemContextSwitcher={<PrismaMobileMultiContextSwitcher clientSnapshot={clientSnapshot} />}
          />
        </section>
      </section>
    </main>
  );
}
