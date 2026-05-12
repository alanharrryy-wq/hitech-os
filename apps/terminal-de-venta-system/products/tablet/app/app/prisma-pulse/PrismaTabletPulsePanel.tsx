"use client";

import { useState } from "react";
import type { PrismaChartFlags, PrismaInsightEnvelope, PrismaTabletChartsViewModel } from "@prisma-charts/prismaChartContracts";
import { formatAgeMinutes, formatPercent } from "@prisma-charts/prismaChartFormatters";
import { TabletShiftPulseStrip } from "./charts/TabletShiftPulseStrip";
import { TabletSyncOutboxStatusMatrix } from "./charts/TabletSyncOutboxStatusMatrix";
import styles from "./prisma-tablet-pulse.module.css";

type PrismaTabletPulsePanelProps = {
  envelope: PrismaInsightEnvelope<PrismaTabletChartsViewModel>;
  flags: PrismaChartFlags;
};

export function PrismaTabletPulsePanel({ envelope, flags }: PrismaTabletPulsePanelProps) {
  const [focusLabel, setFocusLabel] = useState("Toque un bloque para ver foco local");

  if (!flags.enabled) {
    return (
      <main className={styles.shell} data-prisma-charts-surface="tablet" data-prisma-charts-enabled="false">
        <section className={styles.disabledPanel}>
          <p>Tablet opera</p>
          <h1>Pulse preview apagado</h1>
          <span>{flags.reason}</span>
          <strong>Use ?preview=charts para revisar sin afectar ventas locales.</strong>
        </section>
      </main>
    );
  }

  return (
    <main className={styles.shell} data-prisma-charts-surface="tablet" data-prisma-charts-enabled="true">
      <section className={styles.header}>
        <div>
          <p>Tablet opera</p>
          <h1>PRISMA Operations Pulse</h1>
          <span>Dos charts tactiles: seguir vendiendo y revisar outbox local.</span>
        </div>
        <aside>
          <strong>{formatPercent(envelope.confidence.score)}</strong>
          <small>{envelope.quality.sourceLabel}</small>
          <small>TTL {formatAgeMinutes(envelope.freshness.maxStaleMinutes)}</small>
        </aside>
      </section>

      <section className={styles.quickFilters} aria-label="Filtros tactiles Tablet">
        <button type="button">Turno actual</button>
        <button type="button">Solo riesgos</button>
        <button type="button">Pendientes sync</button>
        <button type="button">Reset</button>
      </section>

      <section className={styles.focusPanel} aria-live="polite">
        <span>Foco</span>
        <strong>{focusLabel}</strong>
      </section>

      <section className={styles.grid} aria-label="Dos charts operativos Tablet">
        <TabletShiftPulseStrip data={envelope.data.shiftPulseStrip} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <TabletSyncOutboxStatusMatrix data={envelope.data.syncOutboxStatusMatrix} quality={envelope.quality} onFocusLabel={setFocusLabel} />
      </section>
    </main>
  );
}
