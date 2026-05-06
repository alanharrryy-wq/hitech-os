import { pcLicenseOk } from "@/server/licensing/pc-license-api";
import { getPcFeatureList } from "@/server/licensing/pc-license-service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return pcLicenseOk({ features: getPcFeatureList() }, { endpoint: "GET /api/license/features", surface: "pc" });
}
