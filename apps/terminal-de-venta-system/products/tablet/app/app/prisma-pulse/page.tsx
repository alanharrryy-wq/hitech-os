import type { PrismaTabletChartsViewModel } from "@prisma-charts/prismaChartContracts";
import { buildPrismaInsightEnvelope, buildPrismaTripleAppChartsViewModel } from "@prisma-charts/prismaChartAdapters";
import { resolvePrismaChartFlags } from "@prisma-charts/prismaChartFlags";
import { buildPendingOfflineSyncPanel } from "@/server/pos-sync-panel";
import { getTabletRuntimeSnapshot, readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot";
import { PrismaTabletPulsePanel } from "./PrismaTabletPulsePanel";

type SearchParams = Record<string, string | string[] | undefined>;

export const dynamic = "force-dynamic";

export const metadata = {
  title: "PRISMA Pulse - Tablet Operations",
  description: "Preview operativo de Tablet con dos charts touch-first."
};

function toUrlSearchParams(searchParams: SearchParams) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(searchParams)) {
    if (Array.isArray(value)) {
      for (const item of value) params.append(key, item);
    } else if (typeof value === "string") {
      params.set(key, value);
    }
  }
  return params;
}

export default async function PrismaPulsePage({ searchParams }: { searchParams?: Promise<SearchParams> | SearchParams }) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const flags = resolvePrismaChartFlags("tablet", resolvedSearchParams);
  const input = readRuntimeSnapshotInput(toUrlSearchParams(resolvedSearchParams));
  const errors: string[] = [];
  const [runtimeResult, syncPanelResult] = await Promise.allSettled([
    getTabletRuntimeSnapshot(input),
    buildPendingOfflineSyncPanel({ businessId: input.businessId, limit: 200 })
  ]);
  if (runtimeResult.status === "rejected") errors.push(`Tablet runtime unavailable: ${runtimeResult.reason instanceof Error ? runtimeResult.reason.message : String(runtimeResult.reason)}`);
  if (syncPanelResult.status === "rejected") errors.push(`Tablet sync panel unavailable: ${syncPanelResult.reason instanceof Error ? syncPanelResult.reason.message : String(syncPanelResult.reason)}`);
  const model = buildPrismaTripleAppChartsViewModel({
    tablet: {
      runtime: runtimeResult.status === "fulfilled" ? runtimeResult.value : null,
      syncPanel: syncPanelResult.status === "fulfilled" ? syncPanelResult.value : null,
      errors
    }
  });
  const envelope = buildPrismaInsightEnvelope<PrismaTabletChartsViewModel>("tablet", model.tablet, {
    source: flags.useMockFallback ? "mock-fallback" : "local-adapter",
    preview: flags.previewEnabled
  }, model.quality.tablet);

  return <PrismaTabletPulsePanel envelope={envelope} flags={flags} />;
}
