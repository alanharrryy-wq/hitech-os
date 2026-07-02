"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { PrismaChartQuality, ShiftPulseBucket } from "@prisma-charts/prismaChartContracts";
import { shiftPulseStripOption } from "@prisma-charts/prismaChartOptions";
import { TabletChartCard } from "./TabletChartCard";

export function TabletShiftPulseStrip({ data, quality, onFocusLabel }: { data: ShiftPulseBucket[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <TabletChartCard title="Turno actual" subtitle="Ventas, tickets y presion de fila" quality={quality}>
      <PrismaEChart option={shiftPulseStripOption(data)} renderer="svg" height={260} label="Turno actual" description="Lectura de turno para saber si la Tablet puede seguir operando." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </TabletChartCard>
  );
}
