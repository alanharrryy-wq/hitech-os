import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const audit = await getBackofficeModuleOverview("audit");
    return ok(audit, { endpoint: "GET /api/backoffice/audit/recent", persistence: audit.meta.persistence });
  } catch (error) {
    return toBackofficeError(error);
  }
}
