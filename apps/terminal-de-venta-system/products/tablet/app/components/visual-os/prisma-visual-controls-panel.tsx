import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import styles from "./prisma-visual-controls-panel.module.css";

const controls = [
  { label: "Glass", value: 76, layer: "surface", note: "frost premium sin tapar datos" },
  { label: "Glow", value: 42, layer: "atmosphere", note: "haze elegante, no feria de neón" },
  { label: "Depth", value: 78, layer: "surface", note: "cards con separación real" },
  { label: "Density", value: 44, layer: "content", note: "POS respirable para touch" },
  { label: "Contrast", value: 84, layer: "content", note: "precios y stock mandan" },
  { label: "Action", value: 95, layer: "action", note: "COBRAR no pide permiso" },
  { label: "State", value: 86, layer: "state", note: "error/offline visibles" },
  { label: "Touch", value: 94, layer: "focus", note: "dedos humanos, no agujas" }
];

const layerOrder = ["background", "atmosphere", "shell", "surface", "content", "action", "state", "focus", "overlay", "debug"];

export function PrismaVisualControlsPanel() {
  return (
    <PrismaTabletShellUnified
      currentPath="/visual-os"
      title="Visual OS"
      subtitle="Panel interno para revisar perillas, capas y gobierno visual de Tablet."
      kicker="PRISMA calibración"
      status={<TabletShellStatusPill tone="ok">Runtime 00E</TabletShellStatusPill>}
      visualSurface="tablet-shell"
      visualPreset="POS_TOUCH_REFERENCE"
    >
      <section className={styles.panel} data-prisma-vos-runtime="00E" data-prisma-vsurface="tablet-shell" data-prisma-layer="surface">
        <div className={styles.heroCard}>
          <span>Preset activo</span>
          <strong>POS_TOUCH_REFERENCE</strong>
          <p>Vista de calibración. El archivo fuente vive en <code>config/prisma-visual-os/prisma-visual-controls.active.json</code>.</p>
        </div>
        <div className={styles.controlGrid}>
          {controls.map((control) => (
            <article className={styles.controlCard} key={control.label} data-prisma-layer={control.layer}>
              <div>
                <span>{control.layer}</span>
                <strong>{control.label}</strong>
                <p>{control.note}</p>
              </div>
              <meter min="0" max="100" value={control.value} aria-label={`${control.label}: ${control.value}`} />
              <b>{control.value}</b>
            </article>
          ))}
        </div>
        <section className={styles.layerMap} aria-label="Mapa de capas visuales">
          <h2>Mapa de capas</h2>
          <ol>
            {layerOrder.map((layer, index) => (
              <li key={layer}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <strong>{layer}</strong>
              </li>
            ))}
          </ol>
        </section>
      </section>
    </PrismaTabletShellUnified>
  );
}
