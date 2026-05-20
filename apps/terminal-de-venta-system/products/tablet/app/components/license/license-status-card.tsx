import type { FeatureResolution, NormalizedLicenseStatus } from "../../../../../shared/licensing";
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

export function LicenseStatusCard({ status }: { status: NormalizedLicenseStatus }) {
  const tone = toneForState(status.state);
  return (
    <section className={styles.card}>
      <p className={styles.eyebrow}>Licencia local</p>
      <h1 className={styles.title}>Plan {status.plan}</h1>
      <p className={styles.copy}>{stateLabel(status.state)}. {status.operationalDecision === "deny" ? "La operación requiere revisión antes de vender." : "La operación local continúa según capacidades permitidas."}</p>
      <div className={styles.metricGrid}>
        <Metric label="Estado" value={stateLabel(status.state)} accent={tone} />
        <Metric label="Cliente" value={visibleValue(status.customerId, "Sin licencia configurada")} />
        <Metric label="Negocio" value={visibleValue(status.businessId, "Negocio no declarado")} />
        <Metric label="Tienda/sucursal" value={visibleValue(status.storeId ?? status.branchId, "Tienda no declarada")} />
        <Metric label="Terminal/dispositivo" value={visibleValue(status.terminalId ?? status.deviceId ?? status.tabletId, "Equipo no declarado")} />
        <Metric label="Asignación" value={assignmentLabel(status.assignmentState)} />
        <Metric label="Vence" value={visibleValue(status.validUntil, "Vigencia no disponible")} />
        <Metric label="Días restantes" value={status.daysRemaining === null ? "Sin vigencia disponible" : String(status.daysRemaining)} />
        <Metric label="Última decisión" value={visibleValue(status.lastDecisionAt, "Sin decisión registrada")} />
        <Metric label="Decisión operativa" value={decisionLabel(status.operationalDecision)} />
      </div>
      {status.denialReason ? <div className={styles.warning}>Motivo de revisión: {denialReasonLabel(status.denialReason)}</div> : null}
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
