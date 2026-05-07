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
    <section style={{ marginBottom: 18, borderRadius: 24, border: "1px solid rgba(125,211,252,.22)", background: "rgba(15,23,42,.72)", padding: 18, color: "#e2e8f0" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center" }}>
        <div>
          <div style={{ color: "#7dd3fc", fontSize: 12, fontWeight: 900, letterSpacing: ".14em", textTransform: "uppercase" }}>accion manual</div>
          <h2 style={{ margin: "6px 0 4px", color: "#f8fafc" }}>Sincronizar ahora</h2>
          <p style={{ margin: 0, color: "#cbd5e1" }}>Ejecuta bridge Tablet → PC y refresca el status compartido. Un boton, no ceremonia de PowerShell con incienso.</p>
        </div>
        <button
          type="button"
          onClick={runSync}
          disabled={loading}
          style={{ border: 0, borderRadius: 16, padding: "14px 18px", fontWeight: 900, cursor: loading ? "wait" : "pointer", color: "#082f49", background: loading ? "#94a3b8" : "#7dd3fc", minWidth: 180 }}
        >
          {loading ? "Sincronizando..." : "Sincronizar ahora"}
        </button>
      </div>

      {result ? (
        <div style={{ marginTop: 14, borderRadius: 18, padding: 14, background: tone === "ready" ? "rgba(20,83,45,.42)" : "rgba(127,29,29,.42)", border: "1px solid rgba(226,232,240,.18)" }}>
          <strong>{result.ok ? "READY" : "BLOCKED"}</strong>
          <p style={{ margin: "6px 0 0", color: "#e2e8f0" }}>{result.message ?? "Sin mensaje del servidor."}</p>
          {result.bridge?.stderr ? <pre style={{ whiteSpace: "pre-wrap", overflow: "auto", maxHeight: 180 }}>{result.bridge.stderr}</pre> : null}
          {result.statusRefresh?.stderr ? <pre style={{ whiteSpace: "pre-wrap", overflow: "auto", maxHeight: 180 }}>{result.statusRefresh.stderr}</pre> : null}
        </div>
      ) : null}
    </section>
  );
}
