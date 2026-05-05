import { tabletLicenseRefreshOk, getTabletLicenseRefreshStatus } from "@/server/licensing/tablet-license-refresh";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return tabletLicenseRefreshOk(getTabletLicenseRefreshStatus(), { endpoint: "GET /api/license/refresh/status", surface: "tablet" });
}
