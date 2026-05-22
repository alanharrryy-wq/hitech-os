import type { FeatureResolution, NormalizedLicenseStatus } from "../../../../../shared/licensing";
import type { RuntimeContext } from "../../../../../shared/runtime";
import styles from "./license-ui.module.css";

function toneForState(state: string) {
  if (state === "active" || state === "development") return "ok" as const;
  if (state === "offline_grace") return "warn" as const;
  return "danger" as const;
}

function stateLabel(state: string) {
  const labels: Record<string, string> = {
    active: "Licencia local activa",
    development: "Modo desarrollo",
    offline_grace: "Licencia en gracia offline",
    missing: "Licencia no configurada",
    invalid: "Licencia inválida",
    expired: "Licencia vencida",
    suspended: "Licencia suspendida",
    revoked: "Licencia revocada"
  };
  return labels[state] ?? "Estado de licencia requiere revisión";
}

function assignmentLabel(state: string) {
  const labels: Record<string, string> = {
    assigned: "Equipo asignado",
    unassigned: "Equipo no asignado",
    wrong_business: "Negocio incorrecto",
    wrong_store: "Tienda incorrecta",
    wrong_device: "Dispositivo incorrecto",
    wrong_terminal: "Terminal incorrecta",
    exceeded_limit: "Límite de terminales excedido",
    unknown: "Asignación no declarada"
  };
  return labels[state] ?? "Asignación requiere revisión";
}

function decisionLabel(decision: string) {
  const labels: Record<string, string> = {
    allow: "Operación permitida",
    allow_with_warning: "Operación permitida con aviso",
    degrade: "Continuidad local limitada",
    deny: "Operación bloqueada"
  };
  return labels[decision] ?? "Decisión requiere revisión";
}

function denialReasonLabel(reason: string) {
  const labels: Record<string, string> = {
    license_missing: "Licencia no configurada. Revisa instalación local.",
    license_invalid: "Licencia inválida o alterada. Revisa diagnóstico.",
    license_expired: "Licencia vencida. Requiere renovación.",
    license_suspended: "Licencia suspendida. Revisa soporte del cliente.",
    license_revoked: "Licencia revocada. Revisa soporte y evidencia de activación.",
    device_unassigned: "Equipo no asignado a esta licencia. Revisa cliente, negocio y terminal.",
    wrong_business: "Licencia asignada a otro negocio. Revisa activación.",
    wrong_store: "Licencia asignada a otra tienda o sucursal. Revisa activación.",
    wrong_device: "Licencia asignada a otro dispositivo. Revisa activación.",
    wrong_terminal: "Licencia asignada a otra terminal. Revisa activación.",
    exceeded_limit: "Límite de terminales excedido. Revisa licencia del cliente.",
    feature_not_entitled: "La función no está incluida en el plan actual."
  };
  return labels[reason] ?? "Licencia requiere revisión operativa.";
}

function visibleValue(value: string | null | undefined, fallback: string) {
  return value && value.trim() ? value : fallback;
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

function provenanceLabel(context: RuntimeContext) {
  const source = context.provenance.runtimeConfig?.source;
  if (source === "explicit" || source === "env") return "Runtime config explícito";
  if (source === "programdata") return "ProgramData canonical";
  if (source === "legacy_programdata") return "ProgramData legacy";
  if (source === "dev_fallback") return "Fallback dev";
  return "Sin runtime.json";
}

function signatureLabel(status: NormalizedLicenseStatus) {
  if (status.state === "missing") return "No disponible";
  if (status.state === "invalid") return "Inválida o no verificada";
  if (status.warnings.some((warning) => warning.code === "LICENSE_UNSIGNED_DEV")) return "Dev sin firma";
  if (status.source === "local_file" || status.source === "dev_file") return "Firma validada";
  return "No determinada";
}

function statusCopy(status: NormalizedLicenseStatus, context: RuntimeContext) {
  if (status.state === "missing" && context.runtimeMode === "dev") {
    return "Licencia no configurada. La operación local continúa según capacidades permitidas.";
  }
  if (status.state === "missing") {
    return "Instalación pendiente de licencia local. La venta básica puede continuar en modo limitado si la política lo permite.";
  }
  if (status.denialReason === "wrong_device") return "Equipo no asignado a esta licencia. Revisa cliente, negocio, tienda y terminal.";
  if (status.operationalDecision === "deny") return "La operación requiere revisión antes de vender.";
  return "La operación local continúa según capacidades permitidas.";
}

export function LicenseStatusCard({ status, runtimeContext }: { status: NormalizedLicenseStatus; runtimeContext: RuntimeContext }) {
  const tone = toneForState(status.state);
  const isCustomerPending = status.state === "missing" && runtimeContext.runtimeMode !== "dev";
  return (
    <section className={styles.card}>
      <p className={styles.eyebrow}>Licencia local</p>
      <h1 className={styles.title}>{isCustomerPending ? "LICENSE_CUSTOMER_PENDING" : status.state === "missing" ? "Continuidad local" : `Plan ${status.plan}`}</h1>
      <p className={styles.copy}>{stateLabel(status.state)}. {statusCopy(status, runtimeContext)}</p>
      {isCustomerPending ? (
        <div className={styles.actionPanel} data-prisma-license-state="LICENSE_CUSTOMER_PENDING">
          <div>
            <strong>Instalación pendiente de licencia local</strong>
            <span>Runtime e identidad quedan trazados; falta instalar la licencia firmada en ProgramData canonical.</span>
          </div>
          <div className={styles.ctaGrid}>
            <a className={styles.primaryLink} href="http://127.0.0.1:3150/#license-ops">Importar licencia local</a>
            <a className={styles.secondaryLink} href="http://127.0.0.1:3150/#license-ops">Abrir License Ops</a>
            <a className={styles.secondaryLink} href="http://127.0.0.1:3150/api/license-ops/run/export-evidence-zip">Exportar diagnóstico</a>
            <a className={styles.secondaryLink} href="http://127.0.0.1:3150/api/license-ops/run/validate-runtime-config">Validar runtime</a>
          </div>
        </div>
      ) : null}
      <div className={styles.metricGrid}>
        <Metric label="Modo runtime" value={runtimeModeLabel(runtimeContext.runtimeMode)} />
        <Metric label="Origen config" value={provenanceLabel(runtimeContext)} />
        <Metric label="Vertical" value={runtimeContext.vertical} />
        <Metric label="Rol" value={runtimeContext.role} />
        <Metric label="Estado" value={stateLabel(status.state)} accent={tone} />
        <Metric label="Cliente" value={visibleValue(status.customerId, "Sin licencia configurada")} />
        <Metric label="Negocio" value={visibleValue(status.businessId ?? runtimeContext.businessId, "Negocio no declarado")} />
        <Metric label="Tienda/sucursal" value={visibleValue(status.storeId ?? status.branchId ?? runtimeContext.storeId, "Tienda no declarada")} />
        <Metric label="Terminal" value={visibleValue(status.terminalId ?? runtimeContext.terminalId, "Terminal no declarada")} />
        <Metric label="Dispositivo" value={visibleValue(status.deviceId ?? status.tabletId ?? runtimeContext.deviceId, "Equipo no declarado")} />
        <Metric label="Asignación" value={assignmentLabel(status.assignmentState)} />
        <Metric label="Firma" value={signatureLabel(status)} />
        <Metric label="Vence" value={visibleValue(status.validUntil, "Vigencia no disponible")} />
        <Metric label="Días restantes" value={status.daysRemaining === null ? "Sin vigencia disponible" : String(status.daysRemaining)} />
        <Metric label="Última decisión" value={visibleValue(status.lastDecisionAt, "Sin decisión registrada")} />
        <Metric label="Decisión operativa" value={decisionLabel(status.operationalDecision)} />
        <Metric label="Archivo licencia" value={visibleValue(runtimeContext.licenseFile, "Sin ruta resuelta")} />
        <Metric label="Identidad local" value={runtimeContext.deviceIdentity ? "Cargada" : "Pendiente"} />
      </div>
      {status.denialReason ? <div className={styles.warning}>Motivo de revisión: {denialReasonLabel(status.denialReason)}</div> : null}
      {runtimeContext.blockingIssues.length > 0 ? (
        <div className={styles.warningList}>
          {runtimeContext.blockingIssues.map((issue) => (
            <div key={issue.code} className={styles.warning}>
              <strong>{issue.code}</strong>: {issue.message}
            </div>
          ))}
        </div>
      ) : null}
      {status.warnings.length > 0 ? (
        <div className={styles.warningList}>
          {status.warnings.map((warning) => (
            <div key={warning.code} className={styles.warning}>
              <strong>{warning.code}</strong>: {warning.message}
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: "ok" | "warn" | "danger" }) {
  return (
    <div className={styles.metric}>
      <div className={styles.metricLabel}>{label}</div>
      <div className={[styles.metricValue, accent ? styles[`metric_${accent}`] : ""].join(" ")}>{value}</div>
    </div>
  );
}

export function FeatureList({ features }: { features: FeatureResolution[] }) {
  return (
    <section className={styles.card}>
      <h2 className={styles.title}>Features resueltas</h2>
      <div className={styles.featureList}>
        {features.map((feature) => (
          <div key={feature.key} className={styles.featureItem}>
            <div>
              <strong className={styles.featureKey}>{feature.key}</strong>
              <div className={styles.featureReason}>{feature.reason}</div>
            </div>
            <span className={[styles.badge, feature.allowed ? styles.allowed : styles.blocked].join(" ")}>
              {feature.allowed ? "Permitida" : "Bloqueada"}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function LicenseGateBanner({ message }: { message: string }) {
  return <div className={styles.warning}>{message}</div>;
}

export function LicenseBlockedCard({ title, reason }: { title: string; reason: string }) {
  return (
    <section className={styles.blockedCard}>
      <h2 className={styles.title}>{title}</h2>
      <p>{reason}</p>
      <p>La venta básica de Tablet permanece protegida por política de continuidad.</p>
    </section>
  );
}

export function LicenseWarningBadge({ children }: { children: React.ReactNode }) {
  return <span className={styles.warningBadge}>{children}</span>;
}
