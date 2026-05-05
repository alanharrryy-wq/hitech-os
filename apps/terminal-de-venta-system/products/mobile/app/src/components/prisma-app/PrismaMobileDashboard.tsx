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

function LoadingShell() {
  return (
    <main className={styles.mobileRoot} data-prisma-product="mobile" data-prisma-state="loading">
      <section className={styles.loadingShell} aria-label="Cargando PRISMA App">
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
        <main className={styles.mobileRoot} data-prisma-product="mobile" data-prisma-state="error">
          <section className={styles.errorShell}>
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

  return (
    <main className={styles.mobileRoot} data-prisma-product="mobile" data-prisma-surface="prisma.mobile.app">
      <section className={styles.dashboardShell} aria-labelledby="prisma-mobile-dashboard-title">
        <header className={styles.heroPanel}>
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>PRISMA App · Pulso operativo conectado</p>
            <h1 id="prisma-mobile-dashboard-title">{hero.businessName}</h1>
            <strong>{hero.headline}</strong>
            <p>{hero.subline}</p>
            <div className={styles.heroBadges} aria-label="Estado de datos móviles">
              <span className={healthToneClass[hero.health]}>{hero.healthLabel}</span>
              <span>{sourceLabel(clientSnapshot.source)}</span>
              <span>{formatRelativeFetchLabel(clientSnapshot.fetchedAt)}</span>
              {clientSnapshot.stale ? <span>datos con respaldo local</span> : <span>datos frescos</span>}
            </div>
          </div>
          <aside className={styles.phonePreview} aria-label="Resumen móvil principal">
            <div className={styles.phoneChrome}><span /></div>
            <div className={styles.phoneHero}>
              <small>Venta de hoy</small>
              <strong>{snapshot.salesToday.totalSalesLabel}</strong>
              <em>{hero.salesDelta}</em>
            </div>
            <div className={styles.phoneStats}>
              <p><span>Alertas</span><strong>{hero.urgentAlerts}</strong></p>
              <p><span>Stock</span><strong>{hero.inventoryCriticalCount}</strong></p>
              <p><span>Sucursales</span><strong>{hero.branchesToReview}</strong></p>
            </div>
          </aside>
        </header>

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
