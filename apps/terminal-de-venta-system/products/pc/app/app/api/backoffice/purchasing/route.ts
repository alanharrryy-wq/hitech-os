import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api"; // PRISMA_LICENSE_02AB_PC_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  
  // PRISMA_LICENSE_02AB_BEGIN:purchase.write
  const prismaLicenseGate = await guardPcFeatureForApi("purchase.write");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:purchase.write
try {
    const purchasing = await getBackofficeModuleOverview("purchasing");
    return ok(purchasing, { endpoint: "GET /api/backoffice/purchasing", persistence: purchasing.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
