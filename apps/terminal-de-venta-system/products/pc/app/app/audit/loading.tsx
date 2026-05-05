import { AppShell } from "@components/layout/app-shell";

export default function AuditLoading() {
  return (
    <AppShell currentPath="/audit">
      <section className="hero">
        <div className="kicker">auditoría</div>
        <h1 className="hero-title">Cargando auditoría...</h1>
        <p>Buscando acciones sensibles, movimientos raros y conteos con riesgo.</p>
      </section>
      <section className="card"><div className="empty-state">Preparando evidencia de auditoría.</div></section>
    </AppShell>
  );
}
