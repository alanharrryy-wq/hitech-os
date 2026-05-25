import type { PrismaPcChartsViewModel } from "@prisma-charts/prismaChartContracts";
import { buildPrismaInsightEnvelope, buildPrismaTripleAppChartsViewModel } from "@prisma-charts/prismaChartAdapters";
import { resolvePrismaChartFlags } from "@prisma-charts/prismaChartFlags";
import { getBackofficeDashboard } from "@/lib/backoffice/dashboard";
import { getTriDbStatusCard } from "@/server/services/tri-db-status.service";
import { PrismaPcInsightsGrid } from "./PrismaPcInsightsGrid";

type SearchParams = Record<string, string | string[] | undefined>;

export const dynamic = "force-dynamic";

export const metadata = {
  title: "PRISMA Insights - PC Backoffice",
  description: "Vista preview de gobernanza y analisis con ECharts para PC."
};

export default async function PrismaInsightsPage({ searchParams }: { searchParams?: Promise<SearchParams> | SearchParams }) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const flags = resolvePrismaChartFlags("pc", resolvedSearchParams);
  const errors: string[] = [];
  const [dashboardResult, triDbStatusResult] = await Promise.allSettled([
    getBackofficeDashboard(),
    getTriDbStatusCard()
  ]);
  if (dashboardResult.status === "rejected") errors.push(`PC dashboard unavailable: ${dashboardResult.reason instanceof Error ? dashboardResult.reason.message : String(dashboardResult.reason)}`);
  if (triDbStatusResult.status === "rejected") errors.push(`TRI-DB status unavailable: ${triDbStatusResult.reason instanceof Error ? triDbStatusResult.reason.message : String(triDbStatusResult.reason)}`);
  const model = buildPrismaTripleAppChartsViewModel({
    pc: {
      dashboard: dashboardResult.status === "fulfilled" ? dashboardResult.value : null,
      triDbStatus: triDbStatusResult.status === "fulfilled" ? triDbStatusResult.value : null,
      errors
    }
  });
  const envelope = buildPrismaInsightEnvelope<PrismaPcChartsViewModel>("pc", model.pc, {
    source: flags.useMockFallback ? "mock-fallback" : "adapter",
    preview: flags.previewEnabled
  }, model.quality.pc);

  return <PrismaPcInsightsGrid envelope={envelope} flags={flags} />;
}
