"use client";
import { AppShell } from "@components/layout/app-shell";

export default function StockError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <AppShell currentPath="/stock">
      <section className="hero">
        <div className="kicker">inventario</div>
        <h1 className="hero-title">No se pudo leer inventario.</h1>
        <p>La ruta existe, pero la lectura falló antes de presentar datos confiables.</p>
      </section>
      <section className="card">
        <div className="alert-strip"><strong>Error visible</strong><span className="subtle">{error.message}</span></div>
        <button type="button" onClick={() => reset()}>Reintentar</button>
      </section>
    </AppShell>
  );
}
