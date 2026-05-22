import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcLicenseRuntimeControl } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const model = await getPcLicenseRuntimeControl();
    return ok(model, { endpoint: "GET /api/backoffice/license-runtime", bounded: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
