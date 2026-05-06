"use client";
import { AppShell } from "@components/layout/app-shell";

export default function CountsError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <AppShell currentPath="/counts">
      <section className="hero">
        <div className="kicker">conteos</div>
        <h1 className="hero-title">No se pudieron leer conteos.</h1>
        <p>La ruta existe, pero no se certifican diferencias sin datos confiables.</p>
      </section>
      <section className="card">
        <div className="alert-strip"><strong>Error visible</strong><span className="subtle">{error.message}</span></div>
        <button type="button" onClick={() => reset()}>Reintentar</button>
      </section>
    </AppShell>
  );
}
