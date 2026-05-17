"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { ActionPriorityStackDatum, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { actionInboxPriorityStackOption } from "@prisma-charts/prismaChartOptions";
import { MobileChartCard } from "./MobileChartCard";

export function MobileActionInboxPriorityStack({ data, quality, onFocusLabel }: { data: ActionPriorityStackDatum[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <MobileChartCard title="Action Inbox Priority Stack" subtitle="Carga por responsable" quality={quality}>
      <PrismaEChart option={actionInboxPriorityStackOption(data)} renderer="svg" height={210} label="Action Inbox Priority Stack" description="Barras apiladas de acciones abiertas, vencidas, bloqueadas y sin evidencia." empty={data.length === 0} onFocusLabel={onFocusLabel} />
    </MobileChartCard>
  );
}
