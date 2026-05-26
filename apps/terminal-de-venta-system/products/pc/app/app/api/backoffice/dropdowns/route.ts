import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcDropdownContract } from "@/server/services/pc-data-mode-contract.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    return ok(await getPcDropdownContract(), { endpoint: "GET /api/backoffice/dropdowns", mutation: false });
  } catch (error) {
    return toBackofficeError(error);
  }
}
