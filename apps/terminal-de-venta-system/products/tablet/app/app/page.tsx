import styles from './prisma-tablet-light-shell.module.css';

const attentionCards = [
  {
    label: 'Operación táctil',
    value: 'Light-first',
    detail: 'Superficie clara, botones grandes y contraste suave para trabajo de tablet.',
    tone: 'live',
  },
  {
    label: 'Sync y evidencia',
    value: 'Visible',
    detail: 'El shell deja estado y rutas seguras a la mano sin abrir el POS.',
    tone: 'info',
  },
  {
    label: 'Caja protegida',
    value: 'POS cerrado',
    detail: 'Este piloto no toca venta, cobro, checkout ni componentes de POS.',
    tone: 'locked',
  },
];

const safeRoutes = [
  ['Visual OS', '/visual-os', 'Museo visual y rutas de laboratorio.'],
  ['Materiality Catalog', '/visual-os/materiality-catalog', 'Contrato visual instalado en Pilot 01.'],
  ['Inventario', '/inventory', 'Ruta operativa segura para validar claridad.'],
  ['Sincronización', '/sync', 'Estado vivo sin efectos pesados.'],
  ['Licencia', '/settings/license', 'Pantalla de sistema con bajo ruido visual.'],
];

const evidence = [
  ['Pilot', '05 · Tablet Light Shell'],
  ['Surface', 'Tablet productiva light-first'],
  ['Background', 'Tablet Light Cloudglass + Atmosphere Engine'],
  ['Motion', 'Micro only / reduced-motion safe'],
  ['Forbidden', 'POS, checkout, WebGL, Pixi vapor, dark storm'],
  ['Output', '<LOCAL_PATH> result ZIP'],
];

export default function TabletHomePage() {
  return (
    <main
      className={styles.tabletShell}
      data-prisma-surface-governor="pilot-05"
      data-prisma-surface="tablet-light-shell"
      data-tablet-light-first="true"
      data-pos-protected="true"
    >
      <section className={styles.atmosphere} aria-hidden="true" />
      <section className={styles.lightScrim} aria-hidden="true" />

      <div className={styles.frame}>
        <header className={styles.chromeBar}>
          <div className={styles.brandCluster}>
            <span className={styles.brandMark}>P</span>
            <div>
              <p className={styles.eyebrow}>PRISMA Tablet</p>
              <h1>Inicio operativo</h1>
            </div>
          </div>
          <div className={styles.guardrailPill} aria-label="Estado del piloto visual">
            <span className={styles.liveDot} />
            <span>Light Shell activo</span>
          </div>
        </header>

        <section className={styles.heroPanel}>
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>Pilot 05 · Tablet productiva</p>
            <h2>La tablet se vuelve luminosa, táctil y gobernada.</h2>
            <p>
              Este shell traslada tokens y variants seguros a la superficie Tablet sin abrir la caja registradora.
              El fondo respira con imágenes reales, pero el trabajo sigue mandando: lectura primero, acción después, show al final.
            </p>
            <div className={styles.heroActions}>
              <a className={styles.primaryAction} href="/visual-os/materiality-catalog">Abrir Materiality Catalog</a>
              <a className={styles.secondaryAction} href="/sync">Revisar sincronización</a>
            </div>
          </div>

          <aside className={styles.protectionCard}>
            <span className={styles.cardKicker}>Governor verdict</span>
            <strong>Tablet light-first aprobado</strong>
            <p>No dark storm, no vapor pesado, no WebGL, no POS.</p>
          </aside>
        </section>

        <section className={styles.cardGrid} aria-label="Resumen operativo">
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
            <p className={styles.eyebrow}>Rutas seguras</p>
            <h3>Validar shell sin tocar cobro</h3>
            <div className={styles.routeList}>
              {safeRoutes.map(([label, href, detail]) => (
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
            <p className={styles.eyebrow}>Evidencia técnica</p>
            <h3>Contrato del piloto</h3>
            <dl>
              {evidence.map(([key, value]) => (
                <div key={key}>
                  <dt>{key}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
          </article>
        </section>
      </div>
    </main>
  );
}
