import { noStoreJsonInit } from "@/lib/prisma-app/prisma-app-api-contracts";
import { loadMobileDataPlaneState } from "@/lib/prisma-app/mobile-data-plane/state-loader";
import { evaluateDataQuality, PRISMA_MOBILE_INTELLIGENCE_CONTRACT_ID } from "@/lib/prisma-app/mobile-intelligence";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET() {
  const state = await loadMobileDataPlaneState();
  const dataQuality = evaluateDataQuality(state);
  return Response.json({
    ok: true,
    data: dataQuality,
    meta: {
      generatedAt: dataQuality.generatedAt,
      runtimeMode: dataQuality.runtimeMode,
      confidence: dataQuality.confidence,
      freshnessSeconds: dataQuality.freshnessSeconds,
      contractId: PRISMA_MOBILE_INTELLIGENCE_CONTRACT_ID
    }
  }, noStoreJsonInit());
}

