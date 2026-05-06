const steps = [
  { number: "01", title: "Venta" },
  { number: "02", title: "Registro" },
  { number: "03", title: "Caja" },
  { number: "04", title: "Inventario" },
  { number: "05", title: "Alerta" },
  { number: "06", title: "Decisión" }
];

const summary = [
  {
    title: "Captura",
    body: "Venta y registro entran desde Tablet o mostrador.",
    output: "ticket + responsable"
  },
  {
    title: "Control",
    body: "Caja e inventario quedan trazados con variaciones visibles.",
    output: "movimiento auditado"
  },
  {
    title: "Decisión",
    body: "Las alertas convierten señales en acciones claras.",
    output: "riesgo detectado + siguiente paso"
  }
];

export function FlowBand() {
  return (
    <section className="prisma-section-shell" style={{ background: 'linear-gradient(180deg, rgba(7, 16, 36, 0.96), rgba(5, 11, 24, 1))', padding: '3rem 1.75rem' }}>
      <div style={{ maxWidth: '1120px', margin: '0 auto' }}>
        <div style={{ marginBottom: '1.75rem' }}>
          <div className="eyebrow" style={{ color: 'rgba(180, 215, 255, 0.95)', letterSpacing: '0.18em', textTransform: 'uppercase' }}>FLUJO OPERATIVO</div>
          <h2 className="large-title" style={{ color: 'white', margin: '0.75rem 0 0.9rem', fontSize: 'clamp(1.9rem, 2.5vw, 2.2rem)', lineHeight: 1.15, maxWidth: '680px' }}>De la venta a la decisión, sin cajas sueltas.</h2>
          <p className="lead" style={{ color: 'rgba(255, 255, 255, 0.72)', maxWidth: '700px', fontSize: '1rem', lineHeight: 1.75 }}>PRISMA conecta cada movimiento para que venta, caja, inventario y alertas terminen en una acción clara.</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2rem' }}>
          <div style={{
            position: 'relative',
            background: 'rgba(16, 30, 54, 0.96)',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: '24px',
            boxShadow: '0 18px 42px rgba(0, 20, 70, 0.35)',
            padding: '1.1rem 0.75rem 2.2rem',
            overflow: 'visible'
          }}>
            <div style={{
              position: 'absolute',
              left: '3.5%',
              right: '3.5%',
              bottom: '1.1rem',
              height: '3px',
              background: 'linear-gradient(90deg, rgba(90, 190, 255, 0.95), rgba(70, 130, 220, 0.85))',
              borderRadius: '999px',
              zIndex: 1
            }} />

            <div style={{
              position: 'relative',
              zIndex: 2,
              display: 'grid',
              gridTemplateColumns: 'repeat(6, minmax(0, 1fr))',
              gap: '0.85rem',
              alignItems: 'flex-end'
            }}>
              {steps.map((step, index) => {
                const isAlert = index === 4;
                const isDecision = index === 5;
                return (
                  <div key={step.title} style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '0.55rem',
                    padding: '0 0.15rem'
                  }}>
                    <div style={{
                      minWidth: '112px',
                      background: isDecision ? 'rgba(90, 190, 255, 0.14)' : isAlert ? 'rgba(255, 190, 100, 0.12)' : 'rgba(255, 255, 255, 0.06)',
                      border: isDecision ? '1px solid rgba(90, 190, 255, 0.4)' : isAlert ? '1px solid rgba(255, 185, 105, 0.3)' : '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: '16px',
                      padding: '0.75rem 0.85rem',
                      boxShadow: isDecision ? '0 18px 36px rgba(30, 115, 175, 0.2)' : isAlert ? '0 14px 30px rgba(180, 110, 45, 0.16)' : '0 10px 24px rgba(0, 0, 0, 0.16)'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: isAlert ? 'rgba(255, 205, 120, 0.95)' : 'rgba(90, 190, 255, 0.95)' }}>{step.number}</span>
                        <span style={{ fontSize: '0.94rem', lineHeight: 1.25, fontWeight: 700, color: 'rgba(235, 245, 255, 0.96)' }}>{step.title}</span>
                      </div>
                    </div>
                    <span style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '999px',
                      background: isDecision ? 'rgba(90, 190, 255, 1)' : isAlert ? 'rgba(255, 180, 90, 1)' : 'rgba(255, 255, 255, 0.95)',
                      border: isDecision ? '2px solid rgba(255, 255, 255, 0.22)' : '2px solid rgba(255, 255, 255, 0.12)',
                      boxShadow: isDecision ? '0 0 18px rgba(90, 190, 255, 0.32)' : isAlert ? '0 0 12px rgba(255, 190, 90, 0.28)' : '0 0 8px rgba(90, 190, 255, 0.25)' 
                    }} />
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '1rem' }}>
            {summary.map((item) => (
              <div key={item.title} style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                minHeight: '160px',
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '20px',
                padding: '1rem 1rem',
                boxShadow: '0 12px 28px rgba(0, 0, 0, 0.18)',
                backdropFilter: 'blur(10px)'
              }}>
                <div>
                  <div style={{ fontSize: '0.95rem', color: 'rgba(180, 215, 255, 0.9)', fontWeight: 700, marginBottom: '0.5rem' }}>{item.title}</div>
                  <p style={{ color: 'rgba(255, 255, 255, 0.82)', lineHeight: 1.65, margin: 0, fontSize: '0.95rem' }}>{item.body}</p>
                </div>
                <span style={{ display: 'inline-flex', color: 'white', background: 'rgba(90, 190, 255, 0.14)', padding: '5px 10px', borderRadius: '999px', fontSize: '0.84rem', fontWeight: 600 }}>Output: {item.output}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
