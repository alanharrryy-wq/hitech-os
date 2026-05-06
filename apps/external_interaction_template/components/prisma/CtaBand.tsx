import { home } from "@/content/home";
import { site } from "@/content/site";

export function CtaBand() {
  return (
    <section className="prisma-cta-band">
      <div className="prisma-cta-shell">
        <div className="prisma-cta-copy">
          <div className="eyebrow">LISTO PARA OPERAR COMO SISTEMA</div>
          <h2>
            <span>Deja de operar con parches.</span>
            <span>Empieza con PRISMA.</span>
          </h2>
          <p>Conecta ventas, caja, inventario, alertas y decisiones en una operación que sí puedes supervisar.</p>

          <div className="prisma-cta-actions">
            <a className="button-primary" href={site.whatsappUrl}>{home.hero.primaryCta}</a>
            <a className="button-secondary" href="#verticales">{home.hero.secondaryCta}</a>
          </div>

          <div className="prisma-cta-note">Demo enfocada en venta, caja e inventario.</div>
        </div>

        <div className="prisma-cta-panel">
          <div className="prisma-cta-panel-inner">
            <div className="panel-eyebrow">Operación encadenada</div>
            <div className="prisma-rail" aria-hidden="true">
              <div className="rail-line" />
              <div className="rail-signal" />
              <span>Venta</span>
              <span className="rail-step">Caja</span>
              <span className="rail-step">Inventario</span>
              <span className="rail-step">Alerta</span>
              <span className="rail-step final-step">Decisión</span>
            </div>

            <div className="prisma-chip-group">
              <div className="prisma-chip-row">
                <span>Tablet vende</span>
                <span>PC gobierna</span>
                <span>Mobile supervisa</span>
              </div>
              <div className="prisma-chip-row">
                <span>Caja trazable</span>
                <span>Inventario visible</span>
                <span>Alertas accionables</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .prisma-cta-band {
          position: relative;
          overflow: hidden;
          background: radial-gradient(circle at top left, rgba(59,130,246,0.16), transparent 28%), radial-gradient(circle at bottom right, rgba(249, 168, 37, 0.08), transparent 22%), linear-gradient(180deg, #0d1523 0%, #08101a 100%);
          padding: 4.5rem 1.5rem 4rem;
          color: #f8fafc;
        }

        .prisma-cta-band::before {
          content: "";
          position: absolute;
          inset: 0;
          pointer-events: none;
          background: linear-gradient(180deg, rgba(255,255,255,0.08), transparent 42%);
          mix-blend-mode: overlay;
        }

        .prisma-cta-shell {
          position: relative;
          z-index: 1;
          max-width: 1180px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: minmax(0, 1.2fr) minmax(300px, 0.8fr);
          gap: 2rem;
          align-items: stretch;
        }

        .prisma-cta-shell::before {
          content: "";
          position: absolute;
          top: 40%;
          left: 4%;
          width: 90%;
          height: 240px;
          background: linear-gradient(130deg, rgba(59,130,246,0.16), transparent 38%, rgba(59,130,246,0.06) 100%);
          transform: translateY(-50%) rotate(-3deg);
          filter: blur(22px);
          pointer-events: none;
          z-index: 0;
        }

        .prisma-cta-copy {
          position: relative;
          border: 1px solid rgba(148,163,184,0.14);
          background: rgba(8, 16, 28, 0.9);
          box-shadow: 0 30px 90px rgba(0, 0, 0, 0.28);
          border-radius: 32px;
          padding: 2.5rem;
          display: flex;
          flex-direction: column;
          gap: 1.75rem;
          z-index: 1;
        }

        .prisma-cta-copy::after {
          content: "";
          position: absolute;
          right: -18px;
          top: 30%;
          width: 60px;
          height: 130px;
          background: rgba(59,130,246,0.08);
          filter: blur(18px);
          pointer-events: none;
        }

        .prisma-cta-copy .eyebrow {
          display: inline-flex;
          text-transform: uppercase;
          letter-spacing: 0.22em;
          color: #60a5fa;
          font-size: 0.78rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
        }

        .prisma-cta-copy h2 {
          margin: 0;
          font-size: clamp(2rem, 3.4vw, 3rem);
          line-height: 1.05;
          color: #f8fafc;
          max-width: 13ch;
        }

        .prisma-cta-copy h2 span {
          display: block;
        }

        .prisma-cta-copy h2 span + span {
          margin-top: 0.4rem;
        }

        .prisma-cta-copy p {
          margin: 0;
          max-width: 40rem;
          color: #cbd5e1;
          line-height: 1.9;
          font-size: 1rem;
        }

        .prisma-cta-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          align-items: center;
        }

        .prisma-cta-note {
          font-size: 0.95rem;
          color: rgba(226,232,240,0.82);
          font-style: italic;
        }

        .prisma-cta-panel {
          align-self: center;
          z-index: 1;
        }

        .prisma-cta-panel-inner {
          position: relative;
          background: linear-gradient(180deg, rgba(15, 23, 42, 0.94) 0%, rgba(9, 14, 24, 0.98) 100%);
          border: 1px solid rgba(96, 165, 250, 0.16);
          border-radius: 32px;
          padding: 2.2rem 1.8rem 1.8rem;
          box-shadow: 0 24px 80px rgba(0, 0, 0, 0.32);
          overflow: hidden;
        }

        .prisma-cta-panel-inner::before {
          content: "";
          position: absolute;
          right: -20px;
          top: -20px;
          width: 140px;
          height: 140px;
          border-radius: 50%;
          background: rgba(59,130,246,0.16);
          filter: blur(24px);
          pointer-events: none;
        }

        .panel-eyebrow {
          display: inline-flex;
          text-transform: uppercase;
          letter-spacing: 0.18em;
          color: #93c5fd;
          font-size: 0.82rem;
          font-weight: 700;
          margin-bottom: 1rem;
        }

        .prisma-rail {
          position: relative;
          display: grid;
          grid-template-columns: repeat(5, minmax(0, 1fr));
          gap: 0.75rem;
          align-items: center;
          padding: 1.75rem 0 0.4rem;
          border-top: 1px solid rgba(148,163,184,0.12);
          color: #e2e8f0;
          font-weight: 600;
          letter-spacing: 0.02em;
          min-height: 102px;
        }

        .rail-line {
          position: absolute;
          inset: 0.75rem 0.8rem 0.4rem;
          height: 2px;
          background: linear-gradient(90deg, rgba(96,165,250,0.28), rgba(96,165,250,0.92), rgba(59,130,246,0.28));
          z-index: 0;
        }

        .rail-signal {
          position: absolute;
          top: 0.65rem;
          left: 2.5rem;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: rgba(37,99,235,1);
          box-shadow: 0 0 22px rgba(59,130,246,0.75);
          animation: prismaCtaSignal 3.2s ease-in-out infinite;
          z-index: 1;
        }

        .rail-step {
          display: inline-flex;
          justify-content: center;
          position: relative;
          z-index: 1;
          color: rgba(226,232,240,0.88);
        }

        .final-step {
          color: #fbbf24;
          font-weight: 700;
          letter-spacing: 0.04em;
        }

        .prisma-chip-group {
          display: grid;
          gap: 0.75rem;
          margin-top: 1.5rem;
        }

        .prisma-chip-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          align-items: center;
        }

        .prisma-chip-row span {
          display: inline-flex;
          padding: 0.75rem 1rem;
          border-radius: 999px;
          background: rgba(255,255,255,0.07);
          border: 1px solid rgba(148,163,184,0.14);
          color: #e2e8f0;
          font-size: 0.9rem;
          font-weight: 600;
        }

        .button-primary {
          background: linear-gradient(135deg, rgba(59,130,246,1), rgba(37,99,235,1));
          color: white;
          padding: 1rem 2rem;
          min-width: 210px;
          border-radius: 999px;
          box-shadow: 0 18px 40px rgba(37,99,235,0.26);
          transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
        }

        .button-primary:hover,
        .button-primary:focus-visible {
          transform: translateY(-2px);
          box-shadow: 0 22px 46px rgba(37,99,235,0.34);
        }

        .button-secondary {
          background: rgba(255,255,255,0.06);
          color: #bfdbfe;
          padding: 0.98rem 1.8rem;
          min-width: 190px;
          border: 1px solid rgba(96,165,250,0.24);
          border-radius: 999px;
          transition: background 180ms ease, transform 180ms ease, border-color 180ms ease;
        }

        .button-secondary:hover,
        .button-secondary:focus-visible {
          background: rgba(255,255,255,0.12);
          transform: translateY(-1px);
          border-color: rgba(96,165,250,0.4);
        }

        @media (max-width: 900px) {
          .prisma-cta-shell {
            grid-template-columns: 1fr;
          }

          .prisma-cta-panel {
            order: -1;
          }
        }

        @media (max-width: 640px) {
          .prisma-cta-band {
            padding: 3rem 1rem 2.5rem;
          }

          .prisma-cta-copy,
          .prisma-cta-panel-inner {
            padding: 1.75rem;
          }

          .prisma-rail {
            grid-template-columns: 1fr;
            padding-top: 1rem;
          }

          .rail-step {
            justify-content: flex-start;
          }

          .prisma-chip-row {
            justify-content: center;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .rail-signal,
          .button-primary,
          .button-secondary {
            animation: none;
            transition: none;
            transform: none;
          }
        }

        @keyframes prismaCtaSignal {
          0%, 100% {
            transform: translateX(0) scale(1);
            opacity: 0.85;
          }
          50% {
            transform: translateX(calc(100% + 2rem)) scale(1.1);
            opacity: 1;
          }
        }
      `}</style>
    </section>
  );
}
