import { tabletLicenseOk } from "@/server/licensing/tablet-license-api";
import { getTabletFeatureList } from "@/server/licensing/tablet-license-service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return tabletLicenseOk({ features: getTabletFeatureList() }, { endpoint: "GET /api/license/features", surface: "tablet" });
}
