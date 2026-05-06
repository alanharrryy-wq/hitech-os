import { notFound } from "next/navigation";
import { getVertical } from "@/content/verticals";
import { CtaBand } from "./CtaBand";

export function VerticalPage({ slug }: { slug: string }) {
  const vertical = getVertical(slug);
  if (!vertical) notFound();
  const isControl = vertical.slug === "control";

  const surfaces = [
    { name: "Tablet", role: "Captura", description: vertical.surfaces.tablet },
    { name: "PC", role: "Analiza", description: vertical.surfaces.pc },
    { name: "Mobile", role: "Notifica", description: vertical.surfaces.mobile },
    { name: "Core", role: "Normaliza", description: vertical.surfaces.core },
    { name: "Control", role: "Consolida", description: vertical.surfaces.control },
  ];

  return (
    <>
      <section className={`page-hero vertical-page${isControl ? " control-mode" : ""}`}>
        <div className="page-hero-inner">
          <div className="hero-copy">
            <div className="eyebrow">PRISMA {vertical.name}</div>
            <h1 className="large-title">{vertical.headline}</h1>
            <p className="lead">{vertical.promise}</p>

            <div className="hero-info-grid">
              <div className="info-card">
                <span className="info-label">Cliente ideal</span>
                <p>{vertical.audience}</p>
              </div>
              <div className="info-card">
                <span className="info-label">Flujo madre</span>
                <p className="flow-path">{vertical.flow.join(" → ")}</p>
              </div>
            </div>

            <div className="hero-meta-row">
              <span className="hero-chip">Alertas</span>
              <span className="hero-chip">Decisión</span>
              <span className="hero-chip">Auditoría</span>
            </div>

            {isControl ? (
              <div className="hero-flag-row">
                <span>Responsable visible</span>
                <span>Traza cambio</span>
                <span>Control ejecutivo</span>
              </div>
            ) : null}
          </div>

          <div className="hero-visual">
            <div className="image-stage">
              <div className="image-frame">
                <img src={vertical.image} alt={`PRISMA ${vertical.name}`} />
                <div className="image-tag-row">
                  <span className="image-tag">Control dashboard</span>
                  <span className="image-status">En vivo</span>
                </div>
              </div>
              <div className="image-spot" />
            </div>
          </div>
        </div>
      </section>

      <section className="section vertical-surfaces">
        <div className="surface-header">
          <div>
            <div className="eyebrow">Superficies</div>
            <h2 className="large-title">Qué hace cada app en {vertical.name}.</h2>
          </div>
          <p className="surface-intro">Cada app tiene un rol claro en el sistema: captura, análisis, notificación, normalización y control ejecutivo.</p>
        </div>
        <div className="surface-grid">
          {surfaces.map((surface) => (
            <article className="surface-card" key={surface.name}>
              <div className="surface-card-top">
                <span className="surface-name">{surface.name}</span>
                <span className="surface-role">{surface.role}</span>
              </div>
              <p>{surface.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section-tight">
        <div className="dark-band">
          <div className="eyebrow">Aceptación</div>
          <h2 className="large-title">No entra si no deja prueba.</h2>
          <div className="grid-4 flow-grid">
            {vertical.proof.map((item) => (
              <div className="flow-step" key={item}>
                <strong>{item}</strong>
                <span>Debe ser visible, trazable o auditable.</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <CtaBand />

      <style>{`
        .page-hero {
          position: relative;
          overflow: hidden;
          background: linear-gradient(180deg, #f8fbff 0%, #eef4fc 100%);
          padding: 4rem 1.5rem 2rem;
          color: #0f172a;
        }

        .page-hero::before {
          content: "";
          position: absolute;
          inset: 0;
          background-image: radial-gradient(circle at top left, rgba(59,130,246,0.16), transparent 28%), radial-gradient(circle at 80% 20%, rgba(15, 23, 42, 0.04), transparent 26%);
          pointer-events: none;
        }

        .page-hero-inner {
          position: relative;
          z-index: 1;
          max-width: 1180px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.9fr);
          gap: 2.5rem;
          align-items: center;
        }

        .page-hero-inner::after {
          content: "";
          position: absolute;
          top: 48%;
          left: 0;
          width: 100%;
          height: 240px;
          background: linear-gradient(120deg, rgba(59,130,246,0.14), transparent 52%);
          transform: translateY(-50%);
          pointer-events: none;
          filter: blur(18px);
          z-index: 0;
        }

        .hero-copy {
          position: relative;
          z-index: 1;
        }

        .hero-copy .eyebrow {
          display: inline-flex;
          text-transform: uppercase;
          letter-spacing: 0.18em;
          color: #2563eb;
          font-size: 0.78rem;
          font-weight: 700;
          margin-bottom: 1rem;
        }

        .hero-copy .large-title {
          margin: 0;
          font-size: clamp(2.7rem, 4vw, 4.4rem);
          line-height: 1.03;
          max-width: 11ch;
          color: #0f172a;
        }

        .hero-copy .lead {
          margin: 1.5rem 0 0;
          max-width: 44rem;
          color: #334155;
          line-height: 1.85;
          font-size: 1.03rem;
        }

        .hero-info-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 1rem;
          margin-top: 2rem;
        }

        .info-card {
          background: rgba(255,255,255,0.96);
          border: 1px solid rgba(15,23,42,0.08);
          border-radius: 24px;
          padding: 1.4rem 1.5rem;
          box-shadow: 0 24px 60px rgba(15,23,42,0.06);
        }

        .info-label {
          display: inline-flex;
          text-transform: uppercase;
          letter-spacing: 0.14em;
          font-size: 0.75rem;
          font-weight: 700;
          color: #2563eb;
          margin-bottom: 0.85rem;
        }

        .info-card p {
          margin: 0;
          color: #334155;
          line-height: 1.8;
          white-space: pre-wrap;
          word-break: break-word;
        }

        .flow-path {
          display: inline-flex;
          gap: 0.25rem;
          color: #475569;
        }

        .hero-meta-row,
        .hero-flag-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          margin-top: 1.5rem;
        }

        .hero-chip,
        .hero-flag-row span {
          display: inline-flex;
          padding: 0.75rem 1rem;
          border-radius: 999px;
          background: rgba(59,130,246,0.12);
          color: #1d4ed8;
          font-size: 0.88rem;
          font-weight: 700;
          border: 1px solid rgba(59,130,246,0.14);
        }

        .hero-flag-row span {
          background: rgba(15,23,42,0.06);
          color: #334155;
          border-color: rgba(15,23,42,0.08);
        }

        .hero-visual {
          position: relative;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 560px;
        }

        .image-stage {
          position: relative;
          width: 100%;
          max-width: 560px;
          padding: 1rem;
          z-index: 1;
        }

        .image-stage::before {
          content: "";
          position: absolute;
          inset: 10px;
          border-radius: 34px;
          background: radial-gradient(circle at top right, rgba(59,130,246,0.16), transparent 42%);
          filter: blur(20px);
          pointer-events: none;
        }

        .image-frame {
          position: relative;
          overflow: hidden;
          border-radius: 32px;
          border: 1px solid rgba(15,23,42,0.1);
          background: rgba(255,255,255,0.9);
          box-shadow: 0 36px 90px rgba(15,23,42,0.12);
          animation: prismaVerticalGlow 10s ease-in-out infinite;
        }

        .image-frame img {
          display: block;
          width: 100%;
          height: auto;
          object-fit: cover;
        }

        .image-tag-row {
          position: absolute;
          left: 1.2rem;
          top: 1.2rem;
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          z-index: 2;
        }

        .image-tag,
        .image-status {
          display: inline-flex;
          align-items: center;
          padding: 0.55rem 0.85rem;
          border-radius: 999px;
          font-size: 0.8rem;
          font-weight: 700;
        }

        .image-tag {
          background: rgba(15,23,42,0.88);
          color: #f8fafc;
          border: 1px solid rgba(148,163,184,0.18);
        }

        .image-status {
          background: rgba(59,130,246,0.16);
          color: #1d4ed8;
          border: 1px solid rgba(59,130,246,0.24);
        }

        .image-spot {
          position: absolute;
          bottom: -20px;
          right: 2rem;
          width: 140px;
          height: 140px;
          border-radius: 50%;
          background: rgba(59,130,246,0.08);
          filter: blur(20px);
          pointer-events: none;
        }

        .vertical-surfaces {
          position: relative;
          background: #f8fbff;
          padding: 4rem 1.5rem;
          overflow: hidden;
        }

        .surface-header {
          display: flex;
          flex-wrap: wrap;
          justify-content: space-between;
          gap: 1.5rem;
          align-items: flex-start;
          margin-bottom: 2rem;
        }

        .surface-header .eyebrow {
          color: #2563eb;
          margin-bottom: 0.75rem;
        }

        .surface-header .large-title {
          margin: 0;
          font-size: clamp(2.25rem, 3vw, 3rem);
          line-height: 1.05;
          color: #0f172a;
          max-width: 12ch;
        }

        .surface-intro {
          margin: 0;
          max-width: 38rem;
          color: #475569;
          line-height: 1.85;
          font-size: 1rem;
        }

        .surface-grid {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 1rem;
        }

        .surface-card {
          background: rgba(255,255,255,0.92);
          border: 1px solid rgba(15,23,42,0.08);
          border-radius: 26px;
          padding: 1.6rem 1.65rem;
          box-shadow: 0 18px 50px rgba(15,23,42,0.06);
          transition: transform 220ms ease, box-shadow 220ms ease;
        }

        .surface-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 26px 60px rgba(15,23,42,0.1);
        }

        .surface-card-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .surface-name {
          font-size: 0.95rem;
          letter-spacing: 0.18em;
          color: #0f172a;
          text-transform: uppercase;
          font-weight: 800;
        }

        .surface-role {
          display: inline-flex;
          padding: 0.45rem 0.85rem;
          border-radius: 999px;
          background: rgba(59,130,246,0.12);
          color: #1d4ed8;
          font-size: 0.82rem;
          font-weight: 700;
        }

        .surface-card p {
          margin: 0;
          color: #334155;
          line-height: 1.8;
          font-size: 0.97rem;
        }

        .dark-band {
          position: relative;
          background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(10, 14, 22, 0.98));
          border-radius: 30px;
          border: 1px solid rgba(59,130,246,0.16);
          padding: 3rem 1.5rem;
          box-shadow: 0 30px 80px rgba(15,23,42,0.18);
          overflow: hidden;
        }

        .dark-band .eyebrow {
          color: #93c5fd;
        }

        .dark-band .large-title {
          font-size: clamp(2rem, 3vw, 2.75rem);
          margin: 0.75rem 0 1.75rem;
          color: #f8fafc;
          max-width: 15ch;
        }

        .flow-grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .flow-step {
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 24px;
          padding: 1.4rem 1.35rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .flow-step strong {
          display: block;
          color: #f8fafc;
          font-size: 1rem;
          line-height: 1.4;
        }

        .flow-step span {
          color: rgba(226,232,240,0.76);
          font-size: 0.9rem;
          line-height: 1.7;
        }

        @media (max-width: 980px) {
          .page-hero-inner,
          .surface-grid,
          .flow-grid {
            grid-template-columns: 1fr;
          }

          .hero-info-grid {
            grid-template-columns: 1fr;
          }

          .hero-visual {
            min-height: auto;
          }
        }

        @media (max-width: 640px) {
          .page-hero {
            padding: 3rem 1rem 1.5rem;
          }

          .page-hero-inner::after {
            display: none;
          }

          .hero-copy .large-title {
            font-size: 2.4rem;
            max-width: 100%;
          }

          .hero-copy .lead {
            font-size: 1rem;
          }

          .image-stage {
            max-width: 100%;
          }

          .surface-header {
            flex-direction: column;
            gap: 1rem;
          }

          .surface-grid {
            gap: 1rem;
          }

          .flow-grid {
            gap: 1rem;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .image-frame,
          .surface-card,
          .page-hero-inner::after,
          .image-stage::before {
            animation: none;
            transition: none;
          }
        }

        @keyframes prismaVerticalGlow {
          0%, 100% {
            box-shadow: 0 36px 90px rgba(15,23,42,0.12);
          }

          50% {
            box-shadow: 0 40px 110px rgba(15,23,42,0.17);
          }
        }
      `}</style>
    </>
  );
}
