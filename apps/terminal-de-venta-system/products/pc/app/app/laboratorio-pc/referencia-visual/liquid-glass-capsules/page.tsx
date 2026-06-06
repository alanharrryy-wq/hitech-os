import { PrismaGlassCapsule, PrismaGlassTopDock } from '../../../../components/prisma-glass-capsule';
import styles from './liquid-glass-capsules.module.css';

const probeRows = Array.from({ length: 32 }, (_, index) => index + 1);

const sixPills = [
  { label: 'backdrop', tone: 'graphite' as const, variant: 'neutral' as const },
  { label: 'Dark optics', tone: 'rose' as const, variant: 'danger' as const },
  { label: 'Thinking', tone: 'blue' as const, variant: 'thinking' as const },
  { label: 'Lensing', tone: 'violet' as const, variant: 'active' as const },
  { label: 'Color edge', tone: 'adaptive' as const, variant: 'tinted' as const },
  { label: 'No global blue', tone: 'graphite' as const, variant: 'neutral' as const },
];

export default function LiquidGlassCapsulesReferencePage() {
  return (
    <main className={styles.page}>
      <div aria-hidden="true" className={styles.motionBackplate}>
        <div className={styles.fixedGeometryField}>
          <div className={`${styles.geoPair} ${styles.geoPairA}`}><span className={`${styles.geoShape} ${styles.geoCircle} ${styles.red}`} /><span className={`${styles.geoShape} ${styles.geoSquare} ${styles.rose}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairB}`}><span className={`${styles.geoShape} ${styles.geoDot} ${styles.cyan}`} /><span className={`${styles.geoShape} ${styles.geoRect} ${styles.blue}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairC}`}><span className={`${styles.geoShape} ${styles.geoDiamond} ${styles.violet}`} /><span className={`${styles.geoShape} ${styles.geoCapsule} ${styles.magenta}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairD}`}><span className={`${styles.geoShape} ${styles.geoTriangle} ${styles.amber}`} /><span className={`${styles.geoShape} ${styles.geoDot} ${styles.lime}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairE}`}><span className={`${styles.geoShape} ${styles.geoSlash} ${styles.emerald}`} /><span className={`${styles.geoShape} ${styles.geoCircle} ${styles.mint}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairF}`}><span className={`${styles.geoShape} ${styles.geoSquare} ${styles.white}`} /><span className={`${styles.geoShape} ${styles.geoCapsule} ${styles.slate}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairG}`}><span className={`${styles.geoShape} ${styles.geoCircle} ${styles.blue}`} /><span className={`${styles.geoShape} ${styles.geoDiamond} ${styles.cyan}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairH}`}><span className={`${styles.geoShape} ${styles.geoRect} ${styles.rose}`} /><span className={`${styles.geoShape} ${styles.geoTriangle} ${styles.amber}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairI}`}><span className={`${styles.geoShape} ${styles.geoDot} ${styles.lime}`} /><span className={`${styles.geoShape} ${styles.geoCircle} ${styles.magenta}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairJ}`}><span className={`${styles.geoShape} ${styles.geoRect} ${styles.cyan}`} /><span className={`${styles.geoShape} ${styles.geoDot} ${styles.white}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairK}`}><span className={`${styles.geoShape} ${styles.geoSlash} ${styles.magenta}`} /><span className={`${styles.geoShape} ${styles.geoDiamond} ${styles.violet}`} /></div>
          <div className={`${styles.geoPair} ${styles.geoPairL}`}><span className={`${styles.geoShape} ${styles.geoCircle} ${styles.emerald}`} /><span className={`${styles.geoShape} ${styles.geoSquare} ${styles.amber}`} /></div>
          <span className={`${styles.backText} ${styles.backTextMassive} ${styles.backTextPrisma}`}>PRISMA</span>
          <span className={`${styles.backText} ${styles.backTextLarge} ${styles.backTextGlass}`}>GLASS</span>
          <span className={`${styles.backText} ${styles.backTextMassive} ${styles.backTextThinking}`}>THINKING</span>
          <span className={`${styles.backText} ${styles.backTextMedium} ${styles.backTextStatic}`}>STATIC TEXT</span>
          <span className={`${styles.backText} ${styles.backTextSmall} ${styles.backTextDark}`}>DARK BACKDROP</span>
          <span className={`${styles.backText} ${styles.backTextMedium} ${styles.backTextOptic}`}>OPTIC EDGE</span>
          <span className={`${styles.backText} ${styles.backTextSmall} ${styles.backTextRefraction}`}>REFRACTION · LOCAL COLOR · NO GLOBAL BLUE</span>
        </div>
      </div>

      <div className={styles.topDockWrap}>
        <PrismaGlassTopDock status="Thinking" thinking />
      </div>

      <section className={styles.hero}>
        <div className={styles.heroScene}>
          <div className={styles.heroCopy}>
            <p className={styles.kicker}>PRISMA Visual Reference · Dark Liquid Glass Fix7 calibrated</p>
            <h1>Dark glass calibrado: filo más vivo, centro menos oscuro</h1>
            <p>
              Fondo fijo con texto y pares de figuras pequeñas. Las pills deben leer color sólo por proximidad,
              encender una línea fina de 2px más brillante, conservar centro oscuro legible y respirar más largo.
            </p>
          </div>
          <div className={styles.controlledRow}>
            <span aria-hidden="true" className={styles.staticBackCopy}>TEXT BEHIND · COLOR PAIRS · EDGE PICKUP</span>
            <div className={styles.pillLine} aria-label="Fila horizontal de seis cápsulas dark liquid glass">
              {sixPills.map((pill) => (
                <PrismaGlassCapsule key={pill.label} as="div" tone={pill.tone} variant={pill.variant}>
                  {pill.label}
                </PrismaGlassCapsule>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className={styles.visualProof} aria-labelledby="visual-proof-title">
        <p className={styles.kicker}>Visual test</p>
        <h2 id="visual-proof-title">Seis pills sobre pares separados</h2>
        <p>
          Cada par conserva separación menor a un centímetro. Entre pares hay casi cinco centímetros para que no exista
          mezcla falsa. El borde debe encenderse sólo donde cruza color o texto.
        </p>
        <div className={styles.referenceRail}>
          <span aria-hidden="true" className={styles.referenceText}>BUSCAR · THINKING · DARK OPTICS · REFRACTION</span>
          <div className={`${styles.referencePair} ${styles.one}`}><span className={`${styles.geoShape} ${styles.geoCircle} ${styles.red}`} /><span className={`${styles.geoShape} ${styles.geoSquare} ${styles.rose}`} /></div>
          <div className={`${styles.referencePair} ${styles.two}`}><span className={`${styles.geoShape} ${styles.geoDiamond} ${styles.violet}`} /><span className={`${styles.geoShape} ${styles.geoCapsule} ${styles.blue}`} /></div>
          <div className={`${styles.referencePair} ${styles.three}`}><span className={`${styles.geoShape} ${styles.geoTriangle} ${styles.amber}`} /><span className={`${styles.geoShape} ${styles.geoDot} ${styles.lime}`} /></div>
          <div className={styles.referencePills}>
            {sixPills.map((pill) => (
              <PrismaGlassCapsule key={`visual-${pill.label}`} as="div" tone={pill.tone} variant={pill.variant}>
                {pill.label}
              </PrismaGlassCapsule>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.scrollProof} aria-labelledby="scroll-title">
        <h2 id="scroll-title">Scroll proof dark</h2>
        <p>
          El patrón de fondo permanece fijo. Al scrollear, la fila atraviesa texto y figuras; no debe traer color de zonas lejanas.
        </p>
        <div className={styles.scrollLines}>
          {probeRows.map((row) => (
            <p key={row}>Línea óptica #{row}: texto fijo · par de color cercano · cinco centímetros de silencio · pill encima · borde reactivo</p>
          ))}
        </div>
      </section>
    </main>
  );
}
