"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { PrismaChartQuality, SyncOutboxMatrixCell } from "@prisma-charts/prismaChartContracts";
import { syncOutboxMatrixOption } from "@prisma-charts/prismaChartOptions";
import { TabletChartCard } from "./TabletChartCard";

export function TabletSyncOutboxStatusMatrix({ data, quality, onFocusLabel }: { data: SyncOutboxMatrixCell[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <TabletChartCard title="Sync Outbox Status Matrix" subtitle="Pendiente, reintento y bloqueo local" quality={quality}>
      <PrismaEChart option={syncOutboxMatrixOption(data)} renderer="svg" height={260} label="Sync Outbox Status Matrix" description="Matriz de outbox local para ver pendientes, fallidos y reintentos." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </TabletChartCard>
  );
}
