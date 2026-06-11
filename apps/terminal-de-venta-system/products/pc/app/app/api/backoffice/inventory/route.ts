import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const inventory = await getBackofficeModuleOverview("stock");
    return ok(inventory, { endpoint: "GET /api/backoffice/inventory", aliasOf: "GET /api/backoffice/stock", persistence: inventory.meta.persistence, readOnly: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
