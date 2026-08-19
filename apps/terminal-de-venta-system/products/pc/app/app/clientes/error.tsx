"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <section className="card" role="alert">
      <div className="kicker">clientes no disponibles</div>
      <h1 className="section-title">No pudimos cargar los clientes</h1>
      <p className="section-copy">No se realizó ningún cambio. Puedes intentar cargar la pantalla nuevamente.</p>
      <button className="btn btn-primary" type="button" onClick={() => reset()}>
        Reintentar
      </button>
    </section>
  );
}
