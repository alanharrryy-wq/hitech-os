import { AppShell } from "@components/layout/app-shell";

const groups = [
  { title: "Estados", items: ["Bien", "Requiere atención", "Crítico", "Pendiente", "Sin conexión"] },
  { title: "Acciones", items: ["Revisar", "Guardar", "Descargar", "Reintentar", "Ver detalle"] },
  { title: "Evidencia", items: ["Fuente", "Confianza", "Último pulso", "Historial", "Base principal"] }
];

export default function GlosarioPage() {
  return (
    <AppShell currentPath="/glosario">
      <section className="hero"><div className="hero-header"><div className="hero-copy"><div className="kicker">ayuda</div><h1 className="hero-title">Glosario</h1><p>Lenguaje visible para mantener la misma voz en pantallas, botones, tablas y evidencia.</p></div></div></section>
      <section className="card" data-prisma-component="GlossaryGroups">
        <div className="section-head"><div><div className="kicker">lenguaje visible</div><h2 className="section-title">El sistema habla claro primero y muestra técnica después.</h2></div></div>
        <div className="dashboard-grid">
          {groups.map((group) => <article className="card metric-card" key={group.title}><div className="kicker">{group.title}</div><div className="list" style={{ marginTop: 12 }}>{group.items.map((item) => <div className="list-item" key={item}>{item}</div>)}</div></article>)}
        </div>
      </section>
    </AppShell>
  );
}
