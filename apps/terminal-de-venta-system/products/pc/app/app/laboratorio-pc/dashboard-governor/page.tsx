import type { CSSProperties } from "react";
import styles from "./prisma-surface-dashboard.module.css";

const attentionItems = [
  { label: "Sincronización viva", value: "Actualizado", detail: "Los pulsos recientes se leen como operación viva, no como ruido técnico.", tone: "live" },
  { label: "Inventario bajo control", value: "12 focos", detail: "Se priorizan productos que requieren acción antes de vender o comprar.", tone: "warning" },
  { label: "Caja protegida", value: "Sin cambios POS", detail: "El piloto no toca venta, cobro, checkout ni rutas de POS.", tone: "locked" }
] as const;

const actions = ["Revisar productos críticos primero", "Validar último pulso de tablet", "Abrir evidencia visual antes de promover"];
const evidence = [
  ["Pilot", "04 · PC Dashboard Governed Hoy"],
  ["Route budget", "PC dashboard high / clarity first"],
  ["Atmosphere", "Real assets + readability scrim"],
  ["Material", "G3 hero, G2 cards, G1 details"],
  ["Glow", "1 strong max, semantic only"],
  ["Motion", "Ambient slow, reduced-motion safe"]
];

export const dynamic = "force-static";

export default function DashboardGovernorPage() {
  return (
    <main
      className={styles.dashboardSurface}
      data-prisma-surface-governor="pilot-04"
      data-prisma-panel="pc.laboratorio.pc.dashboard.governor.route"
      data-prisma-surface="pc"
      data-prisma-route="/laboratorio-pc/dashboard-governor"
      data-pos-protected="true"
    >
      <section className={styles.backgroundField} aria-hidden="true" />
      <section className={styles.scrimField} aria-hidden="true" />
      <div className={styles.shell}>
        <header className={styles.topbar}>
          <div className={styles.brandCluster}>
            <span className={styles.brandMark}>P</span>
            <div><p className={styles.eyebrow}>PRISMA PC · LAB</p><h1>Hoy</h1></div>
          </div>
          <div className={styles.statusCluster} aria-label="Estado del piloto visual"><span className={styles.liveDot} /><span>Surface Governor aislado</span></div>
        </header>
        <section className={styles.heroPanel}>
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>Pilot 04 · Dashboard gobernado</p>
            <h2>Tu operación clara primero. Bonita después. Poderosa siempre.</h2>
            <p>Este tablero vive en laboratorio: visual premium, evidencia legible, POS intocable y cero contaminación del dashboard cliente.</p>
            <div className={styles.heroActions}><a href="/laboratorio-pc/referencia-visual" className={styles.primaryAction}>Abrir laboratorio visual</a><a href="/dashboard" className={styles.secondaryAction}>Ver ruta cliente</a></div>
          </div>
          <aside className={styles.governorCard}><span className={styles.cardKicker}>Governor verdict</span><strong>Aislado de cliente</strong><p>Alto impacto visual con claridad, motion lento y glow semántico. Nada de humo pesado.</p></aside>
        </section>
        <section className={styles.grid} aria-label="Lectura rápida de operación">
          {attentionItems.map((item) => <article key={item.label} className={`${styles.kpiCard} ${styles[item.tone]}`}><span>{item.label}</span><strong>{item.value}</strong><p>{item.detail}</p></article>)}
        </section>
        <section className={styles.workArea}>
          <article className={styles.actionPanel}><p className={styles.eyebrow}>Acciones recomendadas</p><h3>Qué atender ahora</h3><ul>{actions.map((action) => <li key={action}>{action}</li>)}</ul></article>
          <article className={styles.chartFrame} aria-label="Vista conceptual de señales">
            <div className={styles.chartHeader}><div><p className={styles.eyebrow}>Señal del día</p><h3>Pulso operativo</h3></div><span>Mock visual seguro</span></div>
            <div className={styles.signalBars} aria-hidden="true">
              {['34%', '58%', '46%', '78%', '62%', '88%', '54%', '70%'].map((height) => <span key={height} style={{ '--h': height } as CSSProperties} />)}
            </div>
          </article>
          <article className={styles.evidencePanel}><p className={styles.eyebrow}>Evidencia técnica</p><h3>Contrato visible</h3><dl>{evidence.map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{value}</dd></div>)}</dl></article>
        </section>
      </div>
    </main>
  );
}
