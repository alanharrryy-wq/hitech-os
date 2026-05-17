"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { HealthRadarAxis, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { healthRadarCompactOption } from "@prisma-charts/prismaChartOptions";
import { MobileChartCard } from "./MobileChartCard";

export function MobileHealthRadarCompact({ data, quality, onFocusLabel }: { data: HealthRadarAxis[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <MobileChartCard title="Health Radar Compact" subtitle="Dimensiones detras del estado" quality={quality}>
      <PrismaEChart option={healthRadarCompactOption(data)} renderer="svg" height={220} label="Health Radar Compact" description="Radar compacto de calidad de datos, sync, alertas, inventario, uptime y caja." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </MobileChartCard>
  );
}
