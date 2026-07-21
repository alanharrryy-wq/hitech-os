import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcLicenseReadiness } from "@/server/licensing/pc-license-service";

export const runtime = "nodejs";

export async function GET() {
  try {
    return ok(getPcLicenseReadiness(), {
      endpoint: "GET /api/backoffice/platform-readiness",
      mutation: false,
      source: "pc_license_governor"
    });
  } catch (error) {
    return toBackofficeError(error);
  }
}
