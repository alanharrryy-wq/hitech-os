import { pcLicenseOk } from "@/server/licensing/pc-license-api";
import { getPcLicenseStatus } from "@/server/licensing/pc-license-service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return pcLicenseOk(getPcLicenseStatus(), { endpoint: "GET /api/license/status", surface: "pc" });
}
