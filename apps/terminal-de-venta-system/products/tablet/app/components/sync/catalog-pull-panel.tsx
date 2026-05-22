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
  if (!result) return "Sin pull de catalogo en esta sesion.";
  if (result.ok && result.reason === "applied") return `Catalogo aplicado: ${result.counts.applied} cambio(s), ${result.counts.duplicate} duplicado(s).`;
  if (result.ok && result.reason === "empty") return "PC respondio correctamente; no habia cambios nuevos para aplicar.";
  if (result.reason === "pc_sync_disabled") return "Pull PC apagado por configuracion. La Tablet sigue vendiendo local.";
  if (result.reason === "pc_unavailable") return "PC no respondio al export de catalogo. El POS local no se bloquea.";
  if (result.reason === "partial") return `Pull parcial: ${result.counts.applied} aplicado(s), ${result.counts.conflict} conflicto(s), ${result.counts.rejected} rechazado(s).`;
  if (result.reason === "invalid_payload") return "PC envio payload invalido; checkpoint exitoso no se avanzo.";
  return `Resultado catalogo: ${result.reason}.`;
}

function shortDate(value: string | null | undefined) {
  if (!value) return "sin registro";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "sin registro";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
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
    <section className={styles.catalogPull}>
      <div className={styles.catalogHeader}>
        <div>
          <span>PC a Tablet</span>
          <h2>Catalogo entrante</h2>
          <p>Master-data, precios, impuestos y opciones se jalan desde PC con cursor local. La venta local no depende de este pull.</p>
        </div>
        <div className={styles.catalogActions}>
          <button type="button" onClick={() => void run("delta", false)} disabled={disabled}>
            {busyMode === "delta" ? "Jalando" : "Pedir delta"}
          </button>
          <button type="button" onClick={() => void run("bootstrap", true)} disabled={disabled}>
            {busyMode === "bootstrap" ? "Aplicando" : "Bootstrap inicial"}
          </button>
          <button type="button" onClick={() => void run("resync", true)} disabled={disabled}>
            {busyMode === "resync" ? "Rearmando" : "Resync controlado"}
          </button>
          <button type="button" onClick={() => void loadStatus()} disabled={disabled}>
            {busyMode === "refresh" ? "Actualizando" : "Actualizar"}
          </button>
        </div>
      </div>

      <div className={[styles.dispatchNote, styles[`dispatchNote_${tone}`]].join(" ")} role="status">{resultMessage(result)}</div>
      {error ? <div className={styles.alert} role="alert">{error}</div> : null}

      <div className={styles.catalogGrid}>
        <article>
          <span>Conexion PC</span>
          <strong>{status?.pc.enabled ? "configurada" : "apagada"}</strong>
          <small>{status?.pc.origin ?? "sin origen PC"}</small>
        </article>
        <article>
          <span>Cursor</span>
          <strong>{checkpoint?.cursorValue ? "activo" : "sin cursor"}</strong>
          <small>{checkpoint?.cursorValue ?? "bootstrap pendiente"}</small>
        </article>
        <article>
          <span>Ultimo exito</span>
          <strong>{checkpoint?.lastSuccessfulAt ? "cerrado" : "pendiente"}</strong>
          <small>{shortDate(checkpoint?.lastSuccessfulAt)}</small>
        </article>
        <article>
          <span>Ultimo intento</span>
          <strong>{checkpoint?.status ?? "sin intento"}</strong>
          <small>{shortDate(checkpoint?.lastAttemptedAt)}</small>
        </article>
      </div>

      {result ? (
        <div className={styles.catalogResultGrid}>
          <article><span>Recibidos</span><strong>{result.counts.received}</strong></article>
          <article><span>Aplicados</span><strong>{result.counts.applied}</strong></article>
          <article><span>Duplicados</span><strong>{result.counts.duplicate}</strong></article>
          <article><span>Conflictos</span><strong>{result.counts.conflict}</strong></article>
          <article><span>Rechazados</span><strong>{result.counts.rejected}</strong></article>
        </div>
      ) : null}

      <div className={styles.catalogEntityList}>
        {counts.map(([entity, count]) => (
          <span key={entity}>{entity}: {count}</span>
        ))}
      </div>

      {result?.findings.length ? (
        <div className={styles.catalogFindings}>
          {result.findings.slice(0, 6).map((finding, index) => (
            <span key={`${finding.code}-${finding.entityId ?? index}`}>{finding.code}: {finding.entityType ?? "payload"} {finding.entityId ?? ""}</span>
          ))}
        </div>
      ) : null}
    </section>
  );
}
