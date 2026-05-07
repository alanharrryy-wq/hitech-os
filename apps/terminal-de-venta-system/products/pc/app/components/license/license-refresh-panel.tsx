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
    ? "Actualización remota disponible si el servidor de licencias está configurado."
    : "Actualización remota deshabilitada por configuración local.";

  return (
    <section className="card">
      <div className="kicker">actualización remota</div>
      <h2 className="section-title">Actualización de licencia</h2>
      <p className="section-copy">{message}</p>

      <div className="dashboard-actions">
        <Metric label="Estado" value={initialStatus.state} />
        <Metric label="Habilitado" value={initialStatus.enabled ? "sí" : "no"} />
        <Metric label="Último intento" value={initialStatus.lastRefreshAt ?? "nunca"} />
        <Metric label="Último éxito" value={initialStatus.lastSuccessAt ?? "nunca"} />
        <Metric label="Último fallo" value={initialStatus.lastFailureAt ?? "nunca"} />
        <Metric label="Plan" value={initialStatus.plan ?? "n/a"} />
      </div>

      {initialStatus.lastError ? (
        <div className="alert-strip">Error: {initialStatus.lastError}</div>
      ) : null}

      <form action="/api/license/refresh" method="post" className="dashboard-actions">
        <button type="submit">
          Actualizar licencia
        </button>
      </form>

      <p className="section-copy">
        La actualización remota es opcional. Si no hay servidor configurado, la licencia local firmada sigue siendo la fuente de operación.
      </p>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="action-card">
      <strong>{label}</strong>
      <span className="subtle">{value}</span>
    </div>
  );
}
