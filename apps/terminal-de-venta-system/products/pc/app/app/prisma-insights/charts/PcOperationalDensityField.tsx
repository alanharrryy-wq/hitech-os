"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { OperationalDensityCell, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { operationalDensityFieldOption } from "@prisma-charts/prismaChartOptions";
import { ChartCard } from "./PcChartCard";

export function PcOperationalDensityField({ data, quality, onFocusLabel }: { data: OperationalDensityCell[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <ChartCard title="Operational Density Field" kicker="presion por modulo" quality={quality}>
      <PrismaEChart option={operationalDensityFieldOption(data)} renderer="canvas" height={320} label="Operational Density Field" description="Mapa de calor de presion operativa por modulo y tiempo." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </ChartCard>
  );
}
