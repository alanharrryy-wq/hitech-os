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

const QUICK_FILTERS = [
  { id: "shift", label: "Turno actual", summary: "Vista enfocada en salud del turno y continuidad de venta local." },
  { id: "risks", label: "Solo riesgos", summary: "Filtro de revisión: prioriza alertas y señales de riesgo operativo." },
  { id: "sync", label: "Pendientes", summary: "Filtro de revisión: mira reintentos y pendientes locales de la Tablet." },
  { id: "reset", label: "Todo", summary: "Filtros limpios. Vista completa del estado Tablet." }
] as const;

export function PrismaTabletPulsePanel({ envelope, flags }: PrismaTabletPulsePanelProps) {
  const [focusLabel, setFocusLabel] = useState("Toque un bloque para ver foco local");
  const [activeFilter, setActiveFilter] = useState<(typeof QUICK_FILTERS)[number]["id"]>("reset");

  function applyQuickFilter(filter: (typeof QUICK_FILTERS)[number]) {
    setActiveFilter(filter.id);
    setFocusLabel(filter.summary);
  }

  if (!flags.enabled) {
    return (
      <main className={styles.shell} data-prisma-charts-surface="tablet" data-prisma-charts-enabled="false">
        <section className={styles.disabledPanel}>
          <p>Tablet opera</p>
          <h1>Vista operativa apagada</h1>
          <span>{flags.reason}</span>
          <strong>Activa la vista de graficas solo para revisión autorizada.</strong>
        </section>
      </main>
    );
  }

  return (
    <main className={styles.shell} data-prisma-charts-surface="tablet" data-prisma-charts-enabled="true" data-prisma-hardening="tablet-pulse-filters-260611">
      <section className={styles.header}>
        <div>
          <p>Tablet opera</p>
          <h1>Estado operativo</h1>
          <span>Dos graficas tactiles: seguir vendiendo y revisar pendientes locales.</span>
        </div>
        <aside>
          <strong>{formatPercent(envelope.confidence.score)}</strong>
          <small>{envelope.quality.sourceLabel}</small>
        <small>Vigencia {formatAgeMinutes(envelope.freshness.maxStaleMinutes)}</small>
        </aside>
      </section>

      <section className={styles.quickFilters} aria-label="Filtros tactiles Tablet">
        {QUICK_FILTERS.map((filter) => (
          <button
            key={filter.id}
            type="button"
            aria-pressed={activeFilter === filter.id}
            data-active={activeFilter === filter.id ? "true" : "false"}
            onClick={() => applyQuickFilter(filter)}
          >
            {filter.label}
          </button>
        ))}
      </section>

      <section className={styles.focusPanel} aria-live="polite">
        <span>Foco</span>
        <strong>{focusLabel}</strong>
      </section>

      <section className={styles.grid} aria-label="Dos graficas operativas Tablet">
        <TabletShiftPulseStrip data={envelope.data.shiftPulseStrip} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <TabletSyncOutboxStatusMatrix data={envelope.data.syncOutboxStatusMatrix} quality={envelope.quality} onFocusLabel={setFocusLabel} />
      </section>
    </main>
  );
}
