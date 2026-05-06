"use client";

import { AppShell } from "@components/layout/app-shell";

export default function CatalogError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <AppShell currentPath="/catalog">
      <section className="hero">
        <div className="kicker">catálogo</div>
        <h1 className="hero-title">No se pudo abrir catálogo.</h1>
        <p>La ruta existe, pero la lectura falló antes de presentar datos confiables.</p>
      </section>
      <section className="card">
        <div className="alert-strip">
          <strong>Error visible</strong>
          <span className="subtle">{error.message}</span>
        </div>
        <button type="button" onClick={() => reset()}>
          Reintentar
        </button>
      </section>
    </AppShell>
  );
}
