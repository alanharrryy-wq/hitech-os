import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcDataQuality } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const model = await getPcDataQuality();
    return ok(model, { endpoint: "GET /api/backoffice/data-quality", bounded: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
