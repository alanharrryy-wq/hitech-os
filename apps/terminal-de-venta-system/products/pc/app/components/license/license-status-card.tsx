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

export function LicenseStatusCard({ status }: { status: NormalizedLicenseStatus }) {
  const tone = toneClassForState(status.state);
  return (
    <section className="card">
      <div className="kicker">Licencia local</div>
      <h2 className="section-title">Plan {status.plan}</h2>
      <p className="section-copy">Estado de licenciamiento y continuidad operativa.</p>
      <div className="dashboard-actions">
        <Metric label="Estado" value={stateLabel(status.state)} tone={tone} />
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
