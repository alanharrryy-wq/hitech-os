import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api"; // PRISMA_LICENSE_02AB_PC_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  
  // PRISMA_LICENSE_02AB_BEGIN:replenishment.view
  const prismaLicenseGate = await guardPcFeatureForApi("replenishment.view");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:replenishment.view
try {
    const replenishment = await getBackofficeModuleOverview("replenishment");
    return ok(replenishment, { endpoint: "GET /api/backoffice/replenishment", persistence: replenishment.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
