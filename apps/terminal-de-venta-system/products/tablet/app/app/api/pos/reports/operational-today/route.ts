import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { readPosListInput } from "@/server/pos-api/validators";
import { getOperationalTodayReport } from "@/server/pos-reports";

import { guardTabletFeatureForApi } from "@/server/licensing/tablet-license-api"; // PRISMA_LICENSE_02AB_TABLET_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  
  // PRISMA_LICENSE_02AB_BEGIN:report.operational.view
  const prismaLicenseGate = await guardTabletFeatureForApi("report.operational.view");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:report.operational.view
try {
    const input = readPosListInput(new URL(request.url).searchParams, 50, 200);
    const report = await getOperationalTodayReport(input);
    return ok({ report }, undefined, {
      endpoint: "GET /api/pos/reports/operational-today",
      businessId: input.businessId,
      terminalId: input.terminalId ?? null
    });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_DATE") {
      return fail("INVALID_DATE", "Usa date con formato YYYY-MM-DD.", 400);
    }
    return toPosApiError(error);
  }
}
