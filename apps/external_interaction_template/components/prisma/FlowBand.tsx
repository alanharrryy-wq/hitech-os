const steps = [
  ["Entidad", "Qué administra PRISMA."],
  ["Evento", "Qué pasó en operación."],
  ["Evidencia", "Qué prueba quedó."],
  ["Alerta", "Qué exige atención."],
  ["Reporte", "Qué decisión permite."]
];

export function FlowBand() {
  return (
    <section className="section-tight">
      <div className="dark-band">
        <div className="eyebrow">Core PRISMA</div>
        <h2 className="large-title">No son pantallas sueltas. Son eventos con memoria.</h2>
        <p className="lead">Cada módulo debe explicar qué entidad toca, qué evento genera, qué responsable interviene, qué estado cambia, qué evidencia deja y qué reporte alimenta.</p>
        <div className="flow">
          {steps.map(([title, body]) => (
            <div className="flow-step" key={title}>
              <strong>{title}</strong>
              <span>{body}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
