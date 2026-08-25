"use client";

import { useEffect, useMemo, useState } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { requestJson } from "@/lib/pos/cart-state";
import type { PendingSendStatus, SyncPanelResponse, SyncRetryPreparationResult } from "@/lib/pending-offline-sync/sync-panel-contract";
import { filterSyncItems } from "@/lib/pending-offline-sync/sync-panel-view-model";
import { CatalogPullPanel } from "./catalog-pull-panel";
import { PRISMA_ORIGINAL_CUSTOMER } from "../../../../../shared/customer/prisma-original-customer";
import styles from "./pending-offline-sync-panel.module.css";

type FilterMode = "all" | "needs_attention" | PendingSendStatus;
type ActionMode = "loading" | "refreshing" | "sending" | "retrying" | "reconciling" | null;

type DispatchResult = {
  ok: boolean;
  reason: string;
  dispatched: number;
  batchId?: string | null;
  error?: string;
  forced?: boolean;
  reconciliation?: {
    ok?: boolean;
    reason?: string;
    counts?: {
      acked?: number;
      conflict?: number;
      failed?: number;
      skipped?: number;
    };
  } | null;
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
const QUEUE_PREVIEW_LIMIT = 8;

const FILTERS: { key: FilterMode; label: string }[] = [
  { key: "needs_attention", label: "Por atender" },
  { key: "pending", label: "Pendientes" },
  { key: "sent", label: "Enviados" },
  { key: "failed", label: "Fallidos" },
  { key: "conflict", label: "Revisión" },
  { key: "acked", label: "Confirmados" },
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
  if (["pc_sync_disabled", "missing_pc_origin", "pc_unavailable", "empty", "partial", "remote_results_applied_from_non_ok_response"].includes(result.reason)) return "warn";
  return "danger";
}

function visibleSyncError(message: string | null | undefined) {
  const raw = (message ?? "").trim();
  if (!raw) return "Los pendientes quedaron guardados. Puedes reintentar cuando la PC esté disponible.";
  const lower = raw.toLowerCase();
  if (lower.includes("operation was aborted") || lower.includes("aborterror") || lower.includes("aborted")) {
    return "El envío se interrumpió antes de terminar. Los pendientes quedaron guardados y puedes reintentar sin perder ventas.";
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
  const ackedByReconciliation = result.reconciliation?.counts?.acked ?? 0;
  if (ackedByReconciliation > 0) return `PC confirmó ${ackedByReconciliation} movimiento(s) que estaban enviados; Tablet los marcó como confirmados.`;
  if (result.ok && result.reason === "dispatched") return `Envío ejecutado: ${result.dispatched} pendiente(s) mandado(s) a PC.`;
  if (result.ok && result.reason === "empty") return "No había pendientes nuevos; se revisó si había enviados esperando confirmación.";
  if (result.reason === "partial") return `PC recibió ${result.dispatched} pendiente(s), pero respondió con avisos. Revisa la lista: lo aceptado se confirma y lo pendiente queda protegido para reintento.`;
  if (result.reason === "remote_results_applied_from_non_ok_response") return "PC respondió con rechazo o aviso. La Tablet conservó los pendientes que no quedaron confirmados.";
  if (result.reason === "pc_sync_disabled") return `Envío a PC apagado por configuración. La Tablet sigue vendiendo local.${targetUrl}`;
  if (result.reason === "missing_pc_origin") return "Falta configurar el destino PC. Hay pendientes guardados, pero no hay destino configurado para enviar.";
  if (result.reason === "pc_unavailable") return `PC no disponible. Los pendientes quedan guardados localmente.${targetUrl}${lastError}`;
  if (result.reason === "dispatcher_in_flight") return "Ya hay un envío en curso. No se duplicó la operación.";
  if (result.reason === "dispatch_failed") return `No se pudo completar el envío.${lastError || " Los pendientes quedaron protegidos para reintento."}`;
  return `Resultado de envío: ${result.reason}.`;
}

function retryPreparationMessage(result: SyncRetryPreparationResult | null) {
  if (!result) return "";
  if (result.requested !== null) return `Reintento: ${result.updated}/${result.requested} preparadas · ${result.skipped ?? 0} omitidas.`;
  return `Reintento: ${result.updated} operación(es) preparadas.`;
}

function compactOperationalValue(value: string | null | undefined) {
  const text = (value ?? "").trim();
  if (!text) return "";
  return text.length > 28 ? `${text.slice(0, 12)}…${text.slice(-8)}` : text;
}

function operationTime(value: string | null | undefined) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "short", timeStyle: "short" }).format(date);
}

function emptyQueueMessage(filter: FilterMode, confirmed: boolean) {

  if (!confirmed) return "Estado de cola sin confirmar. Actualiza el panel para revisar los movimientos reales.";
  if (filter === "all" || filter === "needs_attention" || filter === "pending") return "No hay pendientes para enviar.";
  return "No hay elementos en este filtro.";
}

function filterTitle(filter: FilterMode) {
  if (filter === "needs_attention") return "Por atender";
  if (filter === "pending") return "Pendientes por enviar";
  if (filter === "failed") return "Fallidos";
  if (filter === "conflict") return "En revisión";
  if (filter === "sent") return "Enviados";
  if (filter === "acked") return "Confirmados";
  return "Todo";
}

function licenseStateLabel(state: string | null | undefined) {
  if (state === "active" || state === "development") return "Cuenta autorizada";
  if (state === "offline_grace") return "Cuenta en gracia offline";
  if (state === "missing") return "Activación pendiente";
  if (state === "expired") return "Licencia vencida";
  if (state === "suspended" || state === "revoked") return "Licencia detenida";
  return "Estado por revisar";
}

function assignmentLabel(state: string | null | undefined) {
  if (state === "assigned") return "Tablet autorizada";
  if (state === "unassigned") return "Tablet pendiente";
  if (state?.startsWith("wrong_")) return "Asignación no coincide";
  if (state === "exceeded_limit") return "Límite por revisar";
  return "Asignación pendiente";
}

function pcConnectionLabel(health: TabletPcHealth | null) {
  if (!health) return "Revisando conexión";
  if (health.enabled === false) return "PC no configurada";
  if (health.ok || health.status === "online") return "PC disponible";
  if (health.status === "degraded") return "PC con aviso";
  if (health.status === "offline") return "PC sin respuesta";
  return "PC por revisar";
}

function pcConnectionTone(health: TabletPcHealth | null) {
  if (!health) return "neutral";
  if (health.enabled === false) return "warn";
  if (health.ok || health.status === "online") return "ok";
  if (health.status === "degraded") return "warn";
  return "danger";
}

function syncHeadline(panel: SyncPanelResponse | null, confirmed: boolean, hasError: boolean) {
  if (hasError) return "Estado de pendientes sin confirmar";
  if (!panel || !confirmed) return "Revisando pendientes";
  if (panel.summary.failed > 0 || panel.summary.conflict > 0) return "Pendientes que requieren atención";
  if (panel.summary.pending > 0) return "Pendientes por enviar";
  return "Pendientes al día";
}

export function SyncWorkspace() {
  const [panel, setPanel] = useState<SyncPanelResponse | null>(null);
  const [filter, setFilter] = useState<FilterMode>("needs_attention");
  const [actionMode, setActionMode] = useState<ActionMode>(null);
  const [showAll, setShowAll] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [panelUnverified, setPanelUnverified] = useState(true);
  const [dispatchResult, setDispatchResult] = useState<DispatchResult | null>(null);
  const [retryResult, setRetryResult] = useState<SyncRetryPreparationResult | null>(null);
  const [license, setLicense] = useState<LicenseStatusResponse["data"] | null>(null);
  const [pcHealth, setPcHealth] = useState<TabletPcHealth | null>(null);
  const busy = actionMode !== null;

  async function loadPanelOnly() {
    try {
      const r = await requestJson<SyncPanelResponse>("/api/pos/sync/panel?limit=120");
      setPanel(r.data);
      setPanelUnverified(false);
    } catch (panelError) {
      setPanelUnverified(true);
      throw panelError;
    }
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
    setRetryResult(null);
    setActionMode("refreshing");
    setError(null);
    try {
      await Promise.all([loadPanelOnly(), loadOperationalContext()]);
    } catch (e) {
      setError(readError(e));
    } finally {
      setActionMode(null);
    }
  }

  async function dispatchNow(force = false) {
    setRetryResult(null);
    setActionMode("sending");
    setError(null);
    try {
      const result = await plainJson<DispatchResult>("/api/pos/sync/dispatch", {
        method: "POST",
        body: JSON.stringify({ force, reconcileSent: true, source: "sync-panel" })
      });
      setDispatchResult(result);
      await Promise.all([loadPanelOnly(), loadOperationalContext()]);
    } catch (e) {
      setError(readError(e));
      try {
        await loadPanelOnly();
      } catch {}
    } finally {
      setActionMode(null);
    }
  }

  async function retryFailed() {
    setActionMode("retrying");
    setError(null);
    try {
      const prepared = await requestJson<SyncRetryPreparationResult>("/api/pos/sync/retry", {
        method: "POST",
        body: JSON.stringify({
          businessId: DEFAULT_SYNC_BUSINESS_ID,
          includeFailed: true,
          includePending: false
        })
      });
      setRetryResult(prepared.data);
      const result = await plainJson<DispatchResult>("/api/pos/sync/dispatch", {
        method: "POST",
        body: JSON.stringify({ force: true, reconcileSent: true, source: "sync-panel-retry" })
      });
      setDispatchResult(result);
      await Promise.all([loadPanelOnly(), loadOperationalContext()]);
    } catch (e) {
      setError(readError(e));
      try {
        await loadPanelOnly();
      } catch {}
    } finally {
      setActionMode(null);
    }
  }

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      setActionMode("loading");
      setError(null);
      try {
        await Promise.all([loadPanelOnly(), loadOperationalContext()]);
      } catch (e) {
        if (!cancelled) setError(readError(e));
      } finally {
        if (!cancelled) setActionMode(null);
      }
    }
    void boot();
    return () => {
      cancelled = true;
    };
  }, []);

  const panelConfirmed = Boolean(panel && !panelUnverified && actionMode === null);
  const items = useMemo(() => (panel && panelConfirmed ? filterSyncItems(panel.items, filter) : []), [panel, panelConfirmed, filter]);
  const visibleItems = useMemo(() => showAll ? items : items.slice(0, QUEUE_PREVIEW_LIMIT), [items, showAll]);
  const hiddenItems = Math.max(0, items.length - visibleItems.length);
  const summaryRisk = panelConfirmed ? panel?.summary.risk : null;
  const tone = summaryRisk === "ok" ? "ok" : summaryRisk === "warn" ? "warn" : summaryRisk === "danger" ? "danger" : "neutral";
  const pendingOrFailedCount = panelConfirmed && panel ? panel.summary.pending + panel.summary.failed : 0;
  const sentAwaitingAckCount = panelConfirmed && panel ? panel.summary.sent : 0;
  const sendableCount = pendingOrFailedCount + sentAwaitingAckCount;
  const retryableCount = panelConfirmed && panel ? panel.summary.failed : 0;
  const primaryActionLabel = pendingOrFailedCount > 0 ? "Enviar pendientes" : sentAwaitingAckCount > 0 ? "Confirmar enviados" : "Enviar pendientes";
  const noteTone = dispatchTone(dispatchResult);
  const pcTone = pcConnectionTone(pcHealth);
  const licenseStatus = license?.status;
  const headline = syncHeadline(panel, panelConfirmed, panelUnverified && actionMode === null);
  const lastCheckedLabel = panelConfirmed && panel?.summary.lastCheckedAt
    ? new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date(panel.summary.lastCheckedAt))
    : "sin confirmar";
  const queueMetric = (value: number | undefined) => panelConfirmed && typeof value === "number" ? value : "—";
  const activeStatusMessage = actionMode === "sending"
    ? "Enviando pendientes a PC..."
    : actionMode === "retrying"
      ? "Preparando reintento..."
      : actionMode === "refreshing" || actionMode === "loading"
        ? "Actualizando estado..."
        : retryResult ? `${retryPreparationMessage(retryResult)} ${dispatchMessage(dispatchResult)}` : dispatchMessage(dispatchResult);

  return (
    <PrismaTabletShellUnified
      currentPath="/sync"
      title="Pendientes y conexión"
      subtitle="Lo que quedó guardado localmente, lo que falló y lo que necesita atención."
      status={<TabletShellStatusPill tone={tone}>{headline}</TabletShellStatusPill>}
      showRouteHeader={false}
    >
      <main className={styles.page}>
        <section className={styles.hero}>
          <div>
            <span>Continuidad operativa</span>
            <h1>{headline}</h1>
            <p>La Tablet puede seguir vendiendo; aquí ves qué falta por enviar, confirmar, reintentar o revisar.</p>
            <div className={styles.heroMeta} aria-label="Estado de conexión y revisión">
              <span className={[styles.metaPill, styles[`metaPill_${pcTone}`]].join(" ")}>{pcConnectionLabel(pcHealth)}</span>
              <span className={styles.metaPill}>Revisado {lastCheckedLabel}</span>
              <span className={styles.metaPill}>{panelConfirmed && panel ? `${panel.summary.total} movimientos en cola` : "Cola sin confirmar"}</span>
            </div>
          </div>
          <div className={styles.heroActions}>
            <button className={styles.primaryAction} type="button" onClick={() => void dispatchNow(false)} disabled={busy || sendableCount === 0}>
              {actionMode === "sending" ? "Enviando..." : primaryActionLabel}
            </button>
            <button className={styles.secondaryAction} type="button" onClick={() => void load()} disabled={busy}>
              {actionMode === "refreshing" || actionMode === "loading" ? "Actualizando..." : "Actualizar estado"}
            </button>
            <button type="button" onClick={() => void retryFailed()} disabled={busy || retryableCount === 0}>
              {actionMode === "retrying" ? "Reintentando..." : "Reintentar fallidos"}
            </button>
          </div>
        </section>

        {busy || dispatchResult || retryResult ? <div className={[styles.dispatchNote, styles[`dispatchNote_${busy ? "neutral" : noteTone}`]].join(" ")} role="status" aria-live="polite">{activeStatusMessage}</div> : null}
        {error ? <div className={styles.alert} role="alert">{error}</div> : null}

        <section className={styles.kpis}>
          <article>
            <span>Pendientes</span>
            <strong>{queueMetric(panel?.summary.pending)}</strong>
            <small>Guardados para enviar</small>
          </article>
          <article>
            <span>Enviados</span>
            <strong>{queueMetric(panel?.summary.sent)}</strong>
            <small>Esperando confirmación</small>
          </article>
          <article>
            <span>Fallidos</span>
            <strong>{queueMetric(panel?.summary.failed)}</strong>
            <small>Requieren reintento</small>
          </article>
          <article>
            <span>Revisión</span>
            <strong>{queueMetric(panel?.summary.conflict)}</strong>
            <small>Requieren revisión; no se reintentan automáticamente</small>
          </article>
          <article>
            <span>Confirmados</span>
            <strong>{queueMetric(panel?.summary.acked)}</strong>
            <small>Confirmados por el flujo</small>
          </article>
        </section>

        <section className={styles.queuePanel} aria-label="Movimientos pendientes">
          <div className={styles.queueHeader}>
            <div>
              <span>Lista operativa</span>
              <h2>{filterTitle(filter)}</h2>
              <p>{!panelConfirmed ? "Estado de cola sin confirmar." : items.length > QUEUE_PREVIEW_LIMIT && !showAll ? `Mostrando ${QUEUE_PREVIEW_LIMIT} de ${items.length}. Usa "Ver todos" solo para revisar uno por uno.` : `${items.length} movimiento(s) visibles.`}</p>
            </div>
            {panelConfirmed && items.length > QUEUE_PREVIEW_LIMIT ? (
              <button className={styles.showMoreButton} type="button" onClick={() => setShowAll((value) => !value)}>
                {showAll ? "Ver menos" : `Ver todos (${hiddenItems} más)`}
              </button>
            ) : null}
          </div>

          <div className={styles.filterBar}>
            {FILTERS.map((f) => (
              <button key={f.key} type="button" onClick={() => { setFilter(f.key); setShowAll(false); }} className={filter === f.key ? styles.activeFilter : undefined}>
                {f.label}
              </button>
            ))}
          </div>

          <div className={styles.queue}>
            {visibleItems.length === 0 ? (
              <div className={styles.empty}>{emptyQueueMessage(filter, panelConfirmed)}</div>
            ) : (
              visibleItems.map((item) => (
                <article className={[styles.item, styles[`risk_${item.risk}`]].join(" ")} key={item.id}>
                  <div>
                    <span>{item.statusLabel}</span>
                    <h2>{item.title}</h2>
                    <p>{item.description}</p>
                    <details>
                      <summary>Detalles de operación</summary>
                      <div className={styles.filterBar}>
                        {item.provenance.source ? <span className={styles.metaPill}>Origen: {compactOperationalValue(item.provenance.source)}</span> : null}
                        {item.provenance.storeId ? <span className={styles.metaPill}>Tienda: {compactOperationalValue(item.provenance.storeId)}</span> : null}
                        {item.provenance.terminalId ? <span className={styles.metaPill}>Terminal: {compactOperationalValue(item.provenance.terminalId)}</span> : null}
                        {item.provenance.deviceId ? <span className={styles.metaPill}>Dispositivo: {compactOperationalValue(item.provenance.deviceId)}</span> : null}
                        {item.provenance.actorId ? <span className={styles.metaPill}>Operador: {compactOperationalValue(item.provenance.actorId)}</span> : null}
                      </div>
                      <p>
                        {item.delivery.remoteLifecycleStatus
                          ? `Estado PC: ${item.delivery.remoteLifecycleStatus}`
                          : "Sin estado remoto persistido todavía."}
                        {item.delivery.remoteLedgerId ? ` · Ledger: ${compactOperationalValue(item.delivery.remoteLedgerId)}` : ""}
                      </p>
                      {item.delivery.lastAttemptAt ? <p>Último intento: {operationTime(item.delivery.lastAttemptAt)}</p> : null}
                      {item.delivery.ackedAt ? <p>Confirmado: {operationTime(item.delivery.ackedAt)}</p> : null}
                      {item.delivery.conflictedAt ? <p>Conflicto detectado: {operationTime(item.delivery.conflictedAt)}</p> : null}
                      {item.delivery.remoteConflictCode ? <p>Motivo de conflicto: {item.delivery.remoteConflictCode}</p> : null}
                      {item.delivery.remoteRejectedReason ? <p>Último rechazo: {item.delivery.remoteRejectedReason}</p> : null}
                      {item.resolutionOwner === "pc_backoffice" ? <p><strong>Revisión en PC / Backoffice.</strong> Tablet conserva la evidencia; no resuelve conflictos aquí.</p> : null}
                    </details>
                  </div>
                  <aside>
                    <strong>{item.attempts}</strong>
                    <small>intentos</small>
                    {item.canRetry ? <em>Reintento disponible</em> : item.status === "conflict" ? <em>Revisión requerida</em> : <em>Sin acción requerida</em>}
                  </aside>
                </article>
              ))
            )}
          </div>
        </section>

        <details className={styles.supportDetails}>
          <summary>Cuenta y equipos</summary>
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
        </details>

        <details className={styles.supportDetails}>
          <summary>Actualizar catálogo</summary>
          <CatalogPullPanel />
        </details>

        <details className={styles.supportDetails}>
          <summary>Detalle adicional</summary>
          <section className={styles.diagnostics}>
            <span>Cliente: {PRISMA_ORIGINAL_CUSTOMER.displayName}</span>
            <span>Última revisión: {lastCheckedLabel}</span>
            {pcHealth?.url ? <span>Destino PC configurado</span> : null}
            {panelConfirmed ? panel?.diagnostics.map((note) => <span key={note}>{note}</span>) : <span>Estado de cola sin confirmar</span>}
          </section>
        </details>
      </main>
    </PrismaTabletShellUnified>
  );
}

export const PendingOfflineSyncPanelScreen = SyncWorkspace;

function readError(error: unknown) {
  if (error instanceof Error) return visibleSyncError(error.message);
  if (typeof error === "object" && error && "message" in error) {
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message.trim()) return visibleSyncError(message);
  }
  return "No se pudo revisar pendientes. La cola local queda protegida.";
}
