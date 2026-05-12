"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { OwnerPulsePoint, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { ownerPulseTimelineOption } from "@prisma-charts/prismaChartOptions";
import { MobileChartCard } from "./MobileChartCard";

export function MobileOwnerPulseTimeline({ data, quality, onFocusLabel }: { data: OwnerPulsePoint[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <MobileChartCard title="Owner Pulse Timeline" subtitle="Tendencia de salud y acciones" quality={quality}>
      <PrismaEChart option={ownerPulseTimelineOption(data)} renderer="svg" height={190} label="Owner Pulse Timeline" description="Linea de salud reciente para supervision de owner." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </MobileChartCard>
  );
}
