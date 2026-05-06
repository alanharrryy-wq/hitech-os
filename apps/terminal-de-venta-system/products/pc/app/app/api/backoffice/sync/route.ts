import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api"; // PRISMA_LICENSE_02AB_PC_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  
  // PRISMA_LICENSE_02AB_BEGIN:sync.managed
  const prismaLicenseGate = await guardPcFeatureForApi("sync.managed");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:sync.managed
try {
    const sync = await getBackofficeModuleOverview("sync");
    return ok(sync, { endpoint: "GET /api/backoffice/sync", persistence: sync.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
