"use client";
import { AppShell } from "@components/layout/app-shell";

export default function InventoryAuditError({ reset }: { error: Error; reset: () => void }) {
  return (
    <AppShell currentPath="/auditoria-inventario">
      <section className="hero">
        <div className="kicker">auditoría de inventario</div>
        <h1 className="hero-title">No pudimos cargar la auditoría</h1>
        <p>No se realizó ningún cambio. Puedes intentar cargar la información nuevamente.</p>
      </section>
      <section className="card"><button type="button" className="btn btn-primary" onClick={() => reset()}>Reintentar</button></section>
    </AppShell>
  );
}
