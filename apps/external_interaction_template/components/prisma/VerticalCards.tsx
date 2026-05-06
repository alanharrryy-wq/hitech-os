import { verticals } from "@/content/verticals";

export function VerticalCards() {
  return (
    <section className="section" id="verticales">
      <div className="eyebrow">Verticales</div>
      <h2 className="large-title">El mismo patrón, aplicado a cada giro.</h2>
      <p className="lead">Commerce, Industrial, Field y Control usan el mismo contrato: entidad, evento, responsable, estado, evidencia, alerta, reporte e historial.</p>
      <div className="grid-4" style={{ marginTop: 30 }}>
        {verticals.map((vertical) => (
          <a className="card vertical-card" href={`/${vertical.slug}`} key={vertical.slug}>
            <img src={vertical.image} alt={`Vista visual de PRISMA ${vertical.name}`} />
            <div>
              <span className="kicker">PRISMA {vertical.name}</span>
              <h3>{vertical.headline}</h3>
              <p>{vertical.promise}</p>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}
