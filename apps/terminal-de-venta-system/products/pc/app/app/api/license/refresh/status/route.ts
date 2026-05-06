import { pcLicenseRefreshOk, getPcLicenseRefreshStatus } from "@/server/licensing/pc-license-refresh";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return pcLicenseRefreshOk(getPcLicenseRefreshStatus(), { endpoint: "GET /api/license/refresh/status", surface: "pc" });
}
