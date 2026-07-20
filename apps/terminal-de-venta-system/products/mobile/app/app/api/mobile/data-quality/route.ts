import { noStoreJsonInit } from "@/lib/prisma-app/prisma-app-api-contracts";
import { evaluateDataQuality, PRISMA_MOBILE_INTELLIGENCE_CONTRACT_ID } from "@/lib/prisma-app/mobile-intelligence";
import { loadAuthorizedMobileState } from "@/lib/prisma-app/mobile-security";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET(request: Request) {
  const guarded = await loadAuthorizedMobileState(request, "RM.DATA.READINESS");
  if (!guarded.ok) return guarded.response;
  const state = guarded.state;
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
