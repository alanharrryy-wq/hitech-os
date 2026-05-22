"use client";

import { useEffect, useMemo, useState } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { requestJson } from "@/lib/pos/cart-state";
import type { PendingSendStatus, SyncPanelResponse } from "@/lib/pending-offline-sync/sync-panel-contract";
import { filterSyncItems } from "@/lib/pending-offline-sync/sync-panel-view-model";
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

const DEFAULT_SYNC_BUSINESS_ID = "biz_tablet_standalone";

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

function dispatchMessage(result: DispatchResult | null) {
  if (!result) return "Sin intento de envío todavía.";
  if (result.ok && result.reason === "dispatched") return `Envío ejecutado: ${result.dispatched} evento(s) mandado(s) a PC.`;
  if (result.ok && result.reason === "empty") return "La cola no tenía eventos listos para enviar.";
  if (result.reason === "pc_sync_disabled") return "Sync PC apagado por configuración. La Tablet sigue vendiendo local.";
  if (result.reason === "missing_pc_origin") return "Falta PRISMA_TABLET_PC_ORIGIN. Hay cola local, pero no hay destino PC configurado.";
  if (result.reason === "pc_unavailable") return "PC no respondió al health check. La cola queda guardada localmente.";
  if (result.reason === "dispatcher_in_flight") return "Ya hay un envío en curso. No se duplicó la operación.";
  if (result.reason === "dispatch_failed") return result.error ? `Falló el envío: ${result.error}` : "Falló el envío. La cola quedó protegida para reintento.";
  return `Resultado de sync: ${result.reason}.`;
}

export function PendingOfflineSyncPanelScreen() {
  const [panel, setPanel] = useState<SyncPanelResponse | null>(null);
  const [filter, setFilter] = useState<FilterMode>("needs_attention");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dispatchResult, setDispatchResult] = useState<DispatchResult | null>(null);

  async function loadPanelOnly() {
    const r = await requestJson<SyncPanelResponse>("/api/pos/sync/panel?limit=120");
    setPanel(r.data);
  }

  async function load() {
    setBusy(true);
    setError(null);
    try {
      await loadPanelOnly();
    } catch (e) {
      setError(readError(e));
    } finally {
      setBusy(false);
    }
  }

  async function dispatchNow(force = true) {
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
        const result = await plainJson<DispatchResult>("/api/pos/sync/dispatch", {
          method: "POST",
          body: JSON.stringify({ force: false, source: "sync-panel-open" })
        });
        if (!cancelled) setDispatchResult(result);
      } catch (e) {
        if (!cancelled) setError(readError(e));
      }
      try {
        await loadPanelOnly();
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
            <p>La Tablet puede seguir vendiendo; aquí ves qué falta por enviar o revisar, sin cables pelados en la cara del cajero.</p>
          </div>
          <div className={styles.heroActions}>
            <button className={styles.primaryAction} type="button" onClick={() => void dispatchNow(true)} disabled={busy || sendableCount === 0}>
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
            <small>Ya quedaron cerrados</small>
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
            <div className={styles.empty}>No hay elementos en este filtro. Extraño, casi sospechosamente ordenado.</div>
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

        <section className={styles.diagnostics}>{panel?.diagnostics.map((note) => <span key={note}>{note}</span>)}</section>
      </main>
    </PrismaTabletShellUnified>
  );
}

function readError(error: unknown) {
  if (error instanceof Error) return error.message;
  if (typeof error === "object" && error && "message" in error) {
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message.trim()) return message;
  }
  return "No se pudo revisar pendientes.";
}
