import type { FeatureResolution, NormalizedLicenseStatus } from "../../../../../shared/licensing";
import type { RuntimeContext } from "../../../../../shared/runtime";
import styles from "./license-ui.module.css";

type Tone = "ok" | "warn" | "danger" | "neutral";

function toneForState(state: string): Tone {
  if (state === "active" || state === "development") return "ok";
  if (state === "offline_grace") return "warn";
  return "danger";
}

function stateLabel(state: string) {
  const labels: Record<string, string> = {
    active: "Licencia activa",
    development: "Modo desarrollo",
    offline_grace: "Operando con gracia offline",
    missing: "Licencia pendiente",
    invalid: "Licencia inválida",
    expired: "Licencia vencida",
    suspended: "Licencia suspendida",
    revoked: "Licencia revocada"
  };
  return labels[state] ?? "Estado por revisar";
}

function assignmentLabel(state: string) {
  const labels: Record<string, string> = {
    assigned: "Equipo asignado",
    unassigned: "Equipo pendiente de asignar",
    wrong_business: "Negocio no coincide",
    wrong_store: "Sucursal no coincide",
    wrong_device: "Dispositivo no coincide",
    wrong_terminal: "Terminal no coincide",
    exceeded_limit: "Límite de terminales excedido",
    unknown: "Asignación no declarada"
  };
  return labels[state] ?? "Asignación por revisar";
}

function decisionLabel(decision: string) {
  const labels: Record<string, string> = {
    allow: "Operación permitida",
    allow_with_warning: "Operación permitida con aviso",
    degrade: "Operación limitada",
    deny: "Operación bloqueada"
  };
  return labels[decision] ?? "Decisión por revisar";
}

function runtimeModeLabel(mode: RuntimeContext["runtimeMode"]) {
  const labels: Record<RuntimeContext["runtimeMode"], string> = {
    dev: "Desarrollo",
    customer: "Cliente",
    test: "Prueba",
    release: "Release"
  };
  return labels[mode];
}

function visibleValue(value: string | null | undefined, fallback: string) {
  return value && value.trim() ? value : fallback;
}

function supportAction(status: NormalizedLicenseStatus, context: RuntimeContext) {
  if (status.state === "active" || status.state === "development") {
    return {
      title: "No requiere acción",
      copy: "La Tablet tiene autorización local suficiente para operar según el plan instalado."
    };
  }
  if (status.state === "offline_grace") {
    return {
      title: "Operación local protegida",
      copy: "La Tablet puede seguir trabajando de forma limitada. El administrador debe revisar la licencia cuando termine la venta o el turno."
    };
  }
  if (status.state === "missing" && context.runtimeMode === "customer") {
    return {
      title: "Instalación pendiente de licencia local",
      copy: "Instalación pendiente de licencia local. La Tablet conserva venta básica en modo limitado mientras el administrador completa la activación."
    };
  }
  if (context.runtimeMode === "dev") {
    return {
      title: "Entorno de desarrollo",
      copy: "Esta Tablet está en modo desarrollo. La licencia real debe instalarse antes de entregar el equipo a cliente."
    };
  }
  return {
    title: "Avisar al administrador",
    copy: "La activación, importación, renovación y revisión de licencias se hacen fuera de esta Tablet. Esta pantalla sólo informa el estado actual."
  };
}

function issueCopy(status: NormalizedLicenseStatus) {
  const reason = status.denialReason;
  const labels: Record<string, string> = {
    license_missing: "Falta instalar una licencia local válida.",
    license_invalid: "La licencia instalada no se pudo validar.",
    license_expired: "La vigencia de la licencia terminó.",
    license_suspended: "La licencia está suspendida.",
    license_revoked: "La licencia fue revocada.",
    device_unassigned: "Este equipo no está asignado en la licencia.",
    wrong_business: "La licencia pertenece a otro negocio.",
    wrong_store: "La licencia pertenece a otra sucursal.",
    wrong_device: "La licencia pertenece a otro dispositivo.",
    wrong_terminal: "La licencia pertenece a otra terminal.",
    exceeded_limit: "Se excedió el límite de terminales permitidas.",
    feature_not_entitled: "El plan no incluye una función solicitada."
  };
  if (reason && labels[reason]) return labels[reason];
  if (status.state === "active" || status.state === "development") return "No se detectaron bloqueos principales.";
  if (status.state === "offline_grace") return "La Tablet conserva continuidad local con restricciones.";
  return "La licencia requiere revisión administrativa.";
}

function categoryForFeature(key: string) {
  const raw = key.toLowerCase();
  if (raw.includes("sale") || raw.includes("pos") || raw.includes("ticket") || raw.includes("checkout")) return "Ventas";
  if (raw.includes("cash") || raw.includes("shift") || raw.includes("session") || raw.includes("corte")) return "Turno y caja";
  if (raw.includes("stock") || raw.includes("inventory") || raw.includes("catalog") || raw.includes("product")) return "Inventario local";
  if (raw.includes("sync") || raw.includes("outbox") || raw.includes("export") || raw.includes("evidence")) return "Sincronización y evidencia";
  if (raw.includes("report") || raw.includes("audit") || raw.includes("history")) return "Reportes";
  return "Otras funciones";
}

function featureLabel(key: string) {
  const raw = key.replace(/[._:-]+/g, " ").trim();
  return raw ? raw.replace(/\b\w/g, (ch) => ch.toUpperCase()) : "Función";
}

export function LicenseStatusCard({ status, runtimeContext }: { status: NormalizedLicenseStatus; runtimeContext: RuntimeContext }) {
  const tone = toneForState(status.state);
  const action = supportAction(status, runtimeContext);
  const headline = tone === "ok" ? "Tablet lista para operar" : tone === "warn" ? "Tablet operando con aviso" : "Licencia requiere atención";

  return (
    <section className={styles.statusCluster} id="license-status" data-prisma-license-state={status.state} data-prisma-client-license-view="readonly">
      <div className={styles.heroCard}>
        <div className={`${styles.statusMark} ${styles[tone]}`} aria-hidden="true">✓</div>
        <div className={styles.heroBody}>
          <div className={styles.heroHeader}>
            <div className={styles.heroCopyBlock}>
              <p className={styles.eyebrow}>Estado del equipo</p>
              <h1 className={styles.title}>{headline}</h1>
              <p className={styles.copy}>{stateLabel(status.state)}. {issueCopy(status)}</p>
            </div>
            <span className={`${styles.statusBadge} ${styles[tone]}`}>{decisionLabel(status.operationalDecision)}</span>
          </div>

          <div className={styles.operatorNotice}>
            <strong>{action.title}</strong>
            <span>{action.copy}</span>
          </div>
        </div>
      </div>

      <div className={styles.identityStrip} aria-label="Resumen de licencia y equipo">
        <Metric label="Estado" value={stateLabel(status.state)} tone={tone} />
        <Metric label="Plan" value={visibleValue(status.plan, "Sin plan instalado")} />
        <Metric label="Asignación" value={assignmentLabel(status.assignmentState)} />
        <Metric label="Terminal" value={visibleValue(status.terminalId ?? runtimeContext.terminalId, "No declarada")} />
        <Metric label="Sucursal" value={visibleValue(status.storeId ?? status.branchId ?? runtimeContext.storeId, "No declarada")} />
        <Metric label="Vigencia" value={status.daysRemaining === null ? visibleValue(status.validUntil, "No disponible") : `${status.daysRemaining} días restantes`} />
      </div>

      {status.warnings.length > 0 ? (
        <div className={styles.warningStack} aria-label="Avisos de licencia">
          {status.warnings.map((warning) => (
            <div key={warning.code} className={styles.warning}>
              <strong>Revisión recomendada</strong>
              <span>{warning.message || warning.code}</span>
            </div>
          ))}
        </div>
      ) : null}

      <details className={styles.evidenceDisclosure}>
        <summary>Ver detalle para soporte</summary>
        <div className={styles.compactMetricGrid}>
          <Metric label="Modo runtime" value={runtimeModeLabel(runtimeContext.runtimeMode)} />
          <Metric label="Origen config" value={visibleValue(runtimeContext.configPath, "Config por defecto o no declarada")} />
          <Metric label="Archivo licencia" value={visibleValue(status.path ?? runtimeContext.licenseFile ?? runtimeContext.paths.licenseFile, "No declarado")} />
          <Metric label="Negocio" value={visibleValue(status.businessId ?? runtimeContext.businessId, "No declarado")} />
          <Metric label="Dispositivo" value={visibleValue(status.deviceId ?? status.tabletId ?? runtimeContext.deviceId, "No declarado")} />
          <Metric label="Fuente" value={status.source} />
          <Metric label="Cliente" value={visibleValue(status.customerId, "No declarado")} />
          <Metric label="Motivo" value={status.denialReason ? issueCopy(status) : "Sin bloqueo principal"} />
        </div>
      </details>
    </section>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: Tone }) {
  return (
    <div className={styles.metric}>
      <div className={styles.metricLabel}>{label}</div>
      <div className={`${styles.metricValue} ${tone ? styles[tone] : ""}`}>{value}</div>
    </div>
  );
}

export function FeatureList({ features }: { features: FeatureResolution[] }) {
  const byCategory = features.reduce<Record<string, FeatureResolution[]>>((acc, feature) => {
    const category = categoryForFeature(feature.key);
    acc[category] = acc[category] || [];
    acc[category].push(feature);
    return acc;
  }, {});
  const categories = Object.entries(byCategory);
  const allowed = features.filter((feature) => feature.allowed).length;
  const blocked = Math.max(features.length - allowed, 0);

  return (
    <section className={`${styles.card} ${styles.featurePanel}`} id="license-features">
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Funciones disponibles</p>
          <h2 className={styles.sectionTitle}>Permisos de operación</h2>
        </div>
        <span className={styles.readonlyPill}>Sólo lectura</span>
      </div>
      <p className={styles.copy}>Resumen de lo que esta Tablet puede usar con la licencia local instalada. No administra licencias desde aquí.</p>

      <div className={styles.summaryStrip}>
        <span className={styles.summaryTile}><strong>{allowed}</strong><small>permitidas</small></span>
        <span className={styles.summaryTile}><strong>{blocked}</strong><small>bloqueadas o limitadas</small></span>
        <span className={styles.summaryTile}><strong>{features.length}</strong><small>revisadas</small></span>
      </div>

      <div className={styles.featureGroups}>
        {categories.map(([category, group]) => {
          const groupAllowed = group.filter((feature) => feature.allowed).length;
          return (
            <details key={category} className={styles.featureGroup}>
              <summary>
                <span>{category}</span>
                <em>{groupAllowed}/{group.length} permitidas</em>
              </summary>
              <div className={styles.featureList}>
                {group.map((feature) => (
                  <div key={feature.key} className={styles.featureItem}>
                    <div>
                      <strong>{featureLabel(feature.key)}</strong>
                      <span>{feature.reason || "Revisado por la licencia local."}</span>
                    </div>
                    <span className={`${styles.featurePill} ${feature.allowed ? styles.ok : styles.danger}`}>{feature.allowed ? "Permitida" : "No disponible"}</span>
                  </div>
                ))}
              </div>
            </details>
          );
        })}
      </div>
    </section>
  );
}
