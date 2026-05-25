"use client";
import { AppShell } from "@components/layout/app-shell";

export default function AuditError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <AppShell currentPath="/audit">
      <section className="hero">
        <div className="kicker">auditoría</div>
        <h1 className="hero-title">No se pudo abrir auditoría.</h1>
        <p>Sin evidencia confiable no se presume control operativo.</p>
      </section>
      <section className="card">
        <div className="alert-strip"><strong>Error visible</strong><span className="subtle">{error.message}</span></div>
        <button type="button" onClick={() => reset()}>Reintentar</button>
      </section>
    </AppShell>
  );
}
