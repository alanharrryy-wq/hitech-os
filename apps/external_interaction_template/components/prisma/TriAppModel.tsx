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
    <section className="prisma-section-shell" style={{ background: 'linear-gradient(135deg, rgba(240, 248, 255, 0.5), rgba(255, 255, 255, 0.8))', padding: '4rem 2rem' }}>
      <div style={{ textAlign: 'left', marginBottom: '2rem' }}>
        <div className="eyebrow" style={{ color: 'var(--prisma-accent)' }}>MODELO TRI-APP</div>
        <h2 className="large-title" style={{ color: 'var(--prisma-text)', marginBottom: '0.5rem' }}>Tablet vende. PC gobierna. Mobile supervisa.</h2>
        <p className="lead" style={{ color: 'var(--prisma-text-secondary)', fontSize: '1.1rem' }}>PRISMA conecta la operación en un solo sistema.</p>
      </div>
      <div className="prisma-command-grid" style={{
        background: 'linear-gradient(135deg, rgba(0, 20, 40, 0.95), rgba(0, 50, 80, 0.85))',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        borderRadius: '16px',
        boxShadow: '0 8px 32px rgba(0, 100, 200, 0.4)',
        padding: '1.5rem 2rem',
        margin: '0 auto',
        maxWidth: '1200px',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        position: 'relative',
        flexWrap: 'wrap',
        gap: '2rem',
        minHeight: '350px'
      }}>
        {/* Línea horizontal de conexión */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '5%',
          right: '5%',
          height: '4px',
          background: 'linear-gradient(90deg, var(--prisma-accent), var(--prisma-accent))',
          borderRadius: '2px',
          zIndex: 1
        }}></div>
        {/* Puntos en la línea */}
        {[0, 1, 2].map((i) => (
          <div key={i} style={{
            position: 'absolute',
            top: '50%',
            left: `${20 + i * 30}%`,
            width: '12px',
            height: '12px',
            background: 'var(--prisma-accent)',
            borderRadius: '50%',
            transform: 'translate(-50%, -50%)',
            boxShadow: '0 0 12px var(--prisma-accent)',
            zIndex: 2
          }}></div>
        ))}
        {triApps.map((app, index) => (
          <div key={app.name} style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            zIndex: 3,
            flex: '1',
            minWidth: '280px',
            position: 'relative',
            marginTop: index === 0 ? '1rem' : index === 1 ? '0' : '1rem'
          }}>
            <article className="prisma-connected-card prisma-hover-lift" style={{
              background: 'rgba(255, 255, 255, 0.1)',
              border: index === 1 ? '2px solid var(--prisma-accent)' : '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '12px',
              padding: '2rem 1.5rem',
              textAlign: 'center',
              width: '100%',
              maxWidth: '320px',
              boxShadow: index === 1 ? '0 12px 40px rgba(0, 100, 200, 0.6)' : '0 6px 20px rgba(0, 0, 0, 0.3)',
              backdropFilter: 'blur(10px)',
              position: 'relative'
            }}>
              {/* LIVE label */}
              <div style={{
                position: 'absolute',
                top: '-10px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'var(--prisma-accent)',
                color: 'white',
                padding: '2px 8px',
                borderRadius: '10px',
                fontSize: '0.75rem',
                fontWeight: 'bold'
              }}>LIVE</div>
              {/* Status dot */}
              <div style={{
                position: 'absolute',
                top: '15px',
                right: '15px',
                width: '10px',
                height: '10px',
                background: 'var(--prisma-accent)',
                borderRadius: '50%',
                boxShadow: '0 0 8px var(--prisma-accent)'
              }}></div>
              <div style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--prisma-accent)', marginBottom: '0.5rem' }}>{app.number}</div>
              <div style={{ fontSize: '1rem', color: 'rgba(255, 255, 255, 0.8)', marginBottom: '0.5rem', fontWeight: '600' }}>{app.name}</div>
              <div style={{ fontSize: '1.8rem', fontWeight: '700', color: 'white', marginBottom: '1rem' }}>{app.role}</div>
              <p style={{ marginBottom: '1rem', lineHeight: '1.6', color: 'rgba(255, 255, 255, 0.9)', fontSize: '0.95rem' }}>{app.body}</p>
              <div style={{
                display: 'inline-block',
                background: 'rgba(255, 255, 255, 0.2)',
                padding: '4px 12px',
                borderRadius: '20px',
                fontSize: '0.85rem',
                color: 'white',
                marginBottom: '0.5rem'
              }}>Output: {app.output}</div>
              <div style={{ fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem' }}>{app.micro}</div>
              <div className="prisma-live-badge" style={{
                color: 'white',
                background: 'rgba(0, 100, 200, 0.3)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                padding: '4px 8px',
                borderRadius: '6px'
              }}>{app.status}</div>
            </article>
          </div>
        ))}
      </div>
    </section>
  );
}
