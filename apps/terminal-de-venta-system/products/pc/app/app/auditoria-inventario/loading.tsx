import { AppShell } from "@components/layout/app-shell";

export default function InventoryAuditLoading() {
  return (
    <AppShell currentPath="/auditoria-inventario">
      <section className="card" aria-busy="true" aria-live="polite">
        <div className="kicker">auditoría de inventario</div>
        <h1 className="section-title">Cargando auditoría</h1>
        <p className="section-copy">Estamos preparando el historial y los hallazgos disponibles.</p>
      </section>
    </AppShell>
  );
}
