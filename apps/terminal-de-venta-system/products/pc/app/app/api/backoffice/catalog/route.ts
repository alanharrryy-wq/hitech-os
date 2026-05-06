import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const catalog = await getBackofficeModuleOverview("catalog");
    return ok(catalog, { endpoint: "GET /api/backoffice/catalog", persistence: catalog.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
