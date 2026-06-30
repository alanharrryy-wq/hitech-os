"use client";

import { useEffect, useMemo, useState } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { requestJson } from "@/lib/pos/cart-state";
import type { PendingSendStatus, SyncPanelResponse } from "@/lib/pending-offline-sync/sync-panel-contract";
import { filterSyncItems } from "@/lib/pending-offline-sync/sync-panel-view-model";
import { CatalogPullPanel } from "./catalog-pull-panel";
import { PRISMA_ORIGINAL_CUSTOMER } from "../../../../../shared/customer/prisma-original-customer";
import styles from "./pending-offline-sync-panel.module.css";

type FilterMode = "all" | "needs_attention" | PendingSendStatus;

type DispatchResult = {
  ok: boolean;
  reason: string;
  dispatched: number;
  batchId?: string | null;
  error?: string;
  forced?: boolean;
  health?: {
    ok?: boolean;
    enabled?: boolean;
    status?: string;
    url?: string | null;
    httpStatus?: number;
    error?: string | null;
  };
};

type LicenseStatusResponse = {
  ok: boolean;
  data?: {
    status?: {
      state?: string;
      plan?: string | null;
      assignmentState?: string;
      operationalDecision?: string;
    };
  };
};

type TabletPcHealth = {
  ok?: boolean;
  enabled?: boolean;
  status?: string;
  url?: string | null;
  error?: string | null;
};

const DEFAULT_SYNC_BUSINESS_ID = PRISMA_ORIGINAL_CUSTOMER.businessId;

const FILTERS: { key: FilterMode; label: string }[] = [
  { key: "needs_attention", label: "Por atender" },
  { key: "pending", label: "Pendientes" },
  { key: "failed", label: "Fallidos" },
  { key: "conflict", label: "Revisión" },
  { key: "all", label: "Todo" }
];

async function plainJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      ...(init?.body ? { "content-type": "application/json" } : {}),
      ...(init?.headers ?? {})
    }
  });
  const payload = await response.json().catch(() => null);
  if (!payload) throw new Error(`Respuesta inválida desde ${url}.`);
  if (!response.ok) {
    const message = typeof payload?.message === "string" ? payload.message : typeof payload?.error === "string" ? payload.error : `HTTP ${response.status}`;
    throw new Error(message);
  }
  return payload as T;
}

function dispatchTone(result: DispatchResult | null) {
  if (!result) return "neutral";
  if (result.ok) return "ok";
  if (["pc_sync_disabled", "missing_pc_origin", "pc_unavailable", "empty"].includes(result.reason)) return "warn";
  return "danger";
}

function visibleSyncError(message: string | null | undefined) {
  const raw = (message ?? "").trim();
  if (!raw) return "La cola local quedó protegida. Puedes reintentar cuando la PC esté disponible.";
  const lower = raw.toLowerCase();
  if (lower.includes("operation was aborted") || lower.includes("aborterror") || lower.includes("aborted")) {
    return "El envío se interrumpió antes de terminar. La cola local quedó guardada y puedes reintentar sin perder ventas.";
  }
  if (lower.includes("failed to fetch") || lower.includes("networkerror")) {
    return "No se alcanzó la PC en este intento. La venta local sigue disponible y los pendientes quedan guardados.";
  }
  return raw;
}

function dispatchMessage(result: DispatchResult | null) {
  if (!result) return "Sin intento de envío todavía.";
  const targetUrl = result.health?.url ? ` Destino: ${result.health.url}.` : "";
  const lastError = result.health?.error ? ` ${visibleSyncError(result.health.error)}` : result.error ? ` ${visibleSyncError(result.error)}` : "";
  if (result.ok && result.reason === "dispatched") return `Envío ejecutado: ${result.dispatched} evento(s) mandado(s) a PC.`;
  if (result.ok && result.reason === "empty") return "La cola no tenía eventos listos para enviar.";
  if (result.reason === "pc_sync_disabled") return `Sync PC apagado por configuración. La Tablet sigue vendiendo local.${targetUrl}`;
  if (result.reason === "missing_pc_origin") return "Falta configurar el destino PC. Hay cola local, pero no hay destino configurado para enviar.";
  if (result.reason === "pc_unavailable") return `PC no disponible. La cola queda guardada localmente.${targetUrl}${lastError}`;
  if (result.reason === "dispatcher_in_flight") return "Ya hay un envío en curso. No se duplicó la operación.";
  if (result.reason === "dispatch_failed") return `No se pudo completar el envío.${lastError || " La cola quedó protegida para reintento."}`;
  return `Resultado de sync: ${result.reason}.`;
}

function emptyQueueMessage(filter: FilterMode) {
  if (filter === "all" || filter === "needs_attention" || filter === "pending") return "No pending items to send.";
  return "No hay elementos en este filtro.";
}

function licenseStateLabel(state: string | null | undefined) {
  if (state === "active" || state === "development") return "Cuenta autorizada";
  if (state === "offline_grace") return "Cuenta en gracia offline";
  if (state === "missing") return "Activacion pendiente";
  if (state === "expired") return "Licencia vencida";
  if (state === "suspended" || state === "revoked") return "Licencia detenida";
  return "Estado por revisar";
}

function assignmentLabel(state: string | null | undefined) {
  if (state === "assigned") return "Tablet autorizada";
  if (state === "unassigned") return "Tablet pendiente";
  if (state?.startsWith("wrong_")) return "Asignacion no coincide";
  if (state === "exceeded_limit") return "Limite por revisar";
  return "Asignacion pendiente";
}

function pcConnectionLabel(health: TabletPcHealth | null) {
  if (!health) return "Revisando conexion";
  if (health.enabled === false) return "PC no configurada";
  if (health.ok || health.status === "online") return "PC disponible";
  if (health.status === "degraded") return "PC con aviso";
  if (health.status === "offline") return "PC sin respuesta";
  return "PC por revisar";
}

export function PendingOfflineSyncPanelScreen() {
  const [panel, setPanel] = useState<SyncPanelResponse | null>(null);
  const [filter, setFilter] = useState<FilterMode>("needs_attention");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dispatchResult, setDispatchResult] = useState<DispatchResult | null>(null);
  const [license, setLicense] = useState<LicenseStatusResponse["data"] | null>(null);
  const [pcHealth, setPcHealth] = useState<TabletPcHealth | null>(null);

  async function loadPanelOnly() {
    const r = await requestJson<SyncPanelResponse>("/api/pos/sync/panel?limit=120");
    setPanel(r.data);
  }

  async function loadOperationalContext() {
    const [licenseResult, pcResult] = await Promise.allSettled([
      requestJson<LicenseStatusResponse["data"]>("/api/license/status").then((response) => response.data),
      plainJson<TabletPcHealth>("/api/pos/sync/health/pc")
    ]);
    if (licenseResult.status === "fulfilled") setLicense(licenseResult.value);
    if (pcResult.status === "fulfilled") setPcHealth(pcResult.value);
  }

  async function load() {
    setBusy(true);
    setError(null);
    try {
      await Promise.all([loadPanelOnly(), loadOperationalContext()]);
    } catch (e) {
      setError(readError(e));
    } finally {
      setBusy(false);
    }
  }

  async function dispatchNow(force = false) {
    setBusy(true);
    setError(null);
    try {
      const result = await plainJson<DispatchResult>("/api/pos/sync/dispatch", {
        method: "POST",
        body: JSON.stringify({ force, source: "sync-panel" })
      });
      setDispatchResult(result);
      await loadPanelOnly();
    } catch (e) {
      setError(readError(e));
      try {
        await loadPanelOnly();
      } catch {}
    } finally {
      setBusy(false);
    }
  }

  async function retryFailed() {
    setBusy(true);
    setError(null);
    try {
      await requestJson<{ updated: number; message: string }>("/api/pos/sync/retry", {
        method: "POST",
        body: JSON.stringify({
          businessId: DEFAULT_SYNC_BUSINESS_ID,
          includeFailed: true,
          includePending: false
        })
      });
      const result = await plainJson<DispatchResult>("/api/pos/sync/dispatch", {
        method: "POST",
        body: JSON.stringify({ force: true, source: "sync-panel-retry" })
      });
      setDispatchResult(result);
      await loadPanelOnly();
    } catch (e) {
      setError(readError(e));
      try {
        await loadPanelOnly();
      } catch {}
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      setBusy(true);
      setError(null);
      try {
        await Promise.all([loadPanelOnly(), loadOperationalContext()]);
      } catch (e) {
        if (!cancelled) setError(readError(e));
      } finally {
        if (!cancelled) setBusy(false);
      }
    }
    void boot();
    return () => {
      cancelled = true;
    };
  }, []);

  const items = useMemo(() => (panel ? filterSyncItems(panel.items, filter) : []), [panel, filter]);
  const tone = panel?.summary.risk === "danger" ? "danger" : panel?.summary.risk === "warn" ? "warn" : "ok";
  const sendableCount = panel ? panel.summary.pending + panel.summary.failed : 0;
  const retryableCount = panel ? panel.summary.failed + panel.summary.conflict : 0;
  const noteTone = dispatchTone(dispatchResult);
  const licenseStatus = license?.status;
  const lastCheckedLabel = panel?.summary.lastCheckedAt ? new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date(panel.summary.lastCheckedAt)) : "sin revision";

  return (
    <PrismaTabletShellUnified
      currentPath="/sync"
      title="Pendientes y conexión"
      subtitle="Lo que quedó guardado localmente, lo que falló y lo que necesita atención."
      status={<TabletShellStatusPill tone={tone}>{panel?.summary.headline ?? "Revisando"}</TabletShellStatusPill>}
    >
      <main className={styles.page}>
        <section className={styles.hero}>
          <div>
            <span>Continuidad operativa</span>
            <h1>{panel?.summary.operatorMessage ?? "Revisando trabajo local"}</h1>
            <p>La Tablet puede seguir vendiendo; aquí ves qué falta por enviar o revisar con datos reales de la cola local.</p>
          </div>
          <div className={styles.heroActions}>
            <button className={styles.primaryAction} type="button" onClick={() => void dispatchNow(false)} disabled={busy || sendableCount === 0}>
              {busy ? "Trabajando" : "Enviar pendientes"}
            </button>
            <button className={styles.secondaryAction} type="button" onClick={() => void load()} disabled={busy}>
              Actualizar estado
            </button>
            <button type="button" onClick={() => void retryFailed()} disabled={busy || retryableCount === 0}>
              Reintentar fallidos
            </button>
          </div>
        </section>

        {dispatchResult ? <div className={[styles.dispatchNote, styles[`dispatchNote_${noteTone}`]].join(" ")}>{dispatchMessage(dispatchResult)}</div> : null}
        {error ? <div className={styles.alert} role="alert">{error}</div> : null}

        <section className={styles.accountGrid} aria-label="Cuenta, licencia y equipos vinculados">
          <article>
            <span>Cliente</span>
            <strong>{PRISMA_ORIGINAL_CUSTOMER.displayName}</strong>
            <small>Cuenta local de venta</small>
          </article>
          <article>
            <span>Licencia</span>
            <strong>{licenseStateLabel(licenseStatus?.state)}</strong>
            <small>{licenseStatus?.plan ?? PRISMA_ORIGINAL_CUSTOMER.planLabel}</small>
          </article>
          <article>
            <span>Tablet</span>
            <strong>{assignmentLabel(licenseStatus?.assignmentState)}</strong>
            <small>{PRISMA_ORIGINAL_CUSTOMER.tabletTerminalName}</small>
          </article>
          <article>
            <span>PC</span>
            <strong>{pcConnectionLabel(pcHealth)}</strong>
            <small>Venta local disponible aunque PC no responda</small>
          </article>
        </section>

        <CatalogPullPanel />

        <section className={styles.kpis}>
          <article>
            <span>Pendientes</span>
            <strong>{panel?.summary.pending ?? 0}</strong>
            <small>Guardados para enviar</small>
          </article>
          <article>
            <span>Fallidos</span>
            <strong>{panel?.summary.failed ?? 0}</strong>
            <small>Requieren reintento</small>
          </article>
          <article>
            <span>Revisión</span>
            <strong>{panel?.summary.conflict ?? 0}</strong>
            <small>Atención antes de enviar</small>
          </article>
          <article>
            <span>Confirmados</span>
            <strong>{panel?.summary.acked ?? 0}</strong>
            <small>Confirmados por el flujo</small>
          </article>
        </section>

        <section className={styles.filterBar}>
          {FILTERS.map((f) => (
            <button key={f.key} type="button" onClick={() => setFilter(f.key)} className={filter === f.key ? styles.activeFilter : undefined}>
              {f.label}
            </button>
          ))}
        </section>

        <section className={styles.queue}>
          {items.length === 0 ? (
            <div className={styles.empty}>{emptyQueueMessage(filter)}</div>
          ) : (
            items.map((item) => (
              <article className={[styles.item, styles[`risk_${item.risk}`]].join(" ")} key={item.id}>
                <div>
                  <span>{item.statusLabel}</span>
                  <h2>{item.title}</h2>
                  <p>{item.description}</p>
                </div>
                <aside>
                  <strong>{item.attempts}</strong>
                  <small>intentos</small>
                  {item.canRetry ? <em>Reintento disponible</em> : <em>Sin acción requerida</em>}
                </aside>
              </article>
            ))
          )}
        </section>

        <details className={styles.supportDetails}>
          <summary>Detalles de soporte</summary>
          <section className={styles.diagnostics}>
            <span>Cliente: {PRISMA_ORIGINAL_CUSTOMER.displayName}</span>
            <span>Ultima revision: {lastCheckedLabel}</span>
            {pcHealth?.url ? <span>Destino PC configurado</span> : null}
            {panel?.diagnostics.map((note) => <span key={note}>{note}</span>)}
          </section>
        </details>
      </main>
    </PrismaTabletShellUnified>
  );
}

function readError(error: unknown) {
  if (error instanceof Error) return visibleSyncError(error.message);
  if (typeof error === "object" && error && "message" in error) {
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message.trim()) return visibleSyncError(message);
  }
  return "No se pudo revisar pendientes. La cola local queda protegida.";
}
