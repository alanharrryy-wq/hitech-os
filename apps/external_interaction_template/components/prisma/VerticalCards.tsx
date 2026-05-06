import { verticals } from "@/content/verticals";

export function VerticalCards() {
  return (
    <section className="section" id="verticales">
      <div className="eyebrow">Verticales</div>
      <h2 className="large-title">Restaurantes, retail, gimnasios y tiendas con caja e inventario.</h2>
      <p className="lead">Cada giro comparte el mismo patrón operativo: vender, registrar, controlar caja e inventario, y mantener alertas y trazabilidad claras.</p>
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
