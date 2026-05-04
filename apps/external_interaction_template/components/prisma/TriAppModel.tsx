import { home } from "@/content/home";
import { site } from "@/content/site";

export function TriAppModel() {
  return (
    <section className="section">
      <div className="eyebrow">Modelo operativo</div>
      <h2 className="large-title">Una plataforma. Tres superficies. Un historial que no se hace pato.</h2>
      <p className="lead">{site.operatingRule}</p>
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
