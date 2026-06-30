"use client";

import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { buildPrismaMobileCommandCenter, type PrismaMobileCommandTone } from "@/lib/prisma-app/prisma-mobile-command-center";
import styles from "./prisma-mobile-dashboard.module.css";

const commandToneClass: Record<PrismaMobileCommandTone, string> = {
  sano: styles.commandToneOk,
  revisar: styles.commandToneReview,
  urgente: styles.commandToneUrgent,
  offline: styles.commandToneOffline
};

const decisionKindLabel = {
  cash: "Caja",
  inventory: "Inventario",
  sync: "Sync",
  sales: "Ventas",
  branch: "Sucursal",
  data: "Datos"
} as const;

function copyMobileText(text: string) {
  if (typeof navigator === "undefined" || !navigator.clipboard) return;
  void navigator.clipboard.writeText(text).catch(() => {});
}

function openMobileTab(tab: "alertas" | "caja") {
  window.dispatchEvent(new CustomEvent(`prisma:open-${tab}`));
}

export function PrismaMobileCommandCenter({ clientSnapshot }: { clientSnapshot: PrismaMobileClientSnapshot }) {
  const command = buildPrismaMobileCommandCenter(clientSnapshot);

  return (
    <section
      className={styles.commandCenter}
      aria-labelledby="prisma-mobile-command-title"
      data-prisma-contract={command.contractId}
      data-prisma-zone="mobile-command-card"
    >
      <header className={styles.commandHeader}>
        <div>
          <span className={styles.commandEyebrow}>Centro de mando móvil</span>
          <h2 id="prisma-mobile-command-title">Decisión rápida del dueño</h2>
          <p>{command.primaryBrief.detail}</p>
        </div>
        <aside className={`${styles.commandScoreCard} ${commandToneClass[command.riskTone]}`} aria-label="Score operativo móvil">
          <span>Listo para decidir</span>
          <strong>{command.readinessScore}%</strong>
          <small>{command.riskLabel}</small>
        </aside>
      </header>

      <div className={styles.commandBriefGrid} aria-label="Orden sugerido de intervención">
        {command.ownerBriefs.map((brief) => (
          <article key={`${brief.title}-${brief.detail}`} className={`${styles.commandBrief} ${commandToneClass[brief.tone]}`}>
            <span>{brief.title}</span>
            <strong>{brief.detail}</strong>
          </article>
        ))}
      </div>

      <div className={styles.commandSignalGrid} aria-label="Señales ejecutivas">
        {command.signals.map((signal) => (
          <article key={signal.label} className={styles.commandSignal}>
            <div>
              <span>{signal.label}</span>
              <strong>{signal.value}</strong>
            </div>
            <p>{signal.detail}</p>
            <i aria-hidden="true"><b style={{ width: `${signal.progress}%` }} /></i>
          </article>
        ))}
      </div>

      <div className={styles.commandDecisionGrid} aria-label="Cola de decisiones móviles">
        <section className={styles.commandQueue} data-prisma-zone="mobile-review-first">
          <header>
            <span>Cola priorizada</span>
            <h3>Qué atender sin abrir PC</h3>
          </header>
          {command.decisionQueue.map((decision) => (
            <article key={decision.id} className={commandToneClass[decision.tone]}>
              <b>{decision.score}</b>
              <div>
                <span>{decisionKindLabel[decision.kind]}</span>
                <strong>{decision.title}</strong>
                <p>{decision.detail}</p>
                <small>{decision.action}</small>
                <div className={styles.actionButtonRow} aria-label={`Acciones para ${decision.title}`}>
                  <button
                    type="button"
                    onClick={() => copyMobileText(`PRISMA · ${decisionKindLabel[decision.kind]} · ${decision.title} · ${decision.detail} · Acción: ${decision.action} · Responsable: ${decision.owner}`)}
                  >
                    Copiar acción
                  </button>
                  <button type="button" onClick={() => openMobileTab(decision.kind === "cash" ? "caja" : "alertas")}>
                    Abrir superficie
                  </button>
                </div>
              </div>
              <em>{decision.owner}</em>
            </article>
          ))}
        </section>

        <aside className={styles.commandDataQuality}>
          <span>Calidad del dato</span>
          <strong>{command.dataQuality.label}</strong>
          <p>{command.dataQuality.detail}</p>
          <small>{command.dataQuality.upstreamTotal > 0 ? `${command.dataQuality.upstreamOk}/${command.dataQuality.upstreamTotal} fuentes disponibles` : "Sin probes reportados"}</small>
          <div>
            <h3>{command.followUp.title}</h3>
            <p>{command.followUp.detail}</p>
            <ul>
              {command.followUp.items.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </div>
        </aside>
      </div>
    </section>
  );
}
