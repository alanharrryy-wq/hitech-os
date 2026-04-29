type RefreshStatus = {
  state: string;
  enabled: boolean;
  lastRefreshAt: string | null;
  lastSuccessAt: string | null;
  lastFailureAt: string | null;
  lastError: string | null;
  licenseId: string | null;
  plan: string | null;
};

export function LicenseRefreshPanel({ initialStatus }: { initialStatus: RefreshStatus }) {
  const message = initialStatus.enabled
    ? "Refresh remoto disponible si el servidor de licencias está configurado."
    : "Refresh remoto deshabilitado por configuración local.";

  return (
    <section style={{ border: "1px solid rgba(127,179,213,0.35)", borderRadius: 18, padding: 20, background: "rgba(15,23,42,0.82)", color: "#e5e7eb" }}>
      <p style={{ margin: 0, color: "#7fb3d5", textTransform: "uppercase", letterSpacing: "0.12em", fontSize: 12, fontWeight: 800 }}>Refresh remoto</p>
      <h2 style={{ margin: "8px 0 4px" }}>Actualización de licencia</h2>
      <p style={{ margin: 0, color: "#aeb6c1" }}>{message}</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: 12, marginTop: 18 }}>
        <Metric label="Estado" value={initialStatus.state} />
        <Metric label="Habilitado" value={initialStatus.enabled ? "sí" : "no"} />
        <Metric label="Último intento" value={initialStatus.lastRefreshAt ?? "nunca"} />
        <Metric label="Último éxito" value={initialStatus.lastSuccessAt ?? "nunca"} />
        <Metric label="Último fallo" value={initialStatus.lastFailureAt ?? "nunca"} />
        <Metric label="Plan" value={initialStatus.plan ?? "n/a"} />
      </div>

      {initialStatus.lastError ? (
        <div style={{ marginTop: 12, color: "#fecaca" }}>Error: {initialStatus.lastError}</div>
      ) : null}

      <form action="/api/license/refresh" method="post" style={{ marginTop: 16 }}>
        <button type="submit" style={{ border: "1px solid rgba(214,189,134,0.45)", borderRadius: 12, padding: "10px 14px", color: "#f4e4bd", background: "rgba(23,21,17,0.88)", cursor: "pointer", fontWeight: 800 }}>
          Actualizar licencia
        </button>
      </form>

      <p style={{ marginTop: 10, marginBottom: 0, color: "#94a3b8", fontSize: 12 }}>
        El refresh remoto es opcional. Si no hay servidor configurado, la licencia local firmada sigue siendo la fuente de operación.
      </p>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ border: "1px solid rgba(148,163,184,0.22)", borderRadius: 14, padding: 12, background: "rgba(2,6,23,0.45)" }}>
      <div style={{ color: "#94a3b8", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 800 }}>{label}</div>
      <div style={{ marginTop: 5, fontFamily: "monospace", overflowWrap: "anywhere", color: "#f8fafc" }}>{value}</div>
    </div>
  );
}
