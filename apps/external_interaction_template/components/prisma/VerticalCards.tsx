import { verticals } from "@/content/verticals";

export function VerticalCards() {
  const commerce = verticals.find(v => v.slug === "commerce")!;
  const supporting = verticals.filter(v => v.slug !== "commerce");

  return (
    <section className="section" id="verticales" style={{ background: 'linear-gradient(180deg, rgba(248, 250, 252, 1), rgba(241, 245, 249, 1))', padding: '4rem 1.75rem' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ marginBottom: '3rem', textAlign: 'center' }}>
          <div className="eyebrow" style={{ color: 'rgba(59, 130, 246, 0.8)', letterSpacing: '0.18em', textTransform: 'uppercase', fontSize: '0.9rem', fontWeight: 700 }}>VERTICALES PRISMA</div>
          <h2 className="large-title" style={{ color: '#1e293b', margin: '0.75rem 0 0.9rem', fontSize: 'clamp(1.9rem, 2.5vw, 2.2rem)', lineHeight: 1.15, maxWidth: '680px', marginLeft: 'auto', marginRight: 'auto' }}>Un sistema, varias operaciones.</h2>
          <p className="lead" style={{ color: 'rgba(30, 41, 59, 0.7)', maxWidth: '700px', fontSize: '1rem', lineHeight: 1.75, marginLeft: 'auto', marginRight: 'auto' }}>Empieza por venta y control diario. Escala hacia activos, campo y mando operativo.</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem', alignItems: 'start' }}>
          {/* Commerce Hero Card */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            borderRadius: '24px',
            padding: '2.5rem',
            boxShadow: '0 20px 50px rgba(0, 0, 0, 0.08)',
            overflow: 'hidden'
          }}>
            <a href={`/${commerce.slug}`} style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
              <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
                <div style={{ flex: '0 0 220px', borderRadius: '16px', overflow: 'hidden' }}>
                  <img src={commerce.image} alt={`Vista visual de PRISMA ${commerce.name}`} style={{ width: '100%', height: 'auto', display: 'block' }} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.85rem', color: 'rgba(59, 130, 246, 0.9)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>PRISMA {commerce.name}</div>
                  <h3 style={{ color: '#1e293b', fontSize: '1.6rem', lineHeight: 1.2, marginBottom: '0.75rem' }}>{commerce.headline}</h3>
                  <p style={{ color: 'rgba(30, 41, 59, 0.8)', lineHeight: 1.6, marginBottom: '1rem' }}>{commerce.promise}</p>
                  <p style={{ color: 'rgba(30, 41, 59, 0.7)', fontSize: '0.95rem', lineHeight: 1.5, marginBottom: '1rem' }}>{commerce.audience}</p>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.9rem', color: '#1e293b', fontWeight: 600, marginBottom: '0.5rem' }}>Flujo operativo:</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {commerce.flow.map((step, idx) => (
                        <span key={step} style={{
                          background: 'rgba(59, 130, 246, 0.1)',
                          color: 'rgba(59, 130, 246, 0.9)',
                          padding: '4px 10px',
                          borderRadius: '999px',
                          fontSize: '0.85rem',
                          fontWeight: 600
                        }}>
                          {idx + 1}. {step}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.9rem', color: '#1e293b', fontWeight: 600, marginBottom: '0.5rem' }}>Evidencias:</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {commerce.proof.map((proof) => (
                        <span key={proof} style={{
                          background: 'rgba(30, 41, 59, 0.1)',
                          color: '#1e293b',
                          padding: '4px 10px',
                          borderRadius: '999px',
                          fontSize: '0.85rem',
                          fontWeight: 600
                        }}>
                          {proof}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.9rem', color: '#1e293b', fontWeight: 600, marginBottom: '0.5rem' }}>Superficies:</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {Object.entries(commerce.surfaces).map(([key, value]) => (
                        <span key={key} style={{
                          background: 'rgba(59, 130, 246, 0.05)',
                          color: 'rgba(30, 41, 59, 0.8)',
                          padding: '4px 10px',
                          borderRadius: '999px',
                          fontSize: '0.8rem',
                          fontWeight: 500
                        }}>
                          {key.toUpperCase()}: {value}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </a>
          </div>

          {/* Supporting Vertical Modules */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {supporting.map((vertical) => (
              <div key={vertical.slug} style={{
                background: 'rgba(255, 255, 255, 0.9)',
                border: '1px solid rgba(59, 130, 246, 0.15)',
                borderRadius: '16px',
                padding: '1.5rem',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.06)',
                backdropFilter: 'blur(10px)'
              }}>
                <a href={`/${vertical.slug}`} style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                    <div style={{ flex: '0 0 80px', borderRadius: '12px', overflow: 'hidden' }}>
                      <img src={vertical.image} alt={`Vista visual de PRISMA ${vertical.name}`} style={{ width: '100%', height: '80px', objectFit: 'cover', display: 'block' }} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.8rem', color: 'rgba(59, 130, 246, 0.9)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.3rem' }}>PRISMA {vertical.name}</div>
                      <h4 style={{ color: '#1e293b', fontSize: '1.1rem', lineHeight: 1.3, marginBottom: '0.5rem' }}>{vertical.headline}</h4>
                      <p style={{ color: 'rgba(30, 41, 59, 0.8)', lineHeight: 1.5, marginBottom: '0.75rem', fontSize: '0.9rem' }}>{vertical.promise}</p>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                        {vertical.flow.slice(0, 2).map((step) => (
                          <span key={step} style={{
                            background: 'rgba(59, 130, 246, 0.1)',
                            color: 'rgba(59, 130, 246, 0.9)',
                            padding: '3px 8px',
                            borderRadius: '999px',
                            fontSize: '0.75rem',
                            fontWeight: 600
                          }}>
                            {step}
                          </span>
                        ))}
                        {vertical.proof.slice(0, 1).map((proof) => (
                          <span key={proof} style={{
                            background: 'rgba(30, 41, 59, 0.1)',
                            color: '#1e293b',
                            padding: '3px 8px',
                            borderRadius: '999px',
                            fontSize: '0.75rem',
                            fontWeight: 600
                          }}>
                            {proof}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </a>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
