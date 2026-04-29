import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeDashboard } from "@/lib/backoffice/dashboard";

import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api"; // PRISMA_LICENSE_02AB_PC_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  
  // PRISMA_LICENSE_02AB_BEGIN:pc.dashboard.view
  const prismaLicenseGate = await guardPcFeatureForApi("pc.dashboard.view");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:pc.dashboard.view
try {
    const dashboard = await getBackofficeDashboard();
    return ok(dashboard, { endpoint: "GET /api/backoffice/dashboard" });
  } catch (error) {
    return toBackofficeError(error);
  }
}
