export function EmptyStateHuman({
  title = "No hay pendientes",
  explanation = "Todo está dentro del rango esperado.",
  actionLabel,
  actionHref
}: {
  title?: string;
  explanation?: string;
  actionLabel?: string;
  actionHref?: string;
}) {
  return (
    <section className="card" data-prisma-component="EmptyStateHuman" role="status">
      <div className="kicker">sin pendientes</div>
      <h2 className="section-title">{title}</h2>
      <p className="section-copy">{explanation}</p>
      {actionLabel && actionHref ? <a className="btn btn-secondary" href={actionHref}>{actionLabel}</a> : null}
    </section>
  );
}
