import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcTabletCommunication } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const model = await getPcTabletCommunication(new URL(request.url).searchParams);
    return ok(model, { endpoint: "GET /api/backoffice/tablet-communication", bounded: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
