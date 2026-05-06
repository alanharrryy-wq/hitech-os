import { AppShell } from "@components/layout/app-shell";

export default function StockLoading() {
  return (
    <AppShell currentPath="/stock">
      <section className="hero">
        <div className="kicker">inventario</div>
        <h1 className="hero-title">Cargando existencias...</h1>
        <p>Consultando cortes, movimientos y señales de integridad.</p>
      </section>
      <section className="card"><div className="empty-state">Preparando movimientos operativos.</div></section>
    </AppShell>
  );
}
