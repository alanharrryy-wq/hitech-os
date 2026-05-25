import { DecisionScreen } from "@components/uiux/decision-screen";
import { settingsScreenContract } from "@/uiux/settings-screen-contract";

export const dynamic = "force-dynamic";

const settingsGroups = [
  {
    title: "Negocio",
    text: "Datos visibles, operación base y preferencias generales.",
    href: "/settings",
    action: "Revisar"
  },
  {
    title: "Usuarios",
    text: "Roles, permisos y accesos que deben cuidarse.",
    href: "/settings",
    action: "Preparar"
  },
  {
    title: "Equipos",
    text: "Terminales, tablet y dispositivos que participan en la operación.",
    href: "/devices",
    action: "Ver equipos"
  },
  {
    title: "Licencia",
    text: "Funciones activas, continuidad y estado de servicio.",
    href: "/settings/license",
    action: "Ver licencia"
  },
  {
    title: "Avanzado",
    text: "Opciones sensibles cerradas por defecto para evitar cambios accidentales.",
    href: "/data-quality",
    action: "Ver técnica"
  }
];

export default async function SettingsPage() {
  return (
    <DecisionScreen {...settingsScreenContract} currentPath="/settings">
      <section className="card" data-prisma-component="SettingsSafeZones">
        <div className="section-head">
          <div>
            <div className="kicker">zonas seguras</div>
            <h2 className="section-title">Ajusta sólo lo necesario, con impacto visible antes de guardar.</h2>
            <div className="section-copy">
              La configuración separa cambios tranquilos, cambios con cuidado y opciones avanzadas para que nadie apague la luz pensando que era el timbre.
            </div>
          </div>
        </div>
        <div className="dashboard-grid">
          {settingsGroups.map((group) => (
            <article className="card metric-card" key={group.title}>
              <div className="kicker">{group.title}</div>
              <div className="card-title">{group.action}</div>
              <p className="section-copy">{group.text}</p>
              <a className="btn btn-secondary" href={group.href}>
                {group.action}
              </a>
            </article>
          ))}
        </div>
      </section>

      <section className="card" data-prisma-component="SettingsConfirmationRules">
        <div className="kicker">confirmaciones</div>
        <h2 className="section-title">Todo cambio sensible debe explicar alcance antes de aplicarse.</h2>
        <div className="list" style={{ marginTop: 12 }}>
          <div className="list-item">Cambios para todos los equipos: confirmar antes de guardar.</div>
          <div className="list-item">Cambios de permisos: mostrar a quién afectan.</div>
          <div className="list-item">Opciones avanzadas: cerradas por defecto y con explicación.</div>
        </div>
      </section>
    </DecisionScreen>
  );
}
