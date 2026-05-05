import { home } from "@/content/home";
import { site } from "@/content/site";

export function Hero() {
  return (
    <section className="hero">
      <div className="hero-inner">
        <div>
          <div className="eyebrow">{home.hero.eyebrow}</div>
          <h1>{home.hero.title}</h1>
          <p>{home.hero.body}</p>
          <div className="hero-actions">
            <a className="button-primary" href={site.whatsappUrl}>{home.hero.primaryCta}</a>
            <a className="button-secondary" href="#verticales">{home.hero.secondaryCta}</a>
          </div>
          <div className="pill-row" aria-label="Regla operativa PRISMA">
            <span className="pill">Tablet opera</span>
            <span className="pill">PC gobierna</span>
            <span className="pill">Mobile supervisa</span>
          </div>
        </div>
        <div className="hero-card">
          <img src="/prisma/marketing/prisma-control.jpg" alt="Mockup visual de PRISMA con dashboard operativo" />
        </div>
      </div>
    </section>
  );
}
