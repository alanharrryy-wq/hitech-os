import { home } from "@/content/home";
import { site } from "@/content/site";

export function TriAppModel() {
  return (
    <section className="section">
      <div className="eyebrow">Modelo tri-app</div>
      <h2 className="large-title">Tablet vende. PC gobierna. Mobile supervisa.</h2>
      <p className="lead">Cada superficie tiene un rol definido en tu operación: ventas y caja en Tablet, gobierno e inventario en PC, y supervisión ligera en Mobile.</p>
      <div className="grid-3" style={{ marginTop: 28 }}>
        {home.surfaces.map((surface) => (
          <article className="card surface-card" key={surface.name}>
            <div>
              <div className="surface-tag">{surface.name}</div>
              <div className="surface-rule">{surface.rule}</div>
              <p>{surface.body}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
