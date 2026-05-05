import type { CSSProperties } from "react";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { buildPrismaMobileHealthRadar } from "@/lib/prisma-app/prisma-mobile-health-radar";
import styles from "./prisma-mobile-dashboard.module.css";

type Props = {
  clientSnapshot: PrismaMobileClientSnapshot;
};

const toneLabel = {
  sano: "Sano",
  revisar: "Revisar",
  urgente: "Urgente",
  offline: "Offline",
};

const trendLabel = {
  subiendo: "subiendo",
  estable: "estable",
  bajando: "bajando",
};

function scoreStyle(score: number): CSSProperties {
  return { "--radar-score": `${score}%` } as CSSProperties;
}

function stableKey(scope: string, index: number, value: string): string {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9áéíóúñü]+/gi, "-")
    .replace(/^-|-$/g, "");

  return `${scope}-${index}-${normalized || "item"}`;
}

export function PrismaMobileHealthRadar({ clientSnapshot }: Props) {
  const radar = buildPrismaMobileHealthRadar(clientSnapshot);

  return (
    <section
      className={styles.healthRadarPanel}
      aria-labelledby="prisma-mobile-health-radar-title"
      data-radar-tone={radar.tone}
    >
      <div className={styles.healthRadarHeader}>
        <div>
          <p className={styles.sectionEyebrow}>Radar de salud operativa</p>
          <h2 id="prisma-mobile-health-radar-title">{radar.healthLabel}</h2>
          <p>{radar.ownerSummary}</p>
        </div>
        <div
          className={styles.healthRadarScore}
          style={scoreStyle(radar.healthScore)}
          aria-label={`Salud operativa ${radar.healthScore} de 100`}
        >
          <span>{radar.healthScore}</span>
          <small>/100</small>
        </div>
      </div>

      <div className={styles.healthRadarAxes} aria-label="Áreas de salud operativa">
        {radar.axes.map((axis) => (
          <article key={axis.id} className={styles.healthRadarAxis} data-axis-tone={axis.tone}>
            <div>
              <span>{axis.label}</span>
              <strong>{axis.score}/100</strong>
            </div>
            <div className={styles.healthRadarTrack} aria-hidden="true">
              <i style={scoreStyle(axis.score)} />
            </div>
            <p>{axis.headline}</p>
            <small>{axis.detail}</small>
            <ul>
              {axis.evidence.length > 0 ? (
                axis.evidence
                  .slice(0, 2)
                  .map((item, index) => <li key={stableKey(`${axis.id}-evidence`, index, item)}>{item}</li>)
              ) : (
                <li key={`${axis.id}-evidence-empty`}>Sin evidencia delicada.</li>
              )}
            </ul>
            <em>
              {toneLabel[axis.tone]} · {trendLabel[axis.trend]}
            </em>
          </article>
        ))}
      </div>

      <div className={styles.healthRadarBottom}>
        <div className={styles.healthRadarWatchlist}>
          <h3>Vigilancia prioritaria</h3>
          {radar.watchlist.slice(0, 5).map((item, index) => (
            <article key={stableKey("watch", index, item.id)} data-watch-tone={item.tone}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
        <div className={styles.healthRadarGuardrails}>
          <h3>Reglas de cierre</h3>
          <ul>
            {radar.guardrails.map((item, index) => (
              <li key={stableKey("guardrail", index, item)}>{item}</li>
            ))}
          </ul>
          <p>
            <strong>Siguiente revisión:</strong> {radar.nextReview}
          </p>
        </div>
      </div>
    </section>
  );
}
