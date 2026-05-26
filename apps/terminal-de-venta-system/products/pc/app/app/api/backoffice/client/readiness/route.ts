import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcClientReadinessContract } from "@/server/services/pc-data-mode-contract.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    return ok(await getPcClientReadinessContract(), { endpoint: "GET /api/backoffice/client/readiness", mutation: false });
  } catch (error) {
    return toBackofficeError(error);
  }
}
