import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcDataModeStatusContract } from "@/server/services/pc-data-mode-contract.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    return ok(await getPcDataModeStatusContract(), { endpoint: "GET /api/backoffice/demo/status", mutation: false });
  } catch (error) {
    return toBackofficeError(error);
  }
}
