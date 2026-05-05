import type { FeatureResolution, NormalizedLicenseStatus } from "../../../../../shared/licensing";

function toneForState(state: string) {
  if (state === "active" || state === "development") return "#14532d";
  if (state === "offline_grace") return "#854d0e";
  return "#7f1d1d";
}

export function LicenseStatusCard({ status }: { status: NormalizedLicenseStatus }) {
  const tone = toneForState(status.state);
  return (
    <section style={{ border: "1px solid rgba(148,163,184,0.35)", borderRadius: 18, padding: 20, background: "rgba(15,23,42,0.88)", color: "#e5e7eb" }}>
      <p style={{ margin: 0, color: "#d6bd86", textTransform: "uppercase", letterSpacing: "0.12em", fontSize: 12, fontWeight: 800 }}>Licencia local</p>
      <h1 style={{ margin: "8px 0 4px", fontSize: 30 }}>Plan {status.plan}</h1>
      <p style={{ margin: 0, color: "#aeb6c1" }}>Estado runtime de licenciamiento y continuidad operativa.</p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(160px,1fr))", gap: 12, marginTop: 18 }}>
        <Metric label="Estado" value={status.state} accent={tone} />
        <Metric label="Cliente" value={status.customerId ?? "sin licencia"} />
        <Metric label="Negocio" value={status.businessId ?? "fallback"} />
        <Metric label="Vence" value={status.validUntil ?? "no disponible"} />
        <Metric label="Días restantes" value={status.daysRemaining === null ? "n/a" : String(status.daysRemaining)} />
        <Metric label="Fuente" value={status.source} />
      </div>
      {status.warnings.length > 0 ? (
        <div style={{ marginTop: 16, display: "grid", gap: 8 }}>
          {status.warnings.map((warning) => (
            <div key={warning.code} style={{ border: "1px solid rgba(250,204,21,0.35)", borderRadius: 12, padding: 12, color: "#fde68a", background: "rgba(113,63,18,0.25)" }}>
              <strong>{warning.code}</strong>: {warning.message}
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div style={{ border: "1px solid rgba(148,163,184,0.22)", borderRadius: 14, padding: 12, background: "rgba(2,6,23,0.45)" }}>
      <div style={{ color: "#94a3b8", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 800 }}>{label}</div>
      <div style={{ marginTop: 5, fontFamily: "monospace", overflowWrap: "anywhere", color: accent ? "#fff" : "#f8fafc", background: accent ?? "transparent", borderRadius: 8, padding: accent ? "2px 8px" : 0, display: "inline-block" }}>{value}</div>
    </div>
  );
}

export function FeatureList({ features }: { features: FeatureResolution[] }) {
  return (
    <section style={{ border: "1px solid rgba(148,163,184,0.30)", borderRadius: 18, padding: 18, background: "rgba(15,23,42,0.78)", color: "#e5e7eb" }}>
      <h2 style={{ marginTop: 0 }}>Features resueltas</h2>
      <div style={{ display: "grid", gap: 8 }}>
        {features.map((feature) => (
          <div key={feature.key} style={{ display: "grid", gridTemplateColumns: "minmax(180px,1fr) auto", gap: 12, alignItems: "center", border: "1px solid rgba(148,163,184,0.18)", borderRadius: 12, padding: 12, background: "rgba(2,6,23,0.35)" }}>
            <div>
              <strong style={{ fontFamily: "monospace" }}>{feature.key}</strong>
              <div style={{ color: "#94a3b8", fontSize: 13 }}>{feature.reason}</div>
            </div>
            <span style={{ borderRadius: 999, padding: "6px 10px", fontSize: 12, fontWeight: 800, color: feature.allowed ? "#bbf7d0" : "#fecaca", background: feature.allowed ? "rgba(22,101,52,0.35)" : "rgba(127,29,29,0.35)", border: `1px solid ${feature.allowed ? "rgba(34,197,94,0.4)" : "rgba(248,113,113,0.4)"}` }}>
              {feature.allowed ? "Permitida" : "Bloqueada"}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function LicenseGateBanner({ message }: { message: string }) {
  return <div style={{ border: "1px solid rgba(250,204,21,0.35)", borderRadius: 14, padding: 12, background: "rgba(113,63,18,0.28)", color: "#fde68a" }}>{message}</div>;
}

export function LicenseBlockedCard({ title, reason }: { title: string; reason: string }) {
  return (
    <section style={{ border: "1px solid rgba(248,113,113,0.35)", borderRadius: 18, padding: 18, background: "rgba(127,29,29,0.24)", color: "#fee2e2" }}>
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      <p>{reason}</p>
      <p style={{ color: "#fecaca" }}>La venta básica de Tablet permanece protegida por política de continuidad.</p>
    </section>
  );
}

export function LicenseWarningBadge({ children }: { children: React.ReactNode }) {
  return <span style={{ borderRadius: 999, padding: "4px 9px", fontSize: 12, color: "#fde68a", background: "rgba(113,63,18,0.35)", border: "1px solid rgba(250,204,21,0.35)" }}>{children}</span>;
}
