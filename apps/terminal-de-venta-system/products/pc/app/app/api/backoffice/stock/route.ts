import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const stock = await getBackofficeModuleOverview("stock");
    return ok(stock, { endpoint: "GET /api/backoffice/stock", persistence: stock.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
