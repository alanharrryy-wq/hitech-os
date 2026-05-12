"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { DecisionLedgerPoint, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { decisionLedgerTimelineOption } from "@prisma-charts/prismaChartOptions";
import { ChartCard } from "./PcChartCard";

export function PcDecisionLedgerTimeline({ data, quality, onFocusLabel }: { data: DecisionLedgerPoint[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <ChartCard title="Decision Ledger Timeline" kicker="auditoria de decisiones" quality={quality}>
      <PrismaEChart option={decisionLedgerTimelineOption(data)} renderer="canvas" height={280} label="Decision Ledger Timeline" description="Linea temporal auditable de decisiones, incidentes, evidencia y resoluciones." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </ChartCard>
  );
}
