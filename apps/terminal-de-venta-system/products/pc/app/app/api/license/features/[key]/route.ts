import { pcLicenseOk } from "@/server/licensing/pc-license-api";
import { resolvePcFeature } from "@/server/licensing/pc-license-service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(_request: Request, context: { params: Promise<{ key: string }> }) {
  const params = await context.params;
  return pcLicenseOk(resolvePcFeature(decodeURIComponent(params.key)), { endpoint: "GET /api/license/features/[key]", surface: "pc" });
}
