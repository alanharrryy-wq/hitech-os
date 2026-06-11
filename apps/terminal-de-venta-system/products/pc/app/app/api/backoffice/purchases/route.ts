import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const purchases = await getBackofficeModuleOverview("purchasing");
    return ok(purchases, { endpoint: "GET /api/backoffice/purchases", aliasOf: "GET /api/backoffice/purchasing", persistence: purchases.meta.persistence, readOnly: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
