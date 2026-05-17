"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { FreshnessBeacon, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { freshnessBeaconGridOption } from "@prisma-charts/prismaChartOptions";
import { MobileChartCard } from "./MobileChartCard";

export function MobileFreshnessRings({ data, quality, onFocusLabel }: { data: FreshnessBeacon[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <MobileChartCard title="Freshness Rings" subtitle="Frescura por modulo" quality={quality}>
      <PrismaEChart option={freshnessBeaconGridOption(data)} renderer="svg" height={190} label="Freshness Rings" description="Indicadores compactos de frescura, TTL, fuente y confianza por modulo." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </MobileChartCard>
  );
}
