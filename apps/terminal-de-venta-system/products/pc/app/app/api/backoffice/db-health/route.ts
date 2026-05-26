import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcDbHealthContract } from "@/server/services/pc-data-mode-contract.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    return ok(await getPcDbHealthContract(), { endpoint: "GET /api/backoffice/db-health", mutation: false });
  } catch (error) {
    return toBackofficeError(error);
  }
}
