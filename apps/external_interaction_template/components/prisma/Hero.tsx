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
    <>
      <style>{`
        @keyframes prismaHeroGlowDrift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        @keyframes prismaHeroFloat {
          0%, 100% { transform: translateY(0) rotate(0deg) scale(1); }
          50% { transform: translateY(-6px) rotate(0.5deg) scale(1.02); }
        }
        @keyframes prismaHeroTelemetryPulse {
          0%, 100% { box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(59, 130, 246, 0.3); border-color: rgba(59, 130, 246, 0.3); }
          50% { box-shadow: 0 16px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 215, 0, 0.2); border-color: rgba(59, 130, 246, 0.5); }
        }
        @keyframes prismaHeroSignalTravel {
          0% { opacity: 0; transform: translateX(-10px); }
          50% { opacity: 1; transform: translateX(0); }
          100% { opacity: 0; transform: translateX(10px); }
        }
        @keyframes prismaHeroCardEnter {
          0% { opacity: 0; transform: translateY(20px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes prismaHeroShine {
          0% { box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3); }
          50% { box-shadow: 0 15px 40px rgba(59, 130, 246, 0.5), 0 0 0 1px rgba(255, 215, 0, 0.1); }
          100% { box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3); }
        }
        @keyframes prismaHeroLightBeam {
          0%, 100% { opacity: 0.3; transform: scale(1) rotate(0deg); }
          50% { opacity: 0.5; transform: scale(1.1) rotate(5deg); }
        }
        @media (prefers-reduced-motion: reduce) {
          .hero { animation: none; }
          .hero-card { animation: none; }
          .hero-floating-card { animation: none; }
          .pill-row span:last-child::after { animation: none; }
          .hero-proof-card { animation: none; }
          .button-primary:hover { animation: none; }
          .hero-light-beam { animation: none; }
        }
      `}</style>
      <section className="hero" style={{ background: 'radial-gradient(ellipse at top right, rgba(173, 216, 230, 0.15) 0%, transparent 50%), linear-gradient(135deg, rgba(7, 16, 36, 0.98), rgba(5, 11, 24, 1))', padding: '4rem 1.75rem', minHeight: '100vh', display: 'flex', alignItems: 'center', backgroundSize: '200% 200%', animation: 'prismaHeroGlowDrift 20s ease-in-out infinite', position: 'relative' }}>
        <div className="hero-light-beam" style={{ position: 'absolute', top: '20%', right: '10%', width: '300px', height: '300px', background: 'radial-gradient(circle, rgba(173, 216, 230, 0.2) 0%, transparent 70%)', borderRadius: '50%', animation: 'prismaHeroLightBeam 15s ease-in-out infinite', pointerEvents: 'none' }}></div>
        <div className="hero-inner" style={{ maxWidth: '1200px', margin: '0 auto', display: 'grid', gridTemplateColumns: '46% 54%', gap: '3rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div className="eyebrow" style={{ color: 'rgba(180, 215, 255, 0.95)', letterSpacing: '0.18em', textTransform: 'uppercase', fontSize: '0.9rem', fontWeight: 700 }}>{home.hero.eyebrow}</div>

            <h1 style={{ color: 'white', fontSize: 'clamp(2.2rem, 3.8vw, 3.2rem)', lineHeight: 1.15, fontWeight: 800, maxWidth: '550px', margin: 0 }}>{home.hero.title}</h1>

            <p style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1.1rem', lineHeight: 1.6, maxWidth: '500px', margin: 0 }}>{home.hero.body}</p>

            <div className="hero-actions" style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <a className="button-primary" href={site.whatsappUrl} style={{ background: 'linear-gradient(135deg, rgba(59, 130, 246, 1), rgba(37, 99, 235, 1))', color: 'white', padding: '1rem 2rem', borderRadius: '50px', textDecoration: 'none', fontWeight: 700, fontSize: '1rem', boxShadow: '0 10px 30px rgba(59, 130, 246, 0.3)', transition: 'transform 0.2s', animation: 'prismaHeroShine 3s ease-in-out infinite' }}>
                {home.hero.primaryCta}
              </a>

              <a className="button-secondary" href="#verticales" style={{ background: 'transparent', color: 'rgba(180, 215, 255, 0.9)', padding: '1rem 2rem', border: '2px solid rgba(59, 130, 246, 0.5)', borderRadius: '50px', textDecoration: 'none', fontWeight: 600, fontSize: '1rem', transition: 'all 0.2s' }}>
                {home.hero.secondaryCta}
              </a>
            </div>

            <div style={{ fontSize: '0.85rem', color: 'rgba(255, 255, 255, 0.6)', fontStyle: 'italic', marginTop: '-1rem' }}>Sistema operativo para negocios reales, sin complicaciones.</div>

            <div className="pill-row" aria-label="Modelo operativo de PRISMA: Tablet vende, PC gobierna, Mobile supervisa" style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginTop: '1rem' }}>
              {surfacePills.map((pill, index) => (
                <span className="pill" key={pill} style={{
                  background: 'rgba(59, 130, 246, 0.15)',
                  color: 'rgba(180, 215, 255, 0.95)',
                  padding: '0.5rem 1rem',
                  borderRadius: '25px',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  position: 'relative'
                }}>
                  {pill}
                  {index < surfacePills.length - 1 && (
                    <span style={{
                      position: 'absolute',
                      right: '-0.5rem',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      color: 'rgba(255, 215, 0, 0.8)',
                      fontSize: '1rem',
                      animation: 'prismaHeroSignalTravel 2s ease-in-out infinite'
                    }}>→</span>
                  )}
                </span>
              ))}
            </div>

            <div className="hero-proof-grid" aria-label="Beneficios clave del sistema PRISMA" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '1.5rem' }}>
              {operationalStats.map((item, index) => (
                <div className="hero-proof-card" key={item.label} style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderTop: '2px solid rgba(255, 215, 0, 0.5)',
                  borderRadius: '16px',
                  padding: '1rem 0.8rem',
                  textAlign: 'center',
                  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(255, 215, 0, 0.1)',
                  animation: `prismaHeroCardEnter 0.8s ease-out ${index * 0.2}s both`
                }}>
                  <strong style={{ color: 'white', fontSize: '1.3rem', fontWeight: 800, display: 'block', marginBottom: '0.25rem' }}>{item.value}</strong>
                  <span style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.8rem', fontWeight: 500 }}>{item.label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="hero-visual" aria-label="Vista previa de PRISMA" style={{ position: 'relative', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <div className="hero-card" style={{
              position: 'relative',
              borderRadius: '24px',
              overflow: 'hidden',
              boxShadow: '0 25px 60px rgba(0, 20, 70, 0.4), 0 0 40px rgba(59, 130, 246, 0.1), 0 0 0 1px rgba(255, 215, 0, 0.2)',
              border: '2px solid rgba(255, 255, 255, 0.1)',
              maxWidth: '500px',
              width: '100%',
              animation: 'prismaHeroFloat 8s ease-in-out infinite'
            }}>
              <img
                src="/prisma/marketing/prisma-control.jpg"
                alt="Mockup visual de PRISMA con dashboard operativo"
                style={{ width: '100%', height: 'auto', display: 'block' }}
              />
              <div style={{
                position: 'absolute',
                inset: 0,
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05), transparent)',
                pointerEvents: 'none'
              }} />
            </div>

            <div className="hero-floating-card hero-floating-card-top" style={{
              position: 'absolute',
              top: '12%',
              right: '8%',
              background: 'rgba(7, 16, 36, 0.85)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderTop: '2px solid rgba(255, 215, 0, 0.4)',
              borderRadius: '12px',
              padding: '0.6rem 0.8rem',
              boxShadow: '0 12px 32px rgba(0, 0, 0, 0.25)',
              fontSize: '0.8rem',
              maxWidth: '160px',
              backdropFilter: 'blur(10px)',
              animation: 'prismaHeroTelemetryPulse 4s ease-in-out infinite'
            }}>
              <span style={{ color: 'rgba(180, 215, 255, 0.8)', display: 'block', marginBottom: '0.2rem' }}>Ventas activas</span>
              <strong style={{ color: 'white', fontWeight: 700 }}>Actualización instantánea</strong>
            </div>

            <div className="hero-floating-card hero-floating-card-bottom" style={{
              position: 'absolute',
              bottom: '18%',
              left: '8%',
              background: 'rgba(7, 16, 36, 0.85)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderTop: '2px solid rgba(255, 215, 0, 0.4)',
              borderRadius: '12px',
              padding: '0.6rem 0.8rem',
              boxShadow: '0 12px 32px rgba(0, 0, 0, 0.25)',
              fontSize: '0.8rem',
              maxWidth: '160px',
              backdropFilter: 'blur(10px)',
              animation: 'prismaHeroTelemetryPulse 4s ease-in-out infinite 1s'
            }}>
              <span style={{ color: 'rgba(180, 215, 255, 0.8)', display: 'block', marginBottom: '0.2rem' }}>Alertas inteligentes</span>
              <strong style={{ color: 'white', fontWeight: 700 }}>Prevención proactiva</strong>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}