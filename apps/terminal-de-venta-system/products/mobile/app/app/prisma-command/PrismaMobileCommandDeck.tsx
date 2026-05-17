"use client";

import { useState } from "react";
import type { PrismaChartFlags, PrismaInsightEnvelope, PrismaMobileChartsViewModel } from "@prisma-charts/prismaChartContracts";
import { formatAgeMinutes, formatPercent } from "@prisma-charts/prismaChartFormatters";
import { MobileActionInboxPriorityStack } from "./charts/MobileActionInboxPriorityStack";
import { MobileConfidenceMeterBands } from "./charts/MobileConfidenceMeterBands";
import { MobileFreshnessRings } from "./charts/MobileFreshnessRings";
import { MobileHealthRadarCompact } from "./charts/MobileHealthRadarCompact";
import { MobileIncidentSparkCards } from "./charts/MobileIncidentSparkCards";
import { MobileOwnerPulseTimeline } from "./charts/MobileOwnerPulseTimeline";
import styles from "./prisma-mobile-command.module.css";

type PrismaMobileCommandDeckProps = {
  envelope: PrismaInsightEnvelope<PrismaMobileChartsViewModel>;
  flags: PrismaChartFlags;
};

export function PrismaMobileCommandDeck({ envelope, flags }: PrismaMobileCommandDeckProps) {
  const [focusLabel, setFocusLabel] = useState("Toque un chart para ampliar resumen");

  if (!flags.enabled) {
    return (
      <main className={styles.shell} data-prisma-charts-surface="mobile" data-prisma-charts-enabled="false">
        <section className={styles.disabledPanel}>
          <p>Mobile supervisa</p>
          <h1>Command preview apagado</h1>
          <span>{flags.reason}</span>
          <strong>Use ?preview=charts para ver el pack sin activar flags de produccion.</strong>
        </section>
      </main>
    );
  }

  return (
    <main className={styles.shell} data-prisma-charts-surface="mobile" data-prisma-charts-enabled="true">
      <section className={styles.header}>
        <p>Mobile supervisa</p>
        <h1>Owner Command</h1>
        <span>Seis modulos compactos para salud, acciones, frescura, incidentes y confianza. No muta ventas, caja ni inventario.</span>
        <div className={styles.signalRow} aria-label="Estado de datos mobile">
          <strong>{formatPercent(envelope.confidence.score)} confianza</strong>
          <small>{envelope.quality.sourceLabel}</small>
          <small>TTL {formatAgeMinutes(envelope.freshness.maxStaleMinutes)}</small>
        </div>
      </section>

      <section className={styles.filterRail} aria-label="Filtros Mobile">
        <button type="button">24h</button>
        <button type="button">Prioridad alta</button>
        <button type="button">Datos stale</button>
        <button type="button">Reset</button>
      </section>

      <section className={styles.focusPanel} aria-live="polite">
        <span>Foco owner</span>
        <strong>{focusLabel}</strong>
      </section>

      <section className={styles.grid} aria-label="Seis charts de supervision Mobile">
        <MobileOwnerPulseTimeline data={envelope.data.ownerPulseTimeline} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <MobileActionInboxPriorityStack data={envelope.data.actionInboxPriorityStack} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <MobileHealthRadarCompact data={envelope.data.healthRadarCompact} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <MobileFreshnessRings data={envelope.data.freshnessBeaconGrid} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <MobileIncidentSparkCards data={envelope.data.incidentSparkCards} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <MobileConfidenceMeterBands data={envelope.data.confidenceMeterBands} quality={envelope.quality} onFocusLabel={setFocusLabel} />
      </section>
    </main>
  );
}
