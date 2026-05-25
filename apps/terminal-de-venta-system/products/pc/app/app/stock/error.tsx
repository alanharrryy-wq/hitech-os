"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <section className="card" role="alert">
      <div className="kicker">no se pudo cargar la vista</div>
      <h1 className="section-title">Intenta actualizar la pantalla</h1>
      <p className="section-copy">La información principal no se pudo preparar. La operación no se modifica.</p>
      <button className="btn btn-primary" type="button" onClick={() => reset()}>
        Reintentar
      </button>
    </section>
  );
}
