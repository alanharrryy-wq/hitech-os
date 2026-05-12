"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { CausalFlowRibbonDatum, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { causalFlowRibbonOption } from "@prisma-charts/prismaChartOptions";
import { ChartCard } from "./PcChartCard";

export function PcCausalFlowRibbon({ data, quality, onFocusLabel }: { data: CausalFlowRibbonDatum[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <ChartCard title="Causal Flow Ribbon" kicker="causa - efecto - accion" quality={quality} wide>
      <PrismaEChart option={causalFlowRibbonOption(data)} renderer="canvas" height={360} label="Causal Flow Ribbon" description="Ribbon de causa, efecto y destino de accion." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </ChartCard>
  );
}
