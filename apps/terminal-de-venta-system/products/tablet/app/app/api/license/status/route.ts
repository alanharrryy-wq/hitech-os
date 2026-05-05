import { tabletLicenseOk } from "@/server/licensing/tablet-license-api";
import { getTabletLicenseStatus } from "@/server/licensing/tablet-license-service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return tabletLicenseOk(getTabletLicenseStatus(), { endpoint: "GET /api/license/status", surface: "tablet" });
}
