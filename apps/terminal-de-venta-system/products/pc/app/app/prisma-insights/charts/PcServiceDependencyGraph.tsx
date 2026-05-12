"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { PrismaChartQuality, ServiceDependencyEdge, ServiceDependencyNode } from "@prisma-charts/prismaChartContracts";
import { serviceDependencyGraphOption } from "@prisma-charts/prismaChartOptions";
import { ChartCard } from "./PcChartCard";

export function PcServiceDependencyGraph({ data, quality, onFocusLabel }: { data: { nodes: ServiceDependencyNode[]; edges: ServiceDependencyEdge[] }; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <ChartCard title="Service Dependency Graph" kicker="servicios y rutas" quality={quality}>
      <PrismaEChart option={serviceDependencyGraphOption(data)} renderer="canvas" height={320} label="Service Dependency Graph" description="Grafo de dependencias entre apps, servicios, endpoints y DB." empty={data.nodes.length === 0} onFocusLabel={onFocusLabel} />
    </ChartCard>
  );
}
