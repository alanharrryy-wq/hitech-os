import styles from "./license-ui.module.css";

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
    <section className={styles.card}>
      <p className={styles.eyebrow}>Refresh remoto</p>
      <h2 className={styles.title}>Actualización de licencia</h2>
      <p className={styles.copy}>{message}</p>

      <div className={styles.metricGrid}>
        <Metric label="Estado" value={initialStatus.state} />
        <Metric label="Habilitado" value={initialStatus.enabled ? "sí" : "no"} />
        <Metric label="Último intento" value={initialStatus.lastRefreshAt ?? "nunca"} />
        <Metric label="Último éxito" value={initialStatus.lastSuccessAt ?? "nunca"} />
        <Metric label="Último fallo" value={initialStatus.lastFailureAt ?? "nunca"} />
        <Metric label="Plan" value={initialStatus.plan ?? "n/a"} />
      </div>

      {initialStatus.lastError ? (
        <div className={styles.warning}>Error: {initialStatus.lastError}</div>
      ) : null}

      <form action="/api/license/refresh" method="post" className={styles.refreshForm}>
        <button type="submit" className={styles.primaryButton}>
          Actualizar licencia
        </button>
      </form>

      <p className={styles.helper}>
        El refresh remoto es opcional. Si no hay servidor configurado, la licencia local firmada sigue siendo la fuente de operación.
      </p>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.metric}>
      <div className={styles.metricLabel}>{label}</div>
      <div className={styles.metricValue}>{value}</div>
    </div>
  );
}
