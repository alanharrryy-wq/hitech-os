export const dynamic = "force-static";

const recipeLinks = [
  ["Materiality Catalog mirror", "/surface-visual-governor/reference-visual/pilot-03/materiality-catalog.registry.json"],
  ["Pilot 02 index", "/surface-visual-governor/reference-visual/pilot-03/recipe-export/index.json"],
  ["Chart recipe", "/surface-visual-governor/reference-visual/pilot-03/recipe-export/chart.recipe.json"],
  ["Visual recipe", "/surface-visual-governor/reference-visual/pilot-03/recipe-export/visual.recipe.json"],
  ["Motion recipe", "/surface-visual-governor/reference-visual/pilot-03/recipe-export/motion.recipe.json"],
  ["Background recipe", "/surface-visual-governor/reference-visual/pilot-03/recipe-export/background.recipe.json"],
  ["Surface compatibility", "/surface-visual-governor/reference-visual/pilot-03/recipe-export/surface.compatibility.json"],
  ["Ultra Codex index", "/surface-visual-governor/reference-visual/pilot-03/recipe-export/ultra-codex.index.json"],
];

const materialCards = [
  {
    eyebrow: "B0-B5",
    title: "Atmosphere Engine",
    copy: "Imagen real + scrim + grain + vignette + drift lento. El fondo vive, pero no se sube a cantar arriba de la tabla.",
  },
  {
    eyebrow: "G2-G4",
    title: "Cloudglass gobernado",
    copy: "Glass premium en paneles importantes, rim selectivo y blur controlado. Nada de leche visual ni antro de LEDs.",
  },
  {
    eyebrow: "N1-N3",
    title: "Glow semántico",
    copy: "El brillo marca foco, estado, acción o riesgo. Si todo brilla, nada importa, así que el cadenero corta la fila.",
  },
  {
    eyebrow: "M0-M3",
    title: "Motion con freno",
    copy: "Microinteracciones y fondo lento con reduced motion respetado. El show no debe marear ni esconder operación.",
  },
];

const gateCards = [
  ["PC", "Permitido", "Referencia visual aislada. No aplica estilos a rutas operativas."],
  ["Tablet", "Light-first", "Sólo se muestra contrato. No se toca Tablet productiva."],
  ["Chart Lab", "Consumidor", "Usa recetas exportadas por Pilot 02 como taller visual."],
  ["POS", "Bloqueado", "Sin dark storm, WebGL, Pixi vapor, blur pesado ni fondos compitiendo con cobro."],
];

const atmosphereAssets = [
  ["Storm cloud real", "/surface-visual-governor/reference-visual/pilot-03/atmosphere-assets/backgrounds/storm-cloud-operations-real.jpg"],
  ["Liquid operations reference", "/surface-visual-governor/reference-visual/pilot-03/atmosphere-assets/backgrounds/liquid-operations-ui-reference.png"],
  ["Soft gray clouds", "/surface-visual-governor/reference-visual/pilot-03/atmosphere-assets/backgrounds/tablet-soft-gray-clouds.svg"],
  ["Aurora slate veil", "/surface-visual-governor/reference-visual/pilot-03/atmosphere-assets/backgrounds/aurora-slate-veil.svg"],
];

export default function ReferenciaVisualPage() {
  return (
    <main className="prismaReferenceVisual" data-pilot="03_pc_referencia_visual">
      <link rel="stylesheet" href="/surface-visual-governor/reference-visual/pilot-03/prisma-pc-reference-visual.css" />
      <section className="prvHero prvGlass prvRim" aria-labelledby="prv-title">
        <div className="prvHeroCopy">
          <p className="prvKicker">PRISMA Surface Visual Governor · Pilot 03</p>
          <h1 id="prv-title">PC Referencia Visual</h1>
          <p className="prvLead">
            Sala de prueba para conectar PC con el Materiality Catalog, validar Cloudglass Executive OS y revisar recetas de Chart Lab sin contaminar rutas operativas.
          </p>
          <div className="prvActionRow" aria-label="Acciones de referencia">
            <a className="prvButton prvButtonPrimary" href="/surface-visual-governor/reference-visual/pilot-03/index.json">Abrir contrato Pilot 03</a>
            <a className="prvButton" href="/surface-visual-governor/reference-visual/pilot-03/materiality-catalog.registry.json">Ver Materiality Catalog</a>
            <a className="prvButton" href="/surface-visual-governor/reference-visual/pilot-03/recipe-export/index.json">Ver recetas Chart Lab</a>
          </div>
        </div>
        <aside className="prvStatusCard" aria-label="Estado del piloto">
          <span className="prvLiveDot" aria-hidden="true" />
          <strong>PASS-ready contract</strong>
          <span>Ruta aislada: /referencia-visual</span>
          <span>DB: no touch · Deploy: no touch</span>
          <span>POS: protegido hasta gate final</span>
        </aside>
      </section>

      <section className="prvGrid prvGridFour" aria-label="Capas visuales">
        {materialCards.map((card) => (
          <article className="prvGlass prvCard" key={card.title}>
            <span className="prvEyebrow">{card.eyebrow}</span>
            <h2>{card.title}</h2>
            <p>{card.copy}</p>
          </article>
        ))}
      </section>

      <section className="prvSplit" aria-label="Contrato y compatibilidad">
        <article className="prvGlass prvPanel">
          <span className="prvEyebrow">Surface Twin</span>
          <h2>PC consume, no improvisa</h2>
          <p>
            Esta pantalla funciona como espejo controlado: toma el catálogo visual instalado en Tablet Visual OS, las recetas exportadas por Chart Lab y las muestra como contrato verificable para PC.
          </p>
          <div className="prvBudget" role="list" aria-label="Presupuesto visual PC referencia">
            <span role="listitem">background: 0.55</span>
            <span role="listitem">glass: medium</span>
            <span role="listitem">rim: signature only</span>
            <span role="listitem">glow: 1 strong / 3 medium</span>
            <span role="listitem">motion: reduced-motion compliant</span>
          </div>
        </article>
        <article className="prvGlass prvPanel prvPanelQuiet">
          <span className="prvEyebrow">Governor Gates</span>
          <h2>Qué puede pasar y qué ni madres</h2>
          <div className="prvGateList">
            {gateCards.map(([surface, state, note]) => (
              <div className="prvGate" key={surface}>
                <strong>{surface}</strong>
                <span>{state}</span>
                <p>{note}</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="prvSplit" aria-label="Assets y recetas">
        <article className="prvGlass prvPanel">
          <span className="prvEyebrow">Atmosphere assets</span>
          <h2>Imágenes reales como motor</h2>
          <p>Estos assets se copian a PC como referencia visual gobernada. No son decoración suelta: son insumo del Atmosphere Engine.</p>
          <div className="prvAssetWall">
            {atmosphereAssets.map(([label, href]) => (
              <a className="prvAsset" href={href} key={href}>
                <span>{label}</span>
              </a>
            ))}
          </div>
        </article>
        <article className="prvGlass prvPanel">
          <span className="prvEyebrow">Recipe export</span>
          <h2>Chart Lab deja la receta servida</h2>
          <p>Los JSON de Pilot 02 quedan disponibles para inspección directa desde PC. La técnica vive abierta para QA, no escondida debajo del tapete.</p>
          <ul className="prvLinks">
            {recipeLinks.map(([label, href]) => (
              <li key={href}><a href={href}>{label}</a></li>
            ))}
          </ul>
        </article>
      </section>

      <section className="prvGlass prvPanel prvEvidence" aria-label="Evidencia técnica">
        <span className="prvEyebrow">Evidencia técnica colapsable por diseño futuro</span>
        <h2>Contrato de seguridad</h2>
        <p>
          Pilot 03 sólo escribe en PC /referencia-visual, public reference assets, docs y verifier. No modifica POS, checkout, package.json, lockfiles, bases de datos ni deploy. Si algo truena, rollback automático y evidencia en <OUTPUT_DIR>.
        </p>
        <code>La galería es laboratorio · el Materiality Catalog es contrato · Chart Lab es taller · PC ahora es sala · POS se toca al final.</code>
      </section>
    </main>
  );
}
