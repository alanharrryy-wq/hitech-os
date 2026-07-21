"use client";

import { useMemo, useState } from "react";

type ApiState = {
  ok: boolean;
  status?: string;
  message?: string;
  bridge?: { stdout?: string; stderr?: string; code?: number | null };
  statusRefresh?: { stdout?: string; stderr?: string; code?: number | null } | null;
};

export function TriDbSyncAction() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ApiState | null>(null);

  const tone = useMemo(() => {
    if (!result) return "idle";
    return result.ok ? "ready" : "blocked";
  }, [result]);

  async function runSync() {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch("/api/sync/tri-db/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      const data = (await response.json()) as ApiState;
      setResult(data);
      if (data.ok) {
        window.setTimeout(() => window.location.reload(), 900);
      }
    } catch (error: any) {
      setResult({ ok: false, status: "BLOCKED", message: error?.message ?? String(error) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <section style={{ marginBottom: 18, padding: 16 }}>
      <div style={{ alignItems: "center", display: "grid", gap: 14, gridTemplateColumns: "minmax(0,1fr) auto" }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 12, fontWeight: 950, letterSpacing: ".14em", textTransform: "uppercase" }}>Accion manual</div>
          <h2 style={{ fontSize: "clamp(1.2rem, 4vw, 1.75rem)", letterSpacing: 0, margin: "6px 0 4px" }}>Ejecutar bridge de rescate</h2>
          <p style={{ lineHeight: 1.45, margin: 0 }}>Proyecta datos por TRI-DB solo para rescate/backfill/diagnostico. El camino primario es OutboxEvent, ingest PC y projectors Prisma. Tablet puede seguir operando si esta accion falla.</p>
        </div>
        <button
          type="button"
          onClick={runSync}
          disabled={loading}
          style={{ cursor: loading ? "wait" : "pointer", fontWeight: 900, minHeight: 44, minWidth: 172, padding: "12px 16px" }}
        >
          {loading ? "Ejecutando..." : "Ejecutar bridge"}
        </button>
      </div>

      {result ? (
        <div data-status-tone={tone} style={{ marginTop: 14, padding: 14 }}>
          <strong>{result.ok ? "Bridge secundario listo" : "Bridge secundario bloqueado"}</strong>
          <p style={{ lineHeight: 1.45, margin: "6px 0 0" }}>{result.message ?? "Sin mensaje del servidor."}</p>
          {result.bridge?.stderr || result.statusRefresh?.stderr ? (
            <details style={{ marginTop: 10 }}>
              <summary style={{ cursor: "pointer", fontWeight: 850 }}>Detalles tecnicos</summary>
              {result.bridge?.stderr ? <pre style={{ marginTop: 10, maxHeight: 180, overflow: "auto", padding: 12, whiteSpace: "pre-wrap" }}>{result.bridge.stderr}</pre> : null}
              {result.statusRefresh?.stderr ? <pre style={{ marginTop: 10, maxHeight: 180, overflow: "auto", padding: 12, whiteSpace: "pre-wrap" }}>{result.statusRefresh.stderr}</pre> : null}
            </details>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
