import { faqs } from "@/content/faq";

const faqPriority = [
  "¿Requiere instalación en PC y tablet?",
  "¿Puedo empezar por partes?",
  "¿PRISMA es solo un punto de venta?",
  "¿Sirve para restaurantes, retail y gimnasios?",
];

const faqCategory: Record<string, string> = {
  "¿Requiere instalación en PC y tablet?": "Implementación",
  "¿Puedo empezar por partes?": "Dispositivos",
  "¿PRISMA es solo un punto de venta?": "Operación",
  "¿Sirve para restaurantes, retail y gimnasios?": "Supervisión",
};

export function Faq() {
  const sortedFaqs = [...faqs].sort(
    (a, b) => faqPriority.indexOf(a.question) - faqPriority.indexOf(b.question),
  );

  return (
    <section className="section prisma-faq">
      <div className="prisma-faq-shell">
        <div className="prisma-faq-intro">
          <div className="eyebrow">DUDAS ANTES DE ARRANCAR</div>
          <h2 className="large-title">Lo que normalmente pregunta un dueño antes de meter PRISMA.</h2>
          <p className="lead">Respuestas claras sobre implementación, dispositivos, operación diaria y supervisión.</p>

          <div className="decision-card">
            <span className="faq-pill">Respuesta clara</span>
            <p>Si estás evaluando PRISMA, aquí hay cuatro dudas reales que suelen definir el siguiente paso.</p>
            <ul>
              <li>Implementación dirigida a los dispositivos clave del negocio.</li>
              <li>Arranque por fases para evitar islas operativas.</li>
              <li>Visibilidad real de ventas, caja e inventario desde el primer ciclo.</li>
            </ul>
          </div>
        </div>

        <div className="prisma-faq-list">
          {sortedFaqs.map((faq) => (
            <article className="faq-card" key={faq.question}>
              <span className="faq-chip">{faqCategory[faq.question]}</span>
              <h3>{faq.question}</h3>
              <p>{faq.answer}</p>
            </article>
          ))}
        </div>
      </div>

      <style>{`
        .prisma-faq {
          position: relative;
          overflow: hidden;
          background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
          padding: 5rem 0 4rem;
          color: #0f172a;
        }

        .prisma-faq::before {
          content: "";
          position: absolute;
          inset: 0;
          background-image: radial-gradient(circle at top right, rgba(37,99,235,0.12), transparent 26%), radial-gradient(circle at bottom left, rgba(59,130,246,0.08), transparent 16%);
          pointer-events: none;
          animation: prismaFaqGlow 18s ease-in-out infinite alternate;
        }

        .prisma-faq-shell {
          position: relative;
          z-index: 1;
          max-width: 1240px;
          margin: 0 auto;
          padding: 0 1.5rem;
          display: grid;
          gap: 2.25rem;
          grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
          align-items: start;
        }

        .prisma-faq-intro {
          max-width: 540px;
        }

        .prisma-faq .eyebrow {
          display: inline-flex;
          text-transform: uppercase;
          letter-spacing: 0.18em;
          color: #2563eb;
          font-size: 0.78rem;
          font-weight: 700;
          margin-bottom: 1rem;
        }

        .prisma-faq .large-title {
          margin: 0 0 1rem;
          font-size: clamp(2rem, 3.5vw, 3.2rem);
          line-height: 1.05;
          max-width: 10ch;
          color: #0f172a;
        }

        .prisma-faq .lead {
          margin: 0 0 2rem;
          max-width: 40rem;
          color: #475569;
          line-height: 1.85;
          font-size: 1rem;
        }

        .decision-card {
          background: rgba(255,255,255,0.95);
          border: 1px solid rgba(15,23,42,0.08);
          border-radius: 28px;
          box-shadow: 0 30px 60px rgba(15,23,42,0.06);
          padding: 2rem;
        }

        .decision-card p {
          margin: 0 0 1.25rem;
          color: #334155;
          line-height: 1.9;
        }

        .decision-card ul {
          margin: 0;
          padding: 0;
          list-style: none;
          display: grid;
          gap: 0.85rem;
        }

        .decision-card li {
          display: flex;
          gap: 0.9rem;
          color: #1f2937;
          line-height: 1.75;
        }

        .decision-card li::before {
          content: "✓";
          width: 1.55rem;
          min-width: 1.55rem;
          height: 1.55rem;
          flex-shrink: 0;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          background: rgba(37,99,235,0.14);
          color: #2563eb;
          font-size: 0.85rem;
          font-weight: 700;
        }

        .faq-pill {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 0.55rem 0.95rem;
          border-radius: 999px;
          background: rgba(37,99,235,0.12);
          color: #1d4ed8;
          font-size: 0.8rem;
          font-weight: 700;
          letter-spacing: 0.02em;
          margin-bottom: 1.25rem;
        }

        .prisma-faq-list {
          display: grid;
          gap: 1.25rem;
        }

        .faq-card {
          position: relative;
          overflow: hidden;
          background: rgba(255,255,255,0.96);
          border: 1px solid rgba(15,23,42,0.08);
          border-radius: 24px;
          padding: 1.75rem;
          box-shadow: 0 18px 40px rgba(15,23,42,0.05);
          transition: transform 280ms ease, box-shadow 280ms ease, border-color 280ms ease;
        }

        .faq-card:hover {
          transform: translateY(-4px);
          border-color: rgba(37,99,235,0.24);
          box-shadow: 0 30px 65px rgba(15,23,42,0.08);
        }

        .faq-card::after {
          content: "";
          position: absolute;
          top: 0;
          right: 0;
          width: 84px;
          height: 84px;
          background: radial-gradient(circle, rgba(59,130,246,0.16) 0%, transparent 65%);
          transform: translate(25%, -25%);
          pointer-events: none;
        }

        .faq-chip {
          display: inline-flex;
          align-items: center;
          padding: 0.45rem 0.8rem;
          border-radius: 999px;
          background: rgba(59,130,246,0.12);
          color: #1d4ed8;
          font-size: 0.78rem;
          font-weight: 700;
          letter-spacing: 0.01em;
          margin-bottom: 1rem;
        }

        .faq-card h3 {
          margin: 0 0 0.9rem;
          color: #0f172a;
          line-height: 1.25;
          font-size: 1.25rem;
        }

        .faq-card p {
          margin: 0;
          color: #475569;
          line-height: 1.8;
          font-size: 1rem;
        }

        .prisma-faq p strong {
          color: #0f172a;
        }

        @media (max-width: 960px) {
          .prisma-faq-shell {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 640px) {
          .prisma-faq {
            padding: 3rem 0 2rem;
          }

          .prisma-faq-shell {
            padding: 0 1rem;
          }

          .faq-card {
            padding: 1.5rem;
          }

          .prisma-faq .large-title {
            font-size: 2.2rem;
          }

          .faq-card::after {
            display: none;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .prisma-faq::before,
          .faq-card,
          .faq-card:hover {
            animation: none;
            transition: none;
            transform: none;
          }
        }

        @keyframes prismaFaqGlow {
          from {
            opacity: 0.22;
          }
          to {
            opacity: 0.42;
          }
        }
      `}</style>
    </section>
  );
}
