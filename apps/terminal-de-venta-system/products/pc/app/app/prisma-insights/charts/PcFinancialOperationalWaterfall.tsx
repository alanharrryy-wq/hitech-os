"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { OperationalWaterfallStep, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { financialOperationalWaterfallOption } from "@prisma-charts/prismaChartOptions";
import { ChartCard } from "./PcChartCard";

export function PcFinancialOperationalWaterfall({ data, quality, onFocusLabel }: { data: OperationalWaterfallStep[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <ChartCard title="Financial / Operational Waterfall" kicker="impacto operativo" quality={quality}>
      <PrismaEChart option={financialOperationalWaterfallOption(data)} renderer="canvas" height={280} label="Financial Operational Waterfall" description="Waterfall que conecta decisiones y operacion con impacto financiero." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </ChartCard>
  );
}
