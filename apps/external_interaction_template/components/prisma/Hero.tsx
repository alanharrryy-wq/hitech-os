import { home } from "@/content/home";
import { site } from "@/content/site";

const operationalStats = [
  {
    value: "3",
    label: "dispositivos sincronizados"
  },
  {
    value: "24/7",
    label: "control operativo"
  },
  {
    value: "1",
    label: "sistema unificado"
  }
];

const surfacePills = [
  "Tablet vende",
  "PC gobierna",
  "Mobile supervisa"
];

export function Hero() {
  return (
    <section className="hero">
      <div className="hero-inner">
        <div>
          <div className="eyebrow">{home.hero.eyebrow}</div>

          <h1>{home.hero.title}</h1>

          <p>{home.hero.body}</p>

          <div className="hero-actions">
            <a className="button-primary" href={site.whatsappUrl}>
              {home.hero.primaryCta}
            </a>

            <a className="button-secondary" href="#verticales">
              {home.hero.secondaryCta}
            </a>
          </div>

          <div className="pill-row" aria-label="Modelo operativo de PRISMA: Tablet vende, PC gobierna, Mobile supervisa">
            {surfacePills.map((pill) => (
              <span className="pill" key={pill}>
                {pill}
              </span>
            ))}
          </div>

          <div className="hero-proof-grid" aria-label="Beneficios clave del sistema PRISMA">
            {operationalStats.map((item) => (
              <div className="hero-proof-card" key={item.label}>
                <strong>{item.value}</strong>
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="hero-visual" aria-label="Vista previa de PRISMA">
          <div className="hero-card">
            <img
              src="/prisma/marketing/prisma-control.jpg"
              alt="Mockup visual de PRISMA con dashboard operativo"
            />
          </div>

          <div className="hero-floating-card hero-floating-card-top">
            <span>Ventas activas</span>
            <strong>Actualización instantánea</strong>
          </div>

          <div className="hero-floating-card hero-floating-card-bottom">
            <span>Alertas inteligentes</span>
            <strong>Prevención proactiva</strong>
          </div>
        </div>
      </div>
    </section>
  );
}