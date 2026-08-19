import { AppShell } from "@components/layout/app-shell";

export default function BarcodeHealthLoading() {
  return (
    <AppShell currentPath="/salud-barcodes">
      <section className="card" aria-busy="true" aria-live="polite">
        <div className="kicker">salud de códigos</div>
        <h1 className="section-title">Cargando revisión de códigos</h1>
        <p className="section-copy">Estamos preparando la cobertura y las incidencias disponibles.</p>
      </section>
    </AppShell>
  );
}
