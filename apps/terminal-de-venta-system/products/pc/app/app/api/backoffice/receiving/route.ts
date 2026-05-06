import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api"; // PRISMA_LICENSE_02AB_PC_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  
  // PRISMA_LICENSE_02AB_BEGIN:receiving.write
  const prismaLicenseGate = await guardPcFeatureForApi("receiving.write");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:receiving.write
try {
    const receiving = await getBackofficeModuleOverview("receiving");
    return ok(receiving, { endpoint: "GET /api/backoffice/receiving", persistence: receiving.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
