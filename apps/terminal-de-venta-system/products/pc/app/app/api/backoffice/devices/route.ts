import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcDeviceFleet } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const model = await getPcDeviceFleet(new URL(request.url).searchParams);
    return ok(model, { endpoint: "GET /api/backoffice/devices", bounded: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
