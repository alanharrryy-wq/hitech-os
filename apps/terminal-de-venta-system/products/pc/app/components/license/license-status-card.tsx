import type { FeatureResolution, NormalizedLicenseStatus } from "../../../../../shared/licensing";
import type { ReactNode } from "react";

function toneClassForState(state: string) {
  if (state === "active" || state === "development") return "tone-ok";
  if (state === "offline_grace") return "tone-warn";
  return "tone-danger";
}

function stateLabel(state: string) {
  if (state === "active") return "activa";
  if (state === "development") return "desarrollo";
  if (state === "offline_grace") return "gracia sin conexión";
  if (state === "expired") return "vencida";
  if (state === "blocked") return "bloqueada";
  return state;
}

function supportIssueCode(status: NormalizedLicenseStatus) {
  const reason = status.denialReason || status.assignmentState;
  const map: Record<string, string> = {
    license_missing: "LICENSE_LOCAL_MISSING",
    license_invalid: "LICENSE_LOCAL_INVALID",
    license_expired: "LICENSE_EXPIRED",
    license_suspended: "LICENSE_LOCAL_INVALID",
    license_revoked: "LICENSE_LOCAL_INVALID",
    wrong_customer: "LICENSE_ASSIGNMENT_WRONG_CUSTOMER",
    wrong_business: "LICENSE_ASSIGNMENT_WRONG_BUSINESS",
    wrong_store: "LICENSE_ASSIGNMENT_WRONG_STORE",
    wrong_device: "PC_DEVICE_ASSIGNMENT_MISMATCH",
    wrong_terminal: "LICENSE_ASSIGNMENT_WRONG_TERMINAL",
    feature_not_entitled: "PC_FEATURES_BLOCKED_BY_LICENSE",
    device_unassigned: "PC_ADMIN_SLOT_NOT_CLAIMED"
  };
  if (status.operationalDecision === "deny") return map[reason || ""] || "PC_SUPPORT_STATUS_CONTRADICTION";
  if (status.warnings.length > 0) return status.warnings[0]?.code || "PC_SUPPORT_STATUS_CONTRADICTION";
  return "OK";
}

function supportIssueCopy(status: NormalizedLicenseStatus) {
  const code = supportIssueCode(status);
  if (code === "LICENSE_ASSIGNMENT_WRONG_BUSINESS") {
    return "La licencia esta activa, pero pertenece a otro negocio. La operacion queda bloqueada hasta reclamar el dispositivo correcto o refrescar la licencia.";
  }
  if (code === "OK") return "Sin bloqueo principal detectado.";
  return "Revisar el codigo canonico en Prisma Support Resolver Center.";
}

export function LicenseStatusCard({ status }: { status: NormalizedLicenseStatus }) {
  const tone = toneClassForState(status.state);
  const issueCode = supportIssueCode(status);
  return (
    <section className="card">
      <div className="kicker">Licencia local</div>
      <h2 className="section-title">Plan {status.plan}</h2>
      <p className="section-copy">{supportIssueCopy(status)}</p>
      <div className="dashboard-actions">
        <Metric label="Estado" value={stateLabel(status.state)} tone={tone} />
        <Metric label="Issue principal" value={issueCode} tone={issueCode === "OK" ? "tone-ok" : "tone-danger"} />
        <Metric label="Cliente" value={status.customerId ?? "sin licencia"} />
        <Metric label="Negocio" value={status.businessId ?? "respaldo local"} />
        <Metric label="Vence" value={status.validUntil ?? "no disponible"} />
        <Metric label="Días restantes" value={status.daysRemaining === null ? "no disponible" : String(status.daysRemaining)} />
        <Metric label="Fuente" value={status.source} />
      </div>
      {status.warnings.length > 0 ? (
        <div className="list">
          {status.warnings.map((warning) => (
            <div key={warning.code} className="alert-strip">
              <strong>{warning.code}</strong>: {warning.message}
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div className="action-card">
      <strong>{label}</strong>
      <span className={tone ? `status-pill ${tone}` : "subtle"}>{value}</span>
    </div>
  );
}

export function FeatureList({ features }: { features: FeatureResolution[] }) {
  return (
    <section className="card">
      <div className="section-head">
        <div>
          <div className="kicker">funciones</div>
          <h2 className="section-title">Funciones resueltas</h2>
          <p className="section-copy">Permisos operativos evaluados desde la licencia local.</p>
        </div>
      </div>
      <div className="list">
        {features.map((feature) => (
          <div key={feature.key} className="list-item">
            <div>
              <strong>{feature.key}</strong>
              <div className="subtle">{feature.reason}</div>
            </div>
            <span className={`status-pill ${feature.allowed ? "tone-ok" : "tone-danger"}`}>
              {feature.allowed ? "Permitida" : "Bloqueada"}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function LicenseGateBanner({ message }: { message: string }) {
  return <div className="alert-strip">{message}</div>;
}

export function LicenseBlockedCard({ title, reason }: { title: string; reason: string }) {
  return (
    <section className="card">
      <h2 className="section-title">{title}</h2>
      <p>{reason}</p>
      <p className="section-copy">La venta básica de Tablet permanece protegida por política de continuidad.</p>
    </section>
  );
}

export function LicenseWarningBadge({ children }: { children: ReactNode }) {
  return <span className="alert-chip">{children}</span>;
}
