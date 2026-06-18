// PRISMA_CTX_WEB_EIT_GENERATED_V1
import type { EitSiteModel } from "@/lib/eit-site-model";

export function EitLandingPage({ model }: { model: EitSiteModel }) {
  return (
    <main className="shell" data-prisma-panel="web.workspace" data-prisma-surface="web" data-prisma-route="/">
      <header className="brandbar" aria-label="PRISMA EIT brand">
        <a className="brandmark" href="/" aria-label="PRISMA EIT inicio">
          <img src="/prisma-mark.png" alt="" aria-hidden="true" />
          <span>
            <strong>PRISMA</strong>
            <small>Executive Intelligence Terminal</small>
          </span>
        </a>
        <span className="brand-status">Operational Knowledge OS</span>
      </header>

      <section className="hero panel">
        <div className="hero-copy">
          <p className="eyebrow">{model.eyebrow}</p>
          <h1>{model.title}</h1>
          <p className="subtitle">{model.subtitle}</p>
          <div className="rule">{model.rule}</div>
        </div>

        <div className="logo-stage" aria-label="PRISMA logo">
          <div className="logo-aura" />
          <img src="/prisma-logo.png" alt="PRISMA" />
        </div>
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
