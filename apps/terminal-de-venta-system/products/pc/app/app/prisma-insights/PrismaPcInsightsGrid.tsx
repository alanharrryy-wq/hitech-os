"use client";

import { useMemo, useState } from "react";
import type { PrismaChartFlags, PrismaInsightEnvelope, PrismaPcChartsViewModel } from "@prisma-charts/prismaChartContracts";
import { chartsForSurface } from "@prisma-charts/prismaChartRegistry";
import { formatAgeMinutes, formatPercent } from "@prisma-charts/prismaChartFormatters";
import { PcCausalFlowRibbon } from "./charts/PcCausalFlowRibbon";
import { PcDecisionLedgerTimeline } from "./charts/PcDecisionLedgerTimeline";
import { PcFinancialOperationalWaterfall } from "./charts/PcFinancialOperationalWaterfall";
import { PcInventoryRiskTreemap } from "./charts/PcInventoryRiskTreemap";
import { PcOperationalDensityField } from "./charts/PcOperationalDensityField";
import { PcServiceDependencyGraph } from "./charts/PcServiceDependencyGraph";
import styles from "./prisma-pc-insights.module.css";

type PrismaPcInsightsGridProps = {
  envelope: PrismaInsightEnvelope<PrismaPcChartsViewModel>;
  flags: PrismaChartFlags;
};

export function PrismaPcInsightsGrid({ envelope, flags }: PrismaPcInsightsGridProps) {
  const [focusLabel, setFocusLabel] = useState("Sin foco seleccionado");
  const charts = useMemo(() => chartsForSurface("pc"), []);

  if (!flags.enabled) {
    return (
      <main className={styles.shell} data-prisma-charts-surface="pc" data-prisma-charts-enabled="false">
        <section className={styles.disabledPanel}>
          <p className={styles.eyebrow}>PRISMA Insights</p>
          <h1>Chart pack preview apagado</h1>
          <p>{flags.reason}</p>
          <span>Activacion segura: agregar <strong>?preview=charts</strong> a esta ruta o usar flags PRISMA_CHARTS_ENABLED y PRISMA_CHARTS_PC.</span>
        </section>
      </main>
    );
  }

  return (
    <main className={styles.shell} data-prisma-charts-surface="pc" data-prisma-charts-enabled="true">
      <section className={styles.hero}>
        <div>
          <p className={styles.eyebrow}>PC gobierna</p>
          <h1>PRISMA Backoffice Insights</h1>
          <p>Seis modulos de analisis para validar causas, dependencias, inventario, decisiones y dinero operativo sin convertir PC en POS.</p>
        </div>
        <aside className={styles.telemetry} aria-label="Calidad de datos de los charts PC">
          <span>{envelope.quality.sourceLabel}</span>
          <strong>{formatPercent(envelope.confidence.score)} confianza</strong>
          <small>{formatAgeMinutes(envelope.freshness.maxStaleMinutes)} TTL - {envelope.quality.emptyState}</small>
        </aside>
      </section>

      <section className={styles.toolbar} aria-label="Filtros preview PC">
        {charts[0]?.filters.map((filter) => (
          <div className={styles.filterGroup} key={filter.id}>
            <span>{filter.label}</span>
            <div>
              {filter.values.slice(0, 4).map((value) => (
                <button type="button" key={value}>{value}</button>
              ))}
            </div>
          </div>
        ))}
        <button className={styles.resetButton} type="button">Reset</button>
      </section>

      <section className={styles.focusPanel} aria-live="polite">
        <span>Foco local</span>
        <strong>{focusLabel}</strong>
      </section>

      <section className={styles.grid} aria-label="Seis charts de gobernanza PC">
        <PcCausalFlowRibbon data={envelope.data.causalFlowRibbon} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <PcOperationalDensityField data={envelope.data.operationalDensityField} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <PcServiceDependencyGraph data={envelope.data.serviceDependencyGraph} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <PcInventoryRiskTreemap data={envelope.data.inventoryRiskTreemap} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <PcDecisionLedgerTimeline data={envelope.data.decisionLedgerTimeline} quality={envelope.quality} onFocusLabel={setFocusLabel} />
        <PcFinancialOperationalWaterfall data={envelope.data.financialOperationalWaterfall} quality={envelope.quality} onFocusLabel={setFocusLabel} />
      </section>
    </main>
  );
}
