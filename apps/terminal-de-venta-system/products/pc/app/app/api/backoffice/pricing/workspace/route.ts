// PRISMA_PRICING_OWNER_V1
import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { getPricingPolicySnapshot } from "@/server/services/pricing-policy.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const licenseGate = await guardPcFeatureForApi("pricing.read");
    if (licenseGate) return licenseGate;
    const workspace = await getPricingPolicySnapshot();
    return ok({ workspace }, { endpoint: "GET /api/backoffice/pricing/workspace", mutationReady: workspace.mutationReady });
  } catch (error) {
    return toBackofficeError(error);
  }
}
