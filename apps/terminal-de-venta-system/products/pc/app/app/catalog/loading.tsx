import { AppShell } from "@components/layout/app-shell";

export default function CatalogLoading() {
  return (
    <AppShell currentPath="/catalog">
      <section className="hero">
        <div className="kicker">catálogo</div>
        <h1 className="hero-title">Cargando catálogo operativo...</h1>
        <p>PC prepara SKUs, barcodes y excepciones sin inventar datos.</p>
      </section>
      <section className="card">
        <div className="empty-state">
          <div className="kicker">cargando</div>
          <strong>Consultando persistencia canónica.</strong>
          <span>Si la base local no existe, la pantalla mostrará un estado honesto.</span>
        </div>
      </section>
    </AppShell>
  );
}
