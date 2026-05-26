import styles from "./license-ui.module.css";

type RefreshStatus = {
  state: string;
  enabled: boolean;
  configurationState?: string;
  operationalDecision?: string;
  lastRefreshAt: string | null;
  lastSuccessAt: string | null;
  lastFailureAt: string | null;
  lastError: string | null;
  licenseId: string | null;
  plan: string | null;
};

function refreshStateLabel(state: string) {
  const labels: Record<string, string> = {
    refresh_disabled: "Refresh remoto no configurado",
    missing_server_url: "Servidor remoto no configurado",
    missing_device_id: "Device ID no configurado",
    configured: "Configurado",
    disabled: "Refresh remoto no configurado",
    never_refreshed: "Sin refresh remoto todavía",
    fresh: "Refresh remoto vigente",
    stale: "Refresh remoto pendiente",
    refresh_failed: "Refresh remoto falló",
    offline_grace: "Gracia offline activa",
    revoked: "Licencia revocada",
    suspended: "Licencia suspendida"
  };
  return labels[state] ?? "Refresh requiere revisión";
}

function visibleValue(value: string | null | undefined, fallback: string) {
  return value && value.trim() ? value : fallback;
}

export function LicenseRefreshPanel({ initialStatus }: { initialStatus: RefreshStatus }) {
  const message = initialStatus.enabled
    ? "Refresh remoto disponible si el servidor de licencias está configurado."
    : "Refresh remoto no configurado. La operación local continúa si la licencia local es válida.";
  const lastErrorMessage = initialStatus.lastError
    ? "No se pudo refrescar licencia remota. Se conserva política local vigente."
    : null;

  return (
    <section className={styles.card} id="license-refresh">
      <p className={styles.eyebrow}>Refresh remoto</p>
      <h2 className={styles.title}>Actualización de licencia</h2>
      <p className={styles.copy}>{message}</p>

      <div className={styles.metricGrid}>
        <Metric label="Estado" value={refreshStateLabel(initialStatus.state)} />
        <Metric label="Habilitado" value={initialStatus.enabled ? "sí" : "no"} />
        <Metric label="Configuración" value={refreshStateLabel(initialStatus.configurationState ?? initialStatus.state)} />
        <Metric label="Último intento" value={initialStatus.lastRefreshAt ?? "nunca"} />
        <Metric label="Último éxito" value={initialStatus.lastSuccessAt ?? "nunca"} />
        <Metric label="Último fallo" value={initialStatus.lastFailureAt ?? "nunca"} />
        <Metric label="Plan" value={visibleValue(initialStatus.plan, "Sin licencia local")} />
      </div>

      {lastErrorMessage ? (
        <div className={styles.warning}>{lastErrorMessage} Detalle: {initialStatus.lastError}</div>
      ) : null}

      {initialStatus.enabled ? (
        <form action="/api/license/refresh" method="post" className={styles.refreshForm}>
          <button type="submit" className={styles.primaryButton}>
            Actualizar licencia
          </button>
        </form>
      ) : (
        <div className={styles.refreshActions} data-prisma-refresh-state="disabled">
          <a className={styles.primaryLink} href="mailto:contacto@hitechrts.com?subject=Soporte%20licencia%20PRISMA%20Tablet">Request support</a>
          <a className={styles.secondaryLink} href="#license-status">View license status</a>
          <a className={styles.secondaryLink} href="https://wa.me/525629563031">View support contact</a>
          <button className={styles.disabledButton} type="button" disabled>
            Update license
          </button>
        </div>
      )}

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
