import { pcLicenseRefreshOk, refreshPcLicense } from "@/server/licensing/pc-license-refresh";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST() {
  const result = await refreshPcLicense();
  return pcLicenseRefreshOk(result, { endpoint: "POST /api/license/refresh", surface: "pc" });
}
