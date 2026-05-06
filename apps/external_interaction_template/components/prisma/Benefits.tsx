import { home } from "@/content/home";

const benefitEvidence = {
  "Vende sin perder el control": [
    "Ticket registrado",
    "Caja trazable",
    "Movimiento de inventario",
    "Responsable visible"
  ],
  "Gobierna desde la PC": [
    "Regla aplicada",
    "Reporte diario",
    "Centro de mando",
    "Decisión clara"
  ],
  "Supervisa desde el celular": [
    "Alerta accionable",
    "Ventas al momento",
    "Inventario bajo",
    "Supervisión remota"
  ]
};

export function Benefits() {
  return (
    <section className="prisma-benefits-shell" style={{ background: 'linear-gradient(180deg, rgba(248, 252, 255, 0.96), rgba(238, 244, 252, 0.96))', padding: '4rem 1.5rem', overflow: 'hidden' }}>
      <style>{`
        @keyframes prismaBenefitsGlow {
          0%, 100% { box-shadow: 0 0 0 rgba(59, 130, 246, 0); }
          50% { box-shadow: 0 0 50px rgba(59, 130, 246, 0.08); }
        }
        @keyframes prismaBenefitsSignal {
          0% { transform: translateX(-8px) scale(0.9); opacity: 0.25; }
          50% { transform: translateX(0) scale(1); opacity: 1; }
          100% { transform: translateX(8px) scale(0.9); opacity: 0.25; }
        }
        @keyframes prismaBenefitsCardLift {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-4px); }
        }
        .prisma-benefits-headline {
          max-width: 820px;
          margin-bottom: 2rem;
        }
        .prisma-benefits-headline .eyebrow {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          color: #0f4d95;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          font-size: 0.85rem;
          font-weight: 700;
          margin-bottom: 0.85rem;
        }
        .prisma-benefits-headline h2 {
          margin: 0;
          font-size: clamp(2rem, 2.6vw, 2.9rem);
          line-height: 1.05;
          color: #081b38;
          letter-spacing: -0.03em;
        }
        .prisma-benefits-headline p {
          margin: 1rem 0 0;
          color: #334e75;
          font-size: 1rem;
          line-height: 1.75;
        }
        .prisma-benefits-grid {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 1.5rem;
          position: relative;
          align-items: stretch;
          margin-top: 1.5rem;
        }
        .prisma-benefits-grid::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 8%;
          right: 8%;
          height: 4px;
          background: linear-gradient(90deg, rgba(59, 130, 246, 0.18), rgba(59, 130, 246, 0.55) 30%, rgba(255, 215, 0, 0.9) 50%, rgba(59, 130, 246, 0.55) 70%, rgba(59, 130, 246, 0.18));
          border-radius: 999px;
          z-index: 1;
        }
        .prisma-benefits-node {
          position: relative;
          z-index: 2;
        }
        .prisma-benefits-signal {
          position: absolute;
          top: 50%;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: rgba(59, 130, 246, 1);
          box-shadow: 0 0 16px rgba(59, 130, 246, 0.35);
          transform: translate(-50%, -50%);
          animation: prismaBenefitsSignal 2.4s ease-in-out infinite;
        }
        .prisma-benefits-signal:nth-child(1) { left: 9%; }
        .prisma-benefits-signal:nth-child(2) { left: 50%; animation-delay: 0.4s; }
        .prisma-benefits-signal:nth-child(3) { left: 91%; animation-delay: 0.8s; }
        .benefit-card {
          background: linear-gradient(180deg, rgba(9, 24, 54, 0.96), rgba(11, 30, 68, 0.96));
          border-radius: 24px;
          padding: 2rem 1.6rem;
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 20px 60px rgba(9, 23, 56, 0.18);
          backdrop-filter: blur(18px);
          display: flex;
          flex-direction: column;
          gap: 1.15rem;
          min-height: 320px;
          animation: prismaBenefitsCardLift 10s ease-in-out infinite;
        }
        .benefit-card-center {
          transform: translateY(-8px);
          border-color: rgba(255, 215, 0, 0.3);
          box-shadow: 0 24px 72px rgba(10, 34, 80, 0.28), 0 0 22px rgba(59, 130, 246, 0.12);
        }
        .benefit-meter {
          font-size: 0.8rem;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: #93c5fd;
          margin-bottom: 0.35rem;
        }
        .benefit-title {
          font-size: 1.45rem;
          line-height: 1.1;
          margin: 0;
          color: white;
        }
        .benefit-copy {
          margin: 0;
          color: rgba(226, 232, 240, 0.9);
          line-height: 1.75;
          font-size: 0.98rem;
        }
        .benefit-chip-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.65rem;
          margin-top: auto;
        }
        .benefit-chip {
          display: inline-flex;
          align-items: center;
          padding: 0.55rem 0.95rem;
          border-radius: 999px;
          font-size: 0.82rem;
          color: rgba(255, 255, 255, 0.9);
          background: rgba(255, 255, 255, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.08);
          min-width: max-content;
        }
        .benefit-chip.feature {
          background: rgba(59, 130, 246, 0.16);
          border-color: rgba(59, 130, 246, 0.28);
        }
        .benefit-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 1rem;
          color: rgba(226, 232, 240, 0.75);
          font-size: 0.86rem;
          margin-top: 0.5rem;
        }
        .benefit-tag {
          display: inline-flex;
          align-items: center;
          gap: 0.45rem;
          padding: 0.55rem 0.85rem;
          border-radius: 999px;
          background: rgba(255, 215, 0, 0.12);
          color: #fff7c0;
          border: 1px solid rgba(255, 215, 0, 0.2);
          font-weight: 700;
        }
        .benefit-timespan {
          color: rgba(148, 163, 184, 0.95);
        }
        @media (max-width: 980px) {
          .prisma-benefits-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
          }
          .prisma-benefits-grid::before {
            top: 3rem;
            left: 2rem;
            width: 4px;
            height: calc(100% - 6rem);
          }
          .prisma-benefits-signal {
            left: 2rem !important;
            top: 16%;
          }
          .prisma-benefits-signal:nth-child(2) { top: 50%; }
          .prisma-benefits-signal:nth-child(3) { top: 84%; }
          .benefit-card {
            min-height: auto;
            animation: none;
          }
          .benefit-card-center {
            transform: translateY(0);
          }
        }
        @media (prefers-reduced-motion: reduce) {
          .prisma-benefits-rail,
          .benefit-card,
          .prisma-benefits-signal {
            animation: none !important;
          }
        }
      `}</style>
      <div className="prisma-benefits-headline">
        <div className="eyebrow">PRUEBA OPERATIVA</div>
        <h2>No prometas control. Enséñalo.</h2>
        <p>PRISMA convierte ventas, caja, inventario y alertas en evidencia clara para decidir.</p>
      </div>
      <div className="prisma-benefits-grid">
        {home.benefits.map((benefit, index) => {
          const isCenter = index === 1;
          const chips = benefitEvidence[benefit.title] ?? [];
          return (
            <div className="prisma-benefits-node" key={benefit.title}>
              <div className="prisma-benefits-signal" aria-hidden="true" />
              <article className={`benefit-card ${isCenter ? 'benefit-card-center' : ''}`}>
                <div className="benefit-meter">PRUEBA {index + 1}</div>
                <h3 className="benefit-title">{benefit.title}</h3>
                <p className="benefit-copy">{benefit.body}</p>
                <div className="benefit-chip-row">
                  {chips.slice(0, 3).map((chip) => (
                    <span key={chip} className={`benefit-chip ${isCenter ? 'feature' : ''}`}>{chip}</span>
                  ))}
                </div>
                <div className="benefit-footer">
                  <span className="benefit-tag">Evidencia operativa</span>
                  <span className="benefit-timespan">{index === 0 ? 'Registro inmediato' : index === 1 ? 'Control continuo' : 'Supervisión al instante'}</span>
                </div>
              </article>
            </div>
          );
        })}
      </div>
    </section>
  );
}
