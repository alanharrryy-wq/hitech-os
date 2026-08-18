import { AppShell } from "@components/layout/app-shell";

export const dynamic = "force-dynamic";

export default function BasicForecastPage() {
  return (
    <AppShell currentPath="/forecast-basico">
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">pronóstico</div>
            <h1 className="hero-title">Pronóstico básico</h1>
            <p>Esta ruta no tiene todavía un owner de forecast runtime certificado. No se muestran cifras, barras ni recomendaciones simuladas.</p>
          </div>
        </div>
      </section>
      <section className="card">
        <div className="section-head"><div><div className="kicker">estado honesto</div><h2 className="section-title">Pronóstico bloqueado por falta de fuente canónica</h2><div className="section-copy">El reabasto real sí está disponible y conserva señales, existencias y sugeridos sustentados por persistencia.</div></div></div>
        <div className="inline-list">
          <a className="btn btn-primary" href="/replenishment">Abrir reabasto real</a>
          <a className="btn" href="/purchasing">Abrir compras</a>
        </div>
      </section>
    </AppShell>
  );
}
