import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const reorder = await getBackofficeModuleOverview("replenishment");
    return ok(reorder, { endpoint: "GET /api/backoffice/reorder", aliasOf: "GET /api/backoffice/replenishment", persistence: reorder.meta.persistence, readOnly: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
