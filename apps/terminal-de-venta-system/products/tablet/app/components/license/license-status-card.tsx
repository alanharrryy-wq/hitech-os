import type { FeatureResolution, NormalizedLicenseStatus } from "../../../../../shared/licensing";
import styles from "./license-ui.module.css";

function toneForState(state: string) {
  if (state === "active" || state === "development") return "ok" as const;
  if (state === "offline_grace") return "warn" as const;
  return "danger" as const;
}

export function LicenseStatusCard({ status }: { status: NormalizedLicenseStatus }) {
  const tone = toneForState(status.state);
  return (
    <section className={styles.card}>
      <p className={styles.eyebrow}>Licencia local</p>
      <h1 className={styles.title}>Plan {status.plan}</h1>
      <p className={styles.copy}>Estado runtime de licenciamiento y continuidad operativa.</p>
      <div className={styles.metricGrid}>
        <Metric label="Estado" value={status.state} accent={tone} />
        <Metric label="Cliente" value={status.customerId ?? "sin licencia"} />
        <Metric label="Negocio" value={status.businessId ?? "fallback"} />
        <Metric label="Vence" value={status.validUntil ?? "no disponible"} />
        <Metric label="Días restantes" value={status.daysRemaining === null ? "n/a" : String(status.daysRemaining)} />
        <Metric label="Fuente" value={status.source} />
      </div>
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
