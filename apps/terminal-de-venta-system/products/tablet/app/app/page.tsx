import styles from './prisma-tablet-light-shell.module.css';

const attentionCards = [
  {
    label: 'Venta rápida',
    value: 'Listo para vender',
    detail: 'Inicia ventas desde la tablet, agrega productos al ticket y cobra de forma clara y segura.',
    tone: 'live',
  },
  {
    label: 'Control central',
    value: 'PC + Tablet',
    detail: 'Conecta una o varias tablets a la PC para administrar catálogo, ventas, inventario y operación.',
    tone: 'ice',
  },
  {
    label: 'Crecimiento',
    value: 'Multi-comercio',
    detail: 'PRISMA puede acompañar la operación de varios comercios con más visibilidad y control.',
    tone: 'locked',
  },
];

const quickRoutes = [
  ['Vender', '/pos', 'Inicia una nueva venta en la tablet.'],
  ['Catálogo', '/catalog', 'Consulta productos, precios y existencias.'],
  ['Ventas de hoy', '/sales/today', 'Revisa tickets, totales y actividad diaria.'],
  ['Turno y caja', '/shift', 'Controla el turno activo y prepara el cierre.'],
  ['Sincronización', '/sync', 'Verifica conexión, actualizaciones y operaciones pendientes.'],
  ['Licencia', '/settings/license', 'Revisa activación, permisos y estado del sistema.'],
];

const ecosystem = [
  ['Tablet', 'Punto de venta ágil para atender clientes en piso.'],
  ['PC', 'Centro de administración para catálogo, ventas, inventario y reportes.'],
  ['App', 'Consulta móvil para mantenerte cerca de la operación.'],
  ['Varias tablets', 'Conecta múltiples tablets a una PC para ampliar la atención.'],
  ['Multi-comercio', 'Monitorea más de un negocio desde el ecosistema PRISMA.'],
];

const statusSummary = [
  ['Operación', 'Lista'],
  ['Sync', 'Activa'],
  ['Licencia', 'Vigente'],
  ['Modo local', 'Disponible'],
];

export default function TabletHomePage() {
  return (
    <main
      className={styles.tabletShell}
      data-prisma-surface="tablet-light-shell"
      data-tablet-light-first="true"
      data-prisma-background="tablet-background-active"
    >
      <section className={styles.atmosphere} aria-hidden="true" />
      <section className={styles.lightScrim} aria-hidden="true" />
      <section className={styles.grain} aria-hidden="true" />

      <div className={styles.frame}>
        <header className={styles.chromeBar}>
          <div className={styles.brandCluster}>
            <span className={styles.brandMark}>P</span>
            <div>
              <p className={styles.eyebrow}>PRISMA Tablet</p>
              <h1>Inicio operativo</h1>
            </div>
          </div>
          <div className={styles.guardrailPill} aria-label="Estado operativo">
            <span className={styles.liveDot} />
            <span>Sistema listo para operar</span>
          </div>
        </header>

        <section className={styles.heroPanel}>
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>Punto de venta conectado</p>
            <h2>Vende, administra y crece con PRISMA.</h2>
            <p>
              Desde esta tablet puedes atender clientes, iniciar ventas, consultar productos,
              revisar existencias y mantener tu operación sincronizada. PRISMA también se conecta
              con PC y App para darte más control, más alcance y una visión completa de tu negocio.
            </p>
            <div className={styles.heroActions}>
              <a className={styles.primaryAction} href="/pos">Iniciar venta</a>
              <a className={styles.secondaryAction} href="/sync">Revisar sincronización</a>
            </div>
          </div>

          <aside className={styles.weatherCard} aria-label="Resumen del ecosistema PRISMA">
            <span className={styles.cardKicker}>Ecosistema PRISMA</span>
            <strong>3</strong>
            <p>Tablet, PC y App trabajando juntos para vender, administrar y monitorear mejor.</p>
            <div className={styles.forecastStrip}>
              {statusSummary.map(([label, value]) => (
                <span key={label}>
                  <small>{label}</small>
                  <b>{value}</b>
                </span>
              ))}
            </div>
          </aside>
        </section>

        <section className={styles.cardGrid} aria-label="Beneficios principales">
          {attentionCards.map((item) => (
            <article key={item.label} className={styles.kpiCard} data-tone={item.tone}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <p>{item.detail}</p>
            </article>
          ))}
        </section>

        <section className={styles.workspaceGrid}>
          <article className={styles.routePanel}>
            <p className={styles.eyebrow}>Accesos rápidos</p>
            <h3>Todo lo esencial para operar tu negocio</h3>
            <div className={styles.routeList}>
              {quickRoutes.map(([label, href, detail]) => (
                <a key={href} href={href} className={styles.routeRow}>
                  <span>
                    <strong>{label}</strong>
                    <small>{detail}</small>
                  </span>
                  <em>abrir</em>
                </a>
              ))}
            </div>
          </article>

          <article className={styles.evidencePanel}>
            <p className={styles.eyebrow}>PRISMA conectado</p>
            <h3>Más que una tablet</h3>
            <dl>
              {ecosystem.map(([key, value]) => (
                <div key={key}>
                  <dt>{key}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
          </article>
        </section>

        <nav className={styles.bottomDock} aria-label="Navegación principal">
          <a href="/">Inicio</a>
          <a href="/pos">Vender</a>
          <a href="/catalog">Catálogo</a>
          <a href="/sales/today">Ventas</a>
          <a href="/sync">Sync</a>
          <a href="/settings/license">Licencia</a>
        </nav>
      </div>
    </main>
  );
}
