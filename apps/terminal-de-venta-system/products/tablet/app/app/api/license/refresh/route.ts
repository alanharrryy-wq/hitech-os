import { tabletLicenseRefreshOk, refreshTabletLicense } from "@/server/licensing/tablet-license-refresh";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST() {
  const result = await refreshTabletLicense();
  return tabletLicenseRefreshOk(result, { endpoint: "POST /api/license/refresh", surface: "tablet" });
}
