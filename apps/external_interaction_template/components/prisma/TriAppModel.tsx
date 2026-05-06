import { home } from "@/content/home";
import { site } from "@/content/site";

export function TriAppModel() {
  const triApps = [
    {
      number: "01",
      name: "Tablet",
      role: "Vende",
      body: "Atiende ventas, tickets, cobros y flujo de mostrador.",
      output: "Ticket + caja",
      status: "Operación diaria",
      micro: "Venta capturada"
    },
    {
      number: "02",
      name: "PC",
      role: "Gobierna",
      body: "Administra inventario, reglas, usuarios, reportes y cierres.",
      output: "Control + decisión",
      status: "Centro de mando",
      micro: "Regla aplicada"
    },
    {
      number: "03",
      name: "Mobile",
      role: "Supervisa",
      body: "Muestra alertas, ventas del día, caja e inventario bajo.",
      output: "Pulso + aviso",
      status: "Supervisión remota",
      micro: "Alerta enviada"
    }
  ];

  return (
    <section className="prisma-triapp-section" style={{ background: 'linear-gradient(180deg, rgba(243, 248, 255, 0.96), rgba(235, 241, 252, 0.96))', padding: '4rem 1.5rem', overflow: 'hidden' }}>
      <style>{`
        @keyframes prismaTriAppRailGlow {
          0%, 100% { box-shadow: 0 0 0 rgba(59, 130, 246, 0), inset 0 0 0 rgba(59, 130, 246, 0); }
          50% { box-shadow: 0 0 80px rgba(59, 130, 246, 0.08), inset 0 0 140px rgba(59, 130, 246, 0.05); }
        }
        @keyframes prismaTriAppSignalPulse {
          0%, 100% { transform: scale(1); opacity: 0.35; }
          50% { transform: scale(1.5); opacity: 1; }
        }
        @keyframes prismaTriAppCardLift {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
        .prisma-triapp-rail {
          position: relative;
          display: grid;
          grid-template-columns: 1fr minmax(340px, 1.2fr) 1fr;
          gap: 1.5rem;
          align-items: center;
          padding: 2.25rem 2rem 2.5rem;
          border-radius: 28px;
          background: radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 30%), radial-gradient(circle at bottom right, rgba(255, 215, 0, 0.08), transparent 25%), linear-gradient(180deg, rgba(6, 16, 40, 0.98), rgba(8, 22, 50, 0.96));
          border: 1px solid rgba(255, 255, 255, 0.12);
          box-shadow: 0 30px 90px rgba(6, 16, 40, 0.18);
          overflow: hidden;
          animation: prismaTriAppRailGlow 18s ease-in-out infinite;
        }
        .prisma-triapp-rail::before {
          content: '';
          position: absolute;
          inset: 0;
          background-image: radial-gradient(circle at 20% 40%, rgba(59, 130, 246, 0.06), transparent 22%), linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 60%);
          pointer-events: none;
        }
        .prisma-triapp-line {
          position: absolute;
          top: 50%;
          left: 6%;
          right: 6%;
          height: 3px;
          background: linear-gradient(90deg, rgba(59, 130, 246, 0.14), rgba(59, 130, 246, 0.45) 20%, rgba(255, 215, 0, 0.9) 50%, rgba(59, 130, 246, 0.45) 80%, rgba(59, 130, 246, 0.14));
          border-radius: 999px;
          z-index: 1;
        }
        .prisma-triapp-signal {
          position: absolute;
          top: 50%;
          width: 12px;
          height: 12px;
          background: rgba(59, 130, 246, 1);
          border-radius: 50%;
          box-shadow: 0 0 18px rgba(59, 130, 246, 0.45);
          transform: translate(-50%, -50%);
          z-index: 2;
          animation: prismaTriAppSignalPulse 2.4s ease-in-out infinite;
        }
        .prisma-triapp-signal:nth-of-type(2) { left: 50%; animation-delay: 0.5s; }
        .prisma-triapp-signal:nth-of-type(3) { left: 84%; animation-delay: 1s; }
        .prisma-triapp-signal:nth-of-type(1) { left: 16%; }
        .triapp-card {
          position: relative;
          background: rgba(7, 20, 42, 0.95);
          border-radius: 20px;
          padding: 2rem 1.6rem;
          min-width: 260px;
          color: white;
          z-index: 3;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
          border: 1px solid rgba(255, 255, 255, 0.08);
          backdrop-filter: blur(14px);
          animation: prismaTriAppCardLift 10s ease-in-out infinite;
        }
        .triapp-card-center {
          grid-column: 2;
          transform: translateY(-10px);
          border: 1px solid rgba(255, 215, 0, 0.38);
          box-shadow: 0 20px 60px rgba(3, 47, 102, 0.35), 0 0 30px rgba(59, 130, 246, 0.12);
        }
        .triapp-card-left { grid-column: 1; align-self: end; }
        .triapp-card-right { grid-column: 3; align-self: start; }
        .triapp-card-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }
        .triapp-card-index {
          font-size: 0.95rem;
          font-weight: 800;
          color: #7dd3fc;
        }
        .triapp-card-state {
          font-size: 0.75rem;
          font-weight: 700;
          color: #fff5c7;
          background: rgba(255, 215, 0, 0.16);
          border-radius: 999px;
          padding: 0.4rem 0.85rem;
          letter-spacing: 0.06em;
        }
        .triapp-card-name {
          font-size: 1rem;
          font-weight: 600;
          color: rgba(255, 255, 255, 0.85);
          margin-bottom: 0.35rem;
        }
        .triapp-card-role {
          font-size: 1.85rem;
          font-weight: 800;
          letter-spacing: -0.04em;
          margin-bottom: 1rem;
        }
        .triapp-card-copy {
          color: rgba(255, 255, 255, 0.88);
          line-height: 1.7;
          margin-bottom: 1.4rem;
          font-size: 0.96rem;
        }
        .triapp-chip-row {
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          gap: 0.6rem;
          margin-bottom: 0.9rem;
        }
        .triapp-chip {
          font-size: 0.82rem;
          padding: 0.45rem 0.9rem;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.08);
          color: rgba(255, 255, 255, 0.9);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .triapp-chip-strong {
          background: rgba(59, 130, 246, 0.18);
          border-color: rgba(59, 130, 246, 0.3);
        }
        .triapp-status {
          font-size: 0.82rem;
          color: #e2e8f0;
          background: rgba(255, 215, 0, 0.15);
          border: 1px solid rgba(255, 215, 0, 0.25);
          border-radius: 12px;
          padding: 0.6rem 0.9rem;
          margin-top: 0.25rem;
          font-weight: 700;
          letter-spacing: 0.02em;
        }
        .triapp-preamble .eyebrow {
          color: #0f4d95;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          font-size: 0.85rem;
          font-weight: 700;
          margin-bottom: 0.75rem;
        }
        .triapp-preamble h2 {
          color: #081b38;
          margin: 0;
          font-size: clamp(2rem, 2.5vw, 2.75rem);
          line-height: 1.05;
          letter-spacing: -0.03em;
          margin-bottom: 0.75rem;
        }
        .triapp-preamble p {
          color: #334e75;
          font-size: 1rem;
          line-height: 1.75;
          max-width: 680px;
          margin: 0;
        }
        @media (max-width: 980px) {
          .prisma-triapp-rail {
            grid-template-columns: 1fr;
            padding-left: 2.5rem;
            padding-right: 1.5rem;
          }
          .prisma-triapp-line {
            top: 4rem;
            left: 1.6rem;
            width: 3px;
            height: calc(100% - 6rem);
          }
          .prisma-triapp-signal {
            left: 1.6rem !important;
          }
          .prisma-triapp-signal:nth-of-type(2) { top: 45%; }
          .prisma-triapp-signal:nth-of-type(3) { top: 80%; }
          .triapp-card {
            width: 100%;
            min-width: auto;
            max-width: 100%;
            transform: translateY(0);
          }
          .triapp-card-left,
          .triapp-card-right,
          .triapp-card-center {
            align-self: stretch;
          }
          .triapp-card-center {
            margin-top: 0;
          }
          .triapp-preamble {
            text-align: left;
          }
        }
        @media (prefers-reduced-motion: reduce) {
          .prisma-triapp-rail,
          .triapp-card,
          .prisma-triapp-signal {
            animation: none !important;
          }
        }
      `}</style>
      <div className="triapp-preamble" style={{ marginBottom: '2rem' }}>
        <div className="eyebrow">MODELO TRI-APP</div>
        <h2>Tablet vende. PC gobierna. Mobile supervisa.</h2>
        <p>PRISMA conecta la operación en un solo sistema.</p>
      </div>
      <div className="prisma-triapp-shell" style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div className="prisma-triapp-rail">
          <div className="prisma-triapp-line" aria-hidden="true"></div>
          <div className="prisma-triapp-signal" aria-hidden="true"></div>
          <div className="prisma-triapp-signal" aria-hidden="true"></div>
          <div className="prisma-triapp-signal" aria-hidden="true"></div>
          {triApps.map((app, index) => {
            const positionClass = index === 0 ? 'triapp-card-left' : index === 1 ? 'triapp-card-center' : 'triapp-card-right';
            const isCenter = index === 1;
            return (
              <article key={app.name} className={`triapp-card ${positionClass}`} style={{ animationDuration: isCenter ? '10s' : '12s' }}>
                <div className="triapp-card-header">
                  <div className="triapp-card-index">{app.number}</div>
                  <div className="triapp-card-state">EN LÍNEA</div>
                </div>
                <div className="triapp-card-name">{app.name}</div>
                <div className="triapp-card-role">{app.role}</div>
                <p className="triapp-card-copy">{app.body}</p>
                <div className="triapp-chip-row">
                  <span className="triapp-chip triapp-chip-strong">Output: {app.output}</span>
                  <span className="triapp-chip">{app.micro}</span>
                </div>
                <div className="triapp-status">{app.status}</div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
