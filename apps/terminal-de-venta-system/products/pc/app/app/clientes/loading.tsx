export default function Loading() {
  return (
    <section className="card" aria-busy="true" aria-live="polite">
      <div className="kicker">clientes</div>
      <h1 className="section-title">Cargando clientes</h1>
      <p className="section-copy">Estamos preparando el directorio y la información disponible.</p>
    </section>
  );
}
