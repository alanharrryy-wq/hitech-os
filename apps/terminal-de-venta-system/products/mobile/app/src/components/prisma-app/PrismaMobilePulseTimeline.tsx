"use client";

import { useMemo } from "react";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { buildPrismaMobilePulseTimeline } from "@/lib/prisma-app/prisma-mobile-pulse-timeline";
import styles from "./prisma-mobile-dashboard.module.css";

type Props = {
  clientSnapshot: PrismaMobileClientSnapshot;
};

export function PrismaMobilePulseTimeline({ clientSnapshot }: Props) {
  const timeline = useMemo(() => buildPrismaMobilePulseTimeline(clientSnapshot), [clientSnapshot]);
  return (
    <section className={styles.pulseTimeline} aria-label="Timeline móvil de pulso operativo">
      <header className={styles.pulseTimelineHeader}>
        <div>
          <p className={styles.eyebrow}>PRISMA App · Pulso del día</p>
          <h2>{timeline.headline}</h2>
          <p>{timeline.subheadline}</p>
        </div>
        <aside className={styles.pulseTimelineCheckpoint} data-tone={timeline.nowCheckpoint.tone}>
          <span>{timeline.nowCheckpoint.label}</span>
          <strong>{timeline.nowCheckpoint.title}</strong>
          <small>{timeline.nowCheckpoint.detail}</small>
        </aside>
      </header>

      <div className={styles.pulseTimelineNarrative} aria-label="Narrativa operativa del día">
        {timeline.ownerNarrative.map((line) => <p key={line}>{line}</p>)}
      </div>

      <div className={styles.pulseTimelineCardGrid} aria-label="Indicadores del pulso móvil">
        {timeline.cards.map((card) => (
          <article key={card.label} data-tone={card.tone}>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
            <small>{card.detail}</small>
          </article>
        ))}
      </div>

      <div className={styles.pulseTimelineChecklist}>
        <span>Checklist inmediato</span>
        <ul>{timeline.nowCheckpoint.checklist.map((item) => <li key={item}>{item}</li>)}</ul>
      </div>

      <div className={styles.pulseTimelineRail} aria-label="Eventos ordenados por fase">
        {timeline.events.map((event) => (
          <article key={event.id} data-phase={event.phase} data-tone={event.tone}>
            <div className={styles.pulseTimelineMarker} aria-hidden="true">
              <i />
              <span>{event.sequence.toString().padStart(2, "0")}</span>
            </div>
            <div className={styles.pulseTimelineEventBody}>
              <span>{event.phase} · {event.timeLabel} · {event.source}</span>
              <h3>{event.title}</h3>
              <p>{event.detail}</p>
              <ul>{event.evidence.map((item) => <li key={item}>{item}</li>)}</ul>
            </div>
            <aside className={styles.pulseTimelineEventMeta}>
              <em>{event.owner}</em>
              <strong>{event.nextCheck}</strong>
              <small>score {event.priorityScore}</small>
            </aside>
          </article>
        ))}
      </div>

      <details className={styles.pulseTimelineExport}>
        <summary>Ver texto de timeline para seguimiento</summary>
        <pre>{timeline.exportText}</pre>
      </details>
    </section>
  );
}
