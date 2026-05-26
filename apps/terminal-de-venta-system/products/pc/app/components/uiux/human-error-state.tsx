export function HumanErrorState({
  title = "No se pudo completar la acción",
  explanation = "El sistema no pudo leer o guardar la información necesaria.",
  recovery = "Reintenta la acción. Si se repite, abre la evidencia técnica.",
  actionLabel = "Reintentar",
  actionHref = "#",
  technicalDetail
}: {
  title?: string;
  explanation?: string;
  recovery?: string;
  actionLabel?: string;
  actionHref?: string;
  technicalDetail?: string;
}) {
  return (
    <section className="card" data-prisma-component="HumanErrorState" role="alert">
      <div className="kicker">requiere atención</div>
      <h2 className="section-title">{title}</h2>
      <p className="section-copy">{explanation}</p>
      <p className="section-copy">{recovery}</p>
      <div className="inline-list">
        <a className="btn btn-primary" href={actionHref}>{actionLabel}</a>
      </div>
      {technicalDetail ? (
        <details style={{ marginTop: 12 }}>
          <summary>Ver detalle técnico</summary>
          <pre style={{ whiteSpace: "pre-wrap" }}>{technicalDetail}</pre>
        </details>
      ) : null}
    </section>
  );
}
