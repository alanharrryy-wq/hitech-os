import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const movements = await getBackofficeModuleOverview("movements");
    return ok(movements, { endpoint: "GET /api/backoffice/movements", persistence: movements.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
