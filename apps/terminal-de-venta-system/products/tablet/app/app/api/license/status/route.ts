import { tabletLicenseOk } from "@/server/licensing/tablet-license-api";
import { getTabletLicenseGovernor } from "@/server/licensing/tablet-license-service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return tabletLicenseOk(getTabletLicenseGovernor(), { endpoint: "GET /api/license/status", surface: "tablet" });
}
