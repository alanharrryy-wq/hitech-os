"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { InventoryRiskNode, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { inventoryRiskTreemapOption } from "@prisma-charts/prismaChartOptions";
import { ChartCard } from "./PcChartCard";

export function PcInventoryRiskTreemap({ data, quality, onFocusLabel }: { data: InventoryRiskNode[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <ChartCard title="Inventory Risk Treemap" kicker="riesgo y dinero" quality={quality}>
      <PrismaEChart option={inventoryRiskTreemapOption(data)} renderer="canvas" height={320} label="Inventory Risk Treemap" description="Treemap de riesgo de inventario y dinero expuesto." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </ChartCard>
  );
}
