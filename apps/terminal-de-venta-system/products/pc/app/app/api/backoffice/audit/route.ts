import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api"; // PRISMA_LICENSE_02AB_PC_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  
  // PRISMA_LICENSE_02AB_BEGIN:audit.view
  const prismaLicenseGate = await guardPcFeatureForApi("audit.view");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:audit.view
try {
    const audit = await getBackofficeModuleOverview("audit");
    return ok(audit, { endpoint: "GET /api/backoffice/audit", persistence: audit.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
