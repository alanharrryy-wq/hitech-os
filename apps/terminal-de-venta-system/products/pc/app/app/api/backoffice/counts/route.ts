import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const counts = await getBackofficeModuleOverview("counts");
    return ok(counts, { endpoint: "GET /api/backoffice/counts", persistence: counts.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
