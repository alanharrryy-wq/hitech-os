"use client";

import { useEffect, useMemo, useState } from "react";
import { requestJson } from "@/lib/pos/cart-state";
import styles from "./pending-offline-sync-panel.module.css";

type CatalogMode = "delta" | "bootstrap" | "resync";

type CatalogCheckpoint = {
  cursorValue: string | null;
  status: string;
  lifecycleStatus: string | null;
  checkpointAt: string;
  lastAttemptedAt: string | null;
  lastSuccessfulAt: string | null;
};

type CatalogStatus = {
  stream: string;
  targetBusinessId: string;
  terminalId: string;
  pc: {
    enabled: boolean;
    origin: string | null;
    exportPath: string;
  };
  checkpoint: CatalogCheckpoint | null;
  tableCounts: Record<string, number>;
};

type CatalogPullResult = {
  ok: boolean;
  reason: string;
  mode: CatalogMode;
  sourceBusinessId: string | null;
  targetBusinessId: string;
  terminalId: string;
  cursorBefore: string | null;
  cursorAfter: string | null;
  checkpoint: CatalogCheckpoint | null;
  counts: {
    received: number;
    applied: number;
    rejected: number;
    conflict: number;
    duplicate: number;
    byEntity: Record<string, number>;
  };
  findings: Array<{ code: string; severity: string; entityType?: string | null; entityId?: string | null; detail: string }>;
  errors: string[];
  health: {
    enabled: boolean;
    origin: string | null;
    url: string | null;
    status: string;
    httpStatus?: number;
  };
};

async function plainJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      ...(init?.body ? { "content-type": "application/json" } : {}),
      ...(init?.headers ?? {})
    }
  });
  const payload = await response.json().catch(() => null);
  if (!payload) throw new Error(`Respuesta invalida desde ${url}.`);
  if (!response.ok) {
    const message = typeof payload?.message === "string" ? payload.message : typeof payload?.error === "string" ? payload.error : `HTTP ${response.status}`;
    throw new Error(message);
  }
  return payload as T;
}

function readError(error: unknown) {
  if (error instanceof Error) return error.message;
  if (typeof error === "object" && error && "message" in error) {
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message.trim()) return message;
  }
  return "No se pudo revisar catalogo entrante.";
}

function resultTone(result: CatalogPullResult | null) {
  if (!result) return "neutral";
  if (result.ok) return "ok";
  if (["pc_sync_disabled", "missing_pc_origin", "pc_unavailable", "partial"].includes(result.reason)) return "warn";
  return "danger";
}

function resultMessage(result: CatalogPullResult | null) {
  if (!result) return "Sin actualizacion de datos en esta sesion.";
  if (result.ok && result.reason === "applied") return `Catalogo aplicado: ${result.counts.applied} cambio(s), ${result.counts.duplicate} duplicado(s).`;
  if (result.ok && result.reason === "empty") return "PC respondio correctamente; no habia cambios nuevos para aplicar.";
  if (result.reason === "pc_sync_disabled") return "Actualizacion desde PC apagada por configuracion. La Tablet sigue vendiendo local.";
  if (result.reason === "pc_unavailable") return "PC no respondio para actualizar datos. El POS local no se bloquea.";
  if (result.reason === "partial") return `Actualizacion parcial: ${result.counts.applied} aplicado(s), ${result.counts.conflict} por revisar, ${result.counts.rejected} rechazado(s).`;
  if (result.reason === "invalid_payload") return "PC envio datos no validos; no se marco como actualizacion completada.";
  return `Resultado de actualizacion: ${result.reason}.`;
}

function shortDate(value: string | null | undefined) {
  if (!value) return "sin registro";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "sin registro";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function entityLabel(entity: string) {
  const labels: Record<string, string> = {
    Product: "Productos",
    Barcode: "Codigos",
    Brand: "Marcas",
    TaxRate: "Impuestos",
    Supplier: "Proveedores",
    ProductSupplier: "Proveedor por producto",
    PriceList: "Listas de precio",
    PriceListItem: "Precios",
    DropdownCatalog: "Opciones",
    DropdownOption: "Valores"
  };
  return labels[entity] ?? entity.replace(/([a-z])([A-Z])/g, "$1 $2");
}

function checkpointStatusLabel(status: string | null | undefined) {
  const raw = String(status ?? "").trim().toLowerCase();
  if (!raw) return "sin intento";
  if (["ok", "success", "applied", "completed", "synced"].includes(raw)) return "completado";
  if (["failed", "error", "rejected"].includes(raw)) return "requiere atencion";
  if (["partial", "conflict"].includes(raw)) return "por revisar";
  if (["pending", "queued"].includes(raw)) return "pendiente";
  return "revisado";
}

export function CatalogPullPanel() {
  const [status, setStatus] = useState<CatalogStatus | null>(null);
  const [result, setResult] = useState<CatalogPullResult | null>(null);
  const [busyMode, setBusyMode] = useState<CatalogMode | "refresh" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadStatus() {
    setBusyMode((current) => current ?? "refresh");
    setError(null);
    try {
      const response = await requestJson<CatalogStatus>("/api/pos/sync/pull");
      setStatus(response.data);
    } catch (err) {
      setError(readError(err));
    } finally {
      setBusyMode((current) => current === "refresh" ? null : current);
    }
  }

  async function run(mode: CatalogMode, resetCheckpoint = false) {
    setBusyMode(mode);
    setError(null);
    try {
      const next = await plainJson<CatalogPullResult>("/api/pos/sync/pull", {
        method: "POST",
        body: JSON.stringify({ mode, resetCheckpoint, requestedBy: "tablet-sync-screen" })
      });
      setResult(next);
      const response = await requestJson<CatalogStatus>("/api/pos/sync/pull");
      setStatus(response.data);
    } catch (err) {
      setError(readError(err));
      try {
        const response = await requestJson<CatalogStatus>("/api/pos/sync/pull");
        setStatus(response.data);
      } catch {}
    } finally {
      setBusyMode(null);
    }
  }

  useEffect(() => {
    void loadStatus();
  }, []);

  const counts = useMemo(() => Object.entries(status?.tableCounts ?? {}), [status]);
  const tone = resultTone(result);
  const checkpoint = result?.checkpoint ?? status?.checkpoint ?? null;
  const disabled = Boolean(busyMode);

  return (
    <section className={styles.catalogPull}
      data-surface="tablet"
      data-screen="sync"
      data-zone="pos"
      data-panel="catalog-pull-panel"
      data-target="catalog-pull-panel-panel-188"
      data-kind="panel"
      data-role="revenue-core"
    >
      <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-div-1" data-kind="panel" data-role="container" className={styles.catalogHeader}>
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-div-2" data-kind="panel" data-role="container">
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-3" data-kind="panel" data-role="panel">PC a Tablet</span>
          <h2>Datos desde PC</h2>
          <p>Productos, precios, impuestos y opciones se actualizan desde PC cuando esta disponible. La venta local no depende de esta actualizacion.</p>
        </div>
        <div className={styles.catalogActions}
          data-surface="tablet"
          data-screen="sync"
          data-zone="pos"
          data-panel="catalog-pull-panel"
          data-target="catalog-pull-panel-button-195"
          data-kind="button"
          data-role="action"
        >
          <button type="button" onClick={() =
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-button-196"
            data-kind="button"
            data-role="action"
          > void run("delta", false)} disabled={disabled}>
            {busyMode === "delta" ? "Actualizando" : "Actualizar datos"}
          </button>
          <button type="button" onClick={() =
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-button-199"
            data-kind="button"
            data-role="action"
          > void run("bootstrap", true)} disabled={disabled}>
            {busyMode === "bootstrap" ? "Preparando" : "Primera carga"}
          </button>
          <button type="button" onClick={() =
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-button-202"
            data-kind="button"
            data-role="action"
          > void run("resync", true)} disabled={disabled}>
            {busyMode === "resync" ? "Reparando" : "Reparar datos"}
          </button>
          <button type="button" onClick={() =
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-button-205"
            data-kind="button"
            data-role="action"
          > void loadStatus()} disabled={disabled}>
            {busyMode === "refresh" ? "Actualizando" : "Actualizar"}
          </button>
        </div>
      </div>

      <div className={[styles.dispatchNote, styles[`dispatchNote_${tone}`]].join(" ")} role="status"
        data-surface="tablet"
        data-screen="sync"
        data-zone="pos"
        data-panel="catalog-pull-panel"
        data-target="catalog-pull-panel-badge-211"
        data-kind="badge"
        data-role="state-feedback"
      >{resultMessage(result)}</div>
      {error ? <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-div-4" data-kind="panel" data-role="container" className={styles.alert} role="alert">{error}</div> : null}

      <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-div-5" data-kind="panel" data-role="container" className={styles.catalogGrid}>
        <article
          data-surface="tablet"
          data-screen="sync"
          data-zone="pos"
          data-panel="catalog-pull-panel"
          data-target="catalog-pull-panel-panel-215"
          data-kind="panel"
          data-role="revenue-core"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-6" data-kind="panel" data-role="panel">Conexion PC</span>
          <strong>{status?.pc.enabled ? "configurada" : "apagada"}</strong>
          <small>{status?.pc.origin ?? "sin origen PC"}</small>
        </article>
        <article
          data-surface="tablet"
          data-screen="sync"
          data-zone="pos"
          data-panel="catalog-pull-panel"
          data-target="catalog-pull-panel-panel-220"
          data-kind="panel"
          data-role="revenue-core"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-7" data-kind="panel" data-role="panel">Avance</span>
          <strong>{checkpoint?.cursorValue ? "registrado" : "pendiente"}</strong>
          <small>{checkpoint?.cursorValue ? "Hay referencia de ultima actualizacion" : "Falta primera carga"}</small>
        </article>
        <article
          data-surface="tablet"
          data-screen="sync"
          data-zone="pos"
          data-panel="catalog-pull-panel"
          data-target="catalog-pull-panel-panel-225"
          data-kind="panel"
          data-role="revenue-core"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-8" data-kind="panel" data-role="panel">Ultimo exito</span>
          <strong>{checkpoint?.lastSuccessfulAt ? "cerrado" : "pendiente"}</strong>
          <small>{shortDate(checkpoint?.lastSuccessfulAt)}</small>
        </article>
        <article
          data-surface="tablet"
          data-screen="sync"
          data-zone="pos"
          data-panel="catalog-pull-panel"
          data-target="catalog-pull-panel-panel-230"
          data-kind="panel"
          data-role="revenue-core"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-9" data-kind="panel" data-role="panel">Ultimo intento</span>
          <strong>{checkpointStatusLabel(checkpoint?.status)}</strong>
          <small>{shortDate(checkpoint?.lastAttemptedAt)}</small>
        </article>
      </div>

      {result ? (
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-div-10" data-kind="panel" data-role="container" className={styles.catalogResultGrid}>
          <article
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-panel-239"
            data-kind="panel"
            data-role="revenue-core"
          ><span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-11" data-kind="panel" data-role="panel">Recibidos</span><strong>{result.counts.received}</strong></article>
          <article
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-panel-240"
            data-kind="panel"
            data-role="revenue-core"
          ><span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-12" data-kind="panel" data-role="panel">Aplicados</span><strong>{result.counts.applied}</strong></article>
          <article
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-panel-241"
            data-kind="panel"
            data-role="revenue-core"
          ><span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-13" data-kind="panel" data-role="panel">Duplicados</span><strong>{result.counts.duplicate}</strong></article>
          <article
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-panel-242"
            data-kind="panel"
            data-role="revenue-core"
          ><span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-14" data-kind="panel" data-role="panel">Conflictos</span><strong>{result.counts.conflict}</strong></article>
          <article
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-panel-243"
            data-kind="panel"
            data-role="revenue-core"
          ><span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-15" data-kind="panel" data-role="panel">Rechazados</span><strong>{result.counts.rejected}</strong></article>
        </div>
      ) : null}

      <div className={styles.catalogEntityList}
        data-surface="tablet"
        data-screen="sync"
        data-zone="pos"
        data-panel="catalog-pull-panel"
        data-target="catalog-pull-panel-panel-247"
        data-kind="panel"
        data-role="revenue-core"
      >
        {counts.map(([entity, count]) => (
          <span key={entity}
            data-surface="tablet"
            data-screen="sync"
            data-zone="pos"
            data-panel="catalog-pull-panel"
            data-target="catalog-pull-panel-panel-249"
            data-kind="panel"
            data-role="revenue-core"
          >{entityLabel(entity)}: {count}</span>
        ))}
      </div>

      {result?.findings.length ? (
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-div-16" data-kind="panel" data-role="container" className={styles.catalogFindings}>
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-span-17" data-kind="panel" data-role="panel">{result.findings.length} dato(s) requieren revision de soporte.</span>
        </div>
      ) : null}

      <details className={styles.supportDetails}>
        <summary>Detalles de soporte</summary>
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="catalog_pull_panel" data-target="catalog-pull-panel-div-18" data-kind="panel" data-role="container" className={styles.diagnostics}>
          <span>Modo tecnico: {result?.mode ?? "sin ejecucion"}</span>
          <span>Referencia anterior: {result?.cursorBefore ?? checkpoint?.cursorValue ?? "sin registro"}</span>
          <span>Referencia nueva: {result?.cursorAfter ?? "sin cambio"}</span>
          <span>Stream: {status?.stream ?? "catalogo"}</span>
          {result?.findings.slice(0, 6).map((finding, index) => (
            <span key={`${finding.code}-${finding.entityId ?? index}`}>{finding.code}: {finding.entityType ?? "payload"} {finding.entityId ?? ""}</span>
          ))}
        </div>
      </details>
    </section>
  );
}
