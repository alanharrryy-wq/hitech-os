import { PrismaGlassCapsule, PrismaGlassTopDock } from '../../components/prisma-glass-capsule';
import styles from './liquid-glass-capsules.module.css';

export default function LiquidGlassCapsulesReferencePage() {
  return (
    <main className={styles.page}>
      <PrismaGlassTopDock status="Thinking" thinking />
      <section className={styles.hero}>
        <div className={styles.messageCard}>
          <p className={styles.kicker}>PRISMA Visual Reference</p>
          <h1>Liquid Glass upper capsules</h1>
          <p>
            Sistema de óvalos flotantes con blur, tinte contextual, borde especular,
            sombra interna y estado vivo. Esto reproduce la intención visual de las
            cápsulas superiores vistas en las capturas: controles flotantes que no son
            tarjetas planas, sino material óptico encima del contenido.
          </p>
        </div>
      </section>
      <section className={styles.testGrid} aria-label="Pruebas de estados visuales">
        <article className={styles.panelRose}>
          <h2>Contenido detrás</h2>
          <p>Mueve scroll y revisa cómo las cápsulas conservan legibilidad mientras el fondo atmosférico queda difuminado debajo del material.</p>
          <div className={styles.sampleRow}>
            <PrismaGlassCapsule shape="circle" tone="graphite" aria-label="Menú demo"><span className={styles.demoGlyph}>≡</span></PrismaGlassCapsule>
            <PrismaGlassCapsule as="div" variant="thinking" tone="blue">Thinking</PrismaGlassCapsule>
            <PrismaGlassCapsule as="div" tone="rose">Editar · Más</PrismaGlassCapsule>
          </div>
        </article>
        <article className={styles.panelLight}>
          <h2>Superficie clara</h2>
          <p>Incluye fallback sin backdrop-filter, soporte reduced motion y tokens por tono para neutral, rose, violet, blue y adaptive.</p>
          <div className={styles.sampleRow}>
            <PrismaGlassCapsule as="div" tone="adaptive">Adaptive</PrismaGlassCapsule>
            <PrismaGlassCapsule as="div" variant="active" tone="violet">Active</PrismaGlassCapsule>
            <PrismaGlassCapsule as="div" variant="danger">Danger</PrismaGlassCapsule>
          </div>
        </article>
      </section>
      <section className={styles.scrollProof}>
        {Array.from({ length: 8 }).map((_, index) => (
          <p key={index}>Línea de prueba #{index + 1}: texto pasando por debajo del dock para validar refracción, contraste, profundidad, borde y sombra. Si esto se ve plano, todavía no está cabrón; si parece vidrio con intención, vamos ganando.</p>
        ))}
      </section>
    </main>
  );
}
