import type { FeatureResolution, NormalizedLicenseStatus } from "../../../../../shared/licensing";
import type { ReactNode } from "react";
import type { PcLicenseReadiness } from "@/server/licensing/pc-license-service";

function toneClassForState(state: string) {
  if (state === "active" || state === "development") return "tone-ok";
  if (state === "offline_grace") return "tone-warn";
  return "tone-danger";
}

function stateLabel(state: string) {
  if (state === "active") return "Activa";
  if (state === "development") return "Modo de prueba";
  if (state === "offline_grace") return "Activa temporalmente sin conexión";
  if (state === "expired") return "Vencida";
  if (state === "blocked") return "Bloqueada";
  return "Requiere revisión";
}

function planLabel(plan: string) {
  const labels: Record<string, string> = {
    TABLET_SOLO: "Tablet Solo",
    TABLET_PRO: "Tablet Pro",
    TABLET_PC_MANAGED: "Tablet + PC Managed",
    TABLET_SOLO_FALLBACK: "Continuidad Tablet",
    DEVELOPMENT: "Modo de prueba"
  };
  return labels[plan] ?? "Plan PRISMA";
}

function licenseStatusCopy(status: NormalizedLicenseStatus) {
  const reason = status.denialReason || status.assignmentState;
  const copy: Record<string, string> = {
    license_missing: "No encontramos una licencia activa en este equipo.",
    license_invalid: "La licencia guardada no pudo validarse.",
    license_expired: "La licencia de este equipo está vencida.",
    license_suspended: "La licencia está suspendida y requiere atención.",
    license_revoked: "La licencia ya no está habilitada para operar.",
    wrong_customer: "Esta licencia pertenece a otra cuenta.",
    wrong_business: "Esta licencia pertenece a otro negocio.",
    wrong_store: "Esta licencia está asignada a otra sucursal.",
    wrong_device: "Este equipo no coincide con la asignación de la licencia.",
    wrong_terminal: "La licencia está vinculada a otra terminal.",
    feature_not_entitled: "El plan actual no incluye una o más funciones de esta PC.",
    device_unassigned: "Este equipo todavía no está vinculado a la licencia.",
    limit_exceeded: "El plan alcanzó el límite de equipos permitidos."
  };

  if (status.operationalDecision === "deny") {
    return copy[reason || ""] ?? "La licencia requiere atención antes de continuar.";
  }
  if (status.warnings.length > 0) {
    return "La licencia permite operar, pero hay avisos que conviene revisar.";
  }
  return "La licencia está lista para las funciones habilitadas de este plan.";
}

function featureLabel(key: string) {
  const labels: Record<string, string> = {
    "pc.open": "Acceso a PC",
    "pc.dashboard.view": "Tablero operativo",
    "pc.dashboard.executive": "Resumen ejecutivo",
    "catalog.write": "Edición de catálogo",
    "pricing.read": "Consulta de precios",
    "pricing.price-lists.write": "Listas de precios",
    "pricing.taxes.write": "Impuestos",
    "pricing.promotions.write": "Promociones",
    "pricing.discounts.write": "Descuentos",
    "pricing.authorization.request": "Solicitudes de autorización",
    "pricing.authorization.decide": "Autorizaciones de precio",
    "pricing.audit.read": "Auditoría de precios",
    "stock.adjust": "Ajustes de inventario",
    "inventory.counts": "Conteos de inventario",
    "purchase.write": "Compras",
    "receiving.write": "Recepción de mercancía",
    "replenishment.view": "Reabasto",
    "audit.view": "Auditoría",
    "sync.managed": "Sincronización administrada",
    "sync.conflict.resolve": "Resolución de revisiones",
    "multi.branch": "Múltiples sucursales",
    "multi.terminal": "Múltiples terminales",
    "multi.user.permissions": "Permisos por usuario",
    "forecast.replenishment": "Pronóstico de reabasto",
    "advanced.analytics": "Análisis avanzado"
  };
  return labels[key] ?? "Función adicional";
}

export function LicenseStatusCard({ status }: { status: NormalizedLicenseStatus }) {
  const tone = toneClassForState(status.state);
  return (
    <section className="card">
      <div className="kicker">Licencia</div>
      <h2 className="section-title">{planLabel(status.plan)}</h2>
      <p className="section-copy">{licenseStatusCopy(status)}</p>
      <div className="dashboard-actions">
        <Metric label="Estado" value={stateLabel(status.state)} tone={tone} />
        <Metric label="Vigencia" value={status.validUntil ?? "No disponible"} />
        <Metric label="Días restantes" value={status.daysRemaining === null ? "No disponible" : String(status.daysRemaining)} />
        <Metric label="Avisos" value={status.warnings.length === 0 ? "Sin avisos" : `${status.warnings.length} por revisar`} tone={status.warnings.length === 0 ? "tone-ok" : "tone-warn"} />
      </div>
    </section>
  );
}

export function LicenseReadinessCard({ readiness }: { readiness: PcLicenseReadiness }) {
  const tone = readiness.state === "ready" ? "tone-ok" : readiness.state === "warning" ? "tone-warn" : "tone-danger";
  const authorization = readiness.deviceScope.currentDeviceAuthorization === "confirmed"
    ? "Vinculado"
    : readiness.deviceScope.currentDeviceAuthorization === "not_confirmed"
      ? "Requiere vinculación"
      : "No disponible";
  const nextStep = readiness.state === "blocked"
    ? "Revisa la licencia o vuelve a vincular este equipo antes de usar las funciones restringidas."
    : readiness.state === "warning"
      ? "Puedes continuar con las funciones disponibles y revisar los avisos cuando te sea posible."
      : "No se requiere ninguna acción adicional.";

  return (
    <section className="card" data-prisma-component="LicenseReadiness">
      <div className="kicker">Disponibilidad</div>
      <h2 className="section-title">{readiness.label}</h2>
      <div className="dashboard-actions">
        <Metric label="Estado" value={readiness.label} tone={tone} />
        <Metric label="Funciones" value={`${readiness.features.allowed} disponibles · ${readiness.features.blocked} restringidas`} />
        <Metric label="Este equipo" value={authorization} tone={authorization === "Vinculado" ? "tone-ok" : "tone-warn"} />
        <Metric label="Límite de equipos PC" value={readiness.deviceScope.documentedLimit === null ? "No especificado" : String(readiness.deviceScope.documentedLimit)} />
        <Metric label="Equipos PC vinculados" value={String(readiness.deviceScope.authorizedPcDevices)} />
      </div>
      {readiness.blockers.length > 0 ? (
        <div className="alert-strip">
          <strong>Acción necesaria</strong>
          <span className="subtle">Hay una restricción de licencia que debes resolver para recuperar todas las funciones.</span>
        </div>
      ) : null}
      {readiness.warnings.length > 0 ? (
        <div className="list-item">Hay {readiness.warnings.length} aviso(s) de licencia que no impiden todas las funciones.</div>
      ) : null}
      <div className="section-copy"><strong>Siguiente paso:</strong> {nextStep}</div>
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
          <div className="kicker">Funciones</div>
          <h2 className="section-title">Lo que incluye este plan</h2>
          <p className="section-copy">Aquí ves qué herramientas están disponibles en esta PC según tu licencia.</p>
        </div>
      </div>
      <div className="list">
        {features.map((feature) => (
          <div key={feature.key} className="list-item">
            <div><strong>{featureLabel(feature.key)}</strong></div>
            <span className={`status-pill ${feature.allowed ? "tone-ok" : "tone-danger"}`}>
              {feature.allowed ? "Disponible" : "No incluida"}
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
      <p className="section-copy">Las funciones no incluidas permanecen bloqueadas sin alterar los datos ya guardados.</p>
    </section>
  );
}

export function LicenseWarningBadge({ children }: { children: ReactNode }) {
  return <span className="alert-chip">{children}</span>;
}
