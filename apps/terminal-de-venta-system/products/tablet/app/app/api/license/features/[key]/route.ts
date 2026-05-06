import { tabletLicenseOk } from "@/server/licensing/tablet-license-api";
import { resolveTabletFeature } from "@/server/licensing/tablet-license-service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(_request: Request, context: { params: Promise<{ key: string }> }) {
  const params = await context.params;
  return tabletLicenseOk(resolveTabletFeature(decodeURIComponent(params.key)), { endpoint: "GET /api/license/features/[key]", surface: "tablet" });
}
