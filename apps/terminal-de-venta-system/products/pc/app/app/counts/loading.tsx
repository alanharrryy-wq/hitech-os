import { AppShell } from "@components/layout/app-shell";

export default function CountsLoading() {
  return (
    <AppShell currentPath="/counts">
      <section className="hero">
        <div className="kicker">conteos</div>
        <h1 className="hero-title">Cargando conteos físicos...</h1>
        <p>Calculando diferencias, exactitud y estados pendientes.</p>
      </section>
      <section className="card"><div className="empty-state">Preparando conciliación de conteos.</div></section>
    </AppShell>
  );
}
