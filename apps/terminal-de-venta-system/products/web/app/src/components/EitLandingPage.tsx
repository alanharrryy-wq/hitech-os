// PRISMA_CTX_WEB_EIT_GENERATED_V1
import type { EitSiteModel } from "@/lib/eit-site-model";

export function EitLandingPage({ model }: { model: EitSiteModel }) {
  return (
    <main className="shell">
      <section className="hero panel">
        <p className="eyebrow">{model.eyebrow}</p>
        <h1>{model.title}</h1>
        <p className="subtitle">{model.subtitle}</p>
        <div className="rule">{model.rule}</div>
      </section>

      <section className="grid" aria-label="Pilares PRISMA EIT">
        {model.pillars.map((pillar) => (
          <article className="card" key={pillar.title}>
            <h2>{pillar.title}</h2>
            <p>{pillar.body}</p>
          </article>
        ))}
      </section>

      <section className="panel routes">
        <h2>Rutas previstas</h2>
        <div>
          {model.routes.map((route) => (
            <span key={route}>{route}</span>
          ))}
        </div>
      </section>
    </main>
  );
}
