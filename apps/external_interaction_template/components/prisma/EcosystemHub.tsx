import { verticals } from "@/content/verticals";

const triApps = [
  {
    number: "01",
    name: "Tablet",
    role: "Vende",
    body: "Atiende ventas, tickets, cobros y flujo de mostrador.",
    output: "Operación diaria",
  },
  {
    number: "02",
    name: "PC",
    role: "Gobierna",
    body: "Administra inventario, reglas, usuarios, reportes y cierre.",
    output: "Centro de mando",
  },
  {
    number: "03",
    name: "Mobile",
    role: "Supervisa",
    body: "Muestra alertas, ventas del día, caja e inventario bajo.",
    output: "Supervisión remota",
  },
];

type Vertical = (typeof verticals)[number];

function getVertical(slug: string): Vertical {
  const found = verticals.find((vertical) => vertical.slug === slug);

  if (!found) {
    throw new Error(`PRISMA vertical not found: ${slug}`);
  }

  return found;
}

export function EcosystemHub() {
  const commerce = getVertical("commerce");
  const supporting = ["industrial", "field", "control"].map(getVertical);

  return (
    <section className="prisma-ecosystem-hub" id="verticales" aria-labelledby="prisma-ecosystem-title">
      <style>{`
        .prisma-ecosystem-hub {
          position: relative;
          overflow: hidden;
          padding: clamp(72px, 9vw, 118px) 1.5rem;
          background:
            radial-gradient(circle at 18% 12%, rgba(59, 130, 246, 0.13), transparent 30%),
            radial-gradient(circle at 82% 8%, rgba(251, 191, 36, 0.11), transparent 28%),
            linear-gradient(180deg, #f7faff 0%, #f2f6fc 100%);
        }

        .prisma-ecosystem-shell {
          width: min(1180px, 100%);
          margin: 0 auto;
          display: grid;
          gap: 28px;
        }

        .prisma-ecosystem-header {
          max-width: 800px;
          display: grid;
          gap: 12px;
        }

        .prisma-ecosystem-eyebrow,
        .prisma-ecosystem-card-eyebrow {
          color: #3f6fff;
          font-size: 0.68rem;
          line-height: 1;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          font-weight: 900;
        }

        .prisma-ecosystem-header h2 {
          margin: 0;
          color: #07162f;
          font-size: clamp(2.25rem, 4.4vw, 4.15rem);
          line-height: 0.92;
          letter-spacing: -0.06em;
        }

        .prisma-ecosystem-header p {
          margin: 0;
          max-width: 730px;
          color: #53617b;
          font-size: clamp(1rem, 1.3vw, 1.16rem);
          line-height: 1.65;
        }

        .prisma-ecosystem-rail {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 14px;
          padding: 16px;
          border-radius: 30px;
          background:
            linear-gradient(135deg, rgba(10, 24, 52, 0.98), rgba(9, 33, 71, 0.96)),
            radial-gradient(circle at top right, rgba(80, 136, 255, 0.22), transparent 42%);
          border: 1px solid rgba(126, 156, 224, 0.22);
          box-shadow: 0 28px 70px rgba(8, 28, 68, 0.18);
        }

        .prisma-ecosystem-rail-card {
          min-height: 164px;
          display: grid;
          gap: 10px;
          padding: 18px;
          border-radius: 22px;
          color: #f8fbff;
          background: rgba(4, 15, 36, 0.78);
          border: 1px solid rgba(136, 166, 235, 0.18);
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
        }

        .prisma-ecosystem-rail-card:nth-child(2) {
          border-color: rgba(251, 191, 36, 0.34);
          background:
            linear-gradient(180deg, rgba(11, 25, 55, 0.95), rgba(7, 20, 45, 0.92)),
            radial-gradient(circle at 50% 0%, rgba(251, 191, 36, 0.14), transparent 52%);
        }

        .prisma-ecosystem-rail-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .prisma-ecosystem-rail-top span {
          color: #8fbaff;
          font-size: 0.68rem;
          letter-spacing: 0.14em;
          font-weight: 900;
        }

        .prisma-ecosystem-rail-top strong {
          color: #ffe08a;
          background: rgba(255, 224, 138, 0.12);
          border: 1px solid rgba(255, 224, 138, 0.26);
          border-radius: 999px;
          padding: 0.32rem 0.5rem;
          font-size: 0.56rem;
          letter-spacing: 0.08em;
        }

        .prisma-ecosystem-rail-card small {
          color: #9fb4dc;
          font-weight: 800;
        }

        .prisma-ecosystem-rail-card h3 {
          margin: 0;
          font-size: clamp(1.45rem, 2.2vw, 2rem);
          line-height: 0.95;
          letter-spacing: -0.05em;
        }

        .prisma-ecosystem-rail-card p {
          margin: 0;
          color: #d7e1f4;
          font-size: 0.9rem;
          line-height: 1.5;
        }

        .prisma-ecosystem-rail-card em {
          align-self: end;
          width: fit-content;
          color: #ffe08a;
          background: rgba(251, 191, 36, 0.13);
          border: 1px solid rgba(251, 191, 36, 0.28);
          border-radius: 999px;
          padding: 0.48rem 0.72rem;
          font-style: normal;
          font-size: 0.72rem;
          font-weight: 900;
        }

        .prisma-ecosystem-grid {
          display: grid;
          grid-template-columns: minmax(0, 1.35fr) minmax(310px, 0.85fr);
          gap: 18px;
          align-items: stretch;
        }

        .prisma-ecosystem-feature,
        .prisma-ecosystem-side-card {
          background: rgba(255, 255, 255, 0.88);
          border: 1px solid rgba(133, 163, 225, 0.26);
          box-shadow: 0 24px 64px rgba(20, 46, 90, 0.10);
          backdrop-filter: blur(14px);
        }

        .prisma-ecosystem-feature {
          border-radius: 30px;
          padding: 22px;
          display: grid;
          grid-template-columns: minmax(230px, 0.75fr) minmax(0, 1fr);
          gap: 24px;
          min-height: 430px;
        }

        .prisma-ecosystem-feature-visual {
          border-radius: 24px;
          background:
            radial-gradient(circle at 50% 0%, rgba(63, 111, 255, 0.16), transparent 42%),
            linear-gradient(180deg, #eef4ff 0%, #e7eef9 100%);
          display: grid;
          place-items: center;
          padding: 24px;
          overflow: hidden;
        }

        .prisma-ecosystem-feature-visual img {
          width: min(100%, 320px);
          height: auto;
          display: block;
          filter: drop-shadow(0 24px 40px rgba(7, 22, 47, 0.18));
        }

        .prisma-ecosystem-feature-body {
          display: grid;
          gap: 14px;
          align-content: center;
        }

        .prisma-ecosystem-feature-body h3,
        .prisma-ecosystem-side-card h3 {
          margin: 0;
          color: #07162f;
          line-height: 1.02;
          letter-spacing: -0.045em;
        }

        .prisma-ecosystem-feature-body h3 {
          font-size: clamp(1.9rem, 2.7vw, 2.7rem);
        }

        .prisma-ecosystem-side-card h3 {
          font-size: 1.18rem;
        }

        .prisma-ecosystem-feature-body p,
        .prisma-ecosystem-side-card p {
          margin: 0;
          color: #4e5d78;
          line-height: 1.58;
        }

        .prisma-ecosystem-chip-row {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .prisma-ecosystem-chip {
          display: inline-flex;
          align-items: center;
          border-radius: 999px;
          padding: 0.44rem 0.7rem;
          color: #284ba7;
          background: #edf3ff;
          font-size: 0.72rem;
          font-weight: 900;
        }

        .prisma-ecosystem-chip-soft {
          color: #566782;
          background: #f2f5fa;
        }

        .prisma-ecosystem-flow {
          display: grid;
          gap: 8px;
        }

        .prisma-ecosystem-flow strong {
          color: #07162f;
          font-size: 0.88rem;
        }

        .prisma-ecosystem-flow div {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .prisma-ecosystem-flow span {
          border-radius: 999px;
          padding: 0.5rem 0.72rem;
          color: #08245a;
          background: rgba(251, 191, 36, 0.14);
          border: 1px solid rgba(251, 191, 36, 0.26);
          font-size: 0.76rem;
          font-weight: 900;
        }

        .prisma-ecosystem-link {
          width: fit-content;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border-radius: 999px;
          padding: 0.78rem 1.04rem;
          background: #0d2a5d;
          color: white;
          text-decoration: none;
          font-weight: 900;
          box-shadow: 0 14px 34px rgba(13, 42, 93, 0.18);
        }

        .prisma-ecosystem-link-ghost {
          padding: 0;
          background: transparent;
          color: #315fd6;
          box-shadow: none;
        }

        .prisma-ecosystem-stack {
          display: grid;
          gap: 14px;
        }

        .prisma-ecosystem-side-card {
          border-radius: 24px;
          padding: 18px;
          display: grid;
          gap: 12px;
        }

        .prisma-ecosystem-side-head {
          display: grid;
          grid-template-columns: 70px minmax(0, 1fr);
          gap: 12px;
          align-items: start;
        }

        .prisma-ecosystem-side-head img {
          width: 70px;
          height: 70px;
          object-fit: cover;
          border-radius: 18px;
          display: block;
          border: 1px solid rgba(7, 22, 47, 0.08);
        }

        @media (max-width: 1024px) {
          .prisma-ecosystem-grid {
            grid-template-columns: 1fr;
          }

          .prisma-ecosystem-feature {
            grid-template-columns: 1fr;
          }

          .prisma-ecosystem-feature-visual {
            min-height: 320px;
          }
        }

        @media (max-width: 820px) {
          .prisma-ecosystem-rail {
            grid-template-columns: 1fr;
          }

          .prisma-ecosystem-feature {
            padding: 18px;
          }

          .prisma-ecosystem-side-head {
            grid-template-columns: 56px minmax(0, 1fr);
          }

          .prisma-ecosystem-side-head img {
            width: 56px;
            height: 56px;
            border-radius: 15px;
          }
        }
      `}</style>

      <div className="prisma-ecosystem-shell">
        <header className="prisma-ecosystem-header">
          <span className="prisma-ecosystem-eyebrow">ECOSISTEMA PRISMA</span>
          <h2 id="prisma-ecosystem-title">Un sistema. Varias operaciones.</h2>
          <p>
            Tablet vende. PC gobierna. Mobile supervisa. Después eliges la vertical:
            comercio, industrial, campo o control.
          </p>
        </header>

        <div className="prisma-ecosystem-rail" aria-label="Modelo operativo tri-app">
          {triApps.map((app) => (
            <article className="prisma-ecosystem-rail-card" key={app.name}>
              <div className="prisma-ecosystem-rail-top">
                <span>{app.number}</span>
                <strong>EN LÍNEA</strong>
              </div>
              <small>{app.name}</small>
              <h3>{app.role}</h3>
              <p>{app.body}</p>
              <em>{app.output}</em>
            </article>
          ))}
        </div>

        <div className="prisma-ecosystem-grid">
          <article className="prisma-ecosystem-feature">
            <a className="prisma-ecosystem-feature-visual" href={`/${commerce.slug}`} aria-label={`Ver PRISMA ${commerce.name}`}>
              <img src={commerce.image} alt={`Vista visual de PRISMA ${commerce.name}`} />
            </a>

            <div className="prisma-ecosystem-feature-body">
              <span className="prisma-ecosystem-card-eyebrow">PRISMA {commerce.name}</span>
              <h3>{commerce.headline}</h3>
              <p>{commerce.promise}</p>

              <div className="prisma-ecosystem-chip-row">
                {commerce.flow.slice(0, 5).map((step) => (
                  <span className="prisma-ecosystem-chip" key={step}>{step}</span>
                ))}
              </div>

              <div className="prisma-ecosystem-flow">
                <strong>Cómo se conecta:</strong>
                <div>
                  <span>Tablet opera</span>
                  <span>PC controla</span>
                  <span>Mobile avisa</span>
                </div>
              </div>

              <a className="prisma-ecosystem-link" href={`/${commerce.slug}`}>
                Ver Commerce
              </a>
            </div>
          </article>

          <div className="prisma-ecosystem-stack">
            {supporting.map((vertical) => (
              <article className="prisma-ecosystem-side-card" key={vertical.slug}>
                <a className="prisma-ecosystem-side-head" href={`/${vertical.slug}`} style={{ textDecoration: "none" }}>
                  <img src={vertical.image} alt={`Vista visual de PRISMA ${vertical.name}`} />
                  <div>
                    <span className="prisma-ecosystem-card-eyebrow">PRISMA {vertical.name}</span>
                    <h3>{vertical.headline}</h3>
                  </div>
                </a>

                <p>{vertical.promise}</p>

                <div className="prisma-ecosystem-chip-row">
                  {vertical.flow.slice(0, 2).map((step) => (
                    <span className="prisma-ecosystem-chip prisma-ecosystem-chip-soft" key={step}>
                      {step}
                    </span>
                  ))}
                  {vertical.proof.slice(0, 1).map((proof) => (
                    <span className="prisma-ecosystem-chip prisma-ecosystem-chip-soft" key={proof}>
                      {proof}
                    </span>
                  ))}
                </div>

                <a className="prisma-ecosystem-link prisma-ecosystem-link-ghost" href={`/${vertical.slug}`}>
                  Ver vertical
                </a>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
