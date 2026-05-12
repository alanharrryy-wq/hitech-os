import type { PrismaMobileChartsViewModel } from "@prisma-charts/prismaChartContracts";
import { buildPrismaInsightEnvelope, buildPrismaTripleAppChartsViewModel } from "@prisma-charts/prismaChartAdapters";
import { resolvePrismaChartFlags } from "@prisma-charts/prismaChartFlags";
import { loadMobileDataPlaneState } from "@/lib/prisma-app/mobile-data-plane";
import { buildSnapshotPayload } from "@/lib/prisma-app/mobile-data-plane/payload-builders";
import { PrismaMobileCommandDeck } from "./PrismaMobileCommandDeck";

type SearchParams = Record<string, string | string[] | undefined>;

export const dynamic = "force-dynamic";

export const metadata = {
  title: "PRISMA Command - Mobile Owner",
  description: "Preview de supervision Mobile con seis charts compactos."
};

export default async function PrismaCommandPage({ searchParams }: { searchParams?: Promise<SearchParams> | SearchParams }) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const flags = resolvePrismaChartFlags("mobile", resolvedSearchParams);
  const errors: string[] = [];
  const snapshotResult = await loadMobileDataPlaneState()
    .then((state) => buildSnapshotPayload(state))
    .catch((error) => {
      errors.push(`Mobile snapshot unavailable: ${error instanceof Error ? error.message : String(error)}`);
      return null;
    });
  const model = buildPrismaTripleAppChartsViewModel({
    mobile: {
      snapshot: snapshotResult,
      errors
    }
  });
  const envelope = buildPrismaInsightEnvelope<PrismaMobileChartsViewModel>("mobile", model.mobile, {
    source: flags.useMockFallback ? "mock-fallback" : "snapshot-adapter",
    preview: flags.previewEnabled
  }, model.quality.mobile);

  return <PrismaMobileCommandDeck envelope={envelope} flags={flags} />;
}
