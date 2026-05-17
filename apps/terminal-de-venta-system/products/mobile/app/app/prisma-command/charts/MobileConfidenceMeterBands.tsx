"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { ConfidenceBand, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { confidenceMeterBandsOption } from "@prisma-charts/prismaChartOptions";
import { MobileChartCard } from "./MobileChartCard";

export function MobileConfidenceMeterBands({ data, quality, onFocusLabel }: { data: ConfidenceBand[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <MobileChartCard title="Confidence Meter Bands" subtitle="Por que confiar o no" quality={quality}>
      <PrismaEChart option={confidenceMeterBandsOption(data)} renderer="svg" height={210} label="Confidence Meter Bands" description="Bandas lineales de confianza por completitud, recencia, consistencia, evidencia y cobertura." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </MobileChartCard>
  );
}
