import { DecisionScreen } from "@components/uiux/decision-screen";
import { settingsGlossaryScreenContract } from "@/uiux/settings-screen-contract";

export const dynamic = "force-dynamic";

const groups = [
  {
    title: "Estados",
    items: ["Bien", "Requiere atención", "Crítico", "Pendiente", "Sin conexión"]
  },
  {
    title: "Acciones",
    items: ["Revisar", "Guardar", "Descargar", "Reintentar", "Ver detalle"]
  },
  {
    title: "Evidencia",
    items: ["Fuente", "Confianza", "Último pulso", "Historial", "Base principal"]
  }
];

export default function GlosarioPage() {
  return (
    <DecisionScreen {...settingsGlossaryScreenContract} currentPath="/glosario">
      <section className="card" data-prisma-component="GlossaryGroups">
        <div className="section-head">
          <div>
            <div className="kicker">lenguaje visible</div>
            <h2 className="section-title">El sistema debe hablar claro primero y mostrar técnica después.</h2>
            <div className="section-copy">
              Estos grupos ayudan a mantener la misma voz en pantallas, botones, tablas y evidencia.
            </div>
          </div>
        </div>
        <div className="dashboard-grid">
          {groups.map((group) => (
            <article className="card metric-card" key={group.title}>
              <div className="kicker">{group.title}</div>
              <div className="list" style={{ marginTop: 12 }}>
                {group.items.map((item) => (
                  <div className="list-item" key={item}>{item}</div>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>
    </DecisionScreen>
  );
}
