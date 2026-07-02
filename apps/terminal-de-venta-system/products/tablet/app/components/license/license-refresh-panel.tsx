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
    refresh_disabled: "Actualización no configurada",
    missing_server_url: "Servidor no configurado",
    missing_device_id: "Equipo sin identificador",
    configured: "Configurada",
    disabled: "Desactivada",
    never_refreshed: "Sin actualización remota",
    fresh: "Actualizada",
    stale: "Pendiente de revisión",
    refresh_failed: "Actualización fallida",
    offline_grace: "Continuidad offline activa",
    revoked: "Licencia revocada",
    suspended: "Licencia suspendida"
  };
  return labels[state] ?? "Requiere revisión";
}

function visibleValue(value: string | null | undefined, fallback: string) {
  return value && value.trim() ? value : fallback;
}

export function LicenseRefreshPanel({ initialStatus }: { initialStatus: RefreshStatus }) {
  const hasError = Boolean(initialStatus.lastError);
  const headline = initialStatus.enabled ? "Actualización automática disponible" : "Licencia local primero";
  const copy = initialStatus.enabled
    ? "El sistema puede recibir actualización remota si el entorno administrativo lo tiene configurado. Esta Tablet no dispara cambios manuales de licencia."
    : "La Tablet sólo muestra el estado instalado. Activar, importar o corregir licencias corresponde al administrador, fuera del equipo del cliente.";

  return (
    <section className={`${styles.card} ${styles.refreshPanel}`} id="license-refresh" data-prisma-license-refresh-view="readonly">
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Actualización</p>
          <h2 className={styles.sectionTitle}>{headline}</h2>
        </div>
        <span className={styles.readonlyPill}>Sin acciones</span>
      </div>
      <p className={styles.copy}>{copy}</p>

      <div className={styles.compactMetricGrid}>
        <Metric label="Estado" value={refreshStateLabel(initialStatus.state)} />
        <Metric label="Modo" value={initialStatus.enabled ? "Automático si está configurado" : "Local"} />
        <Metric label="Configuración" value={refreshStateLabel(initialStatus.configurationState ?? initialStatus.state)} />
        <Metric label="Último intento" value={initialStatus.lastRefreshAt ?? "Nunca"} />
        <Metric label="Último éxito" value={initialStatus.lastSuccessAt ?? "Nunca"} />
        <Metric label="Plan detectado" value={visibleValue(initialStatus.plan, "Sin licencia local")} />
      </div>

      {hasError ? (
        <div className={styles.warning}>
          <strong>Última actualización no completada</strong>
          <span>Se conserva la política local vigente. El administrador puede revisar el detalle de soporte fuera de esta Tablet.</span>
        </div>
      ) : null}

      <p className={styles.helper}>Esta vista no contiene botones de activación, importación, renovación ni administración.</p>
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
