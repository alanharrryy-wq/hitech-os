import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcSyncCommandCenter } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const model = await getPcSyncCommandCenter(new URL(request.url).searchParams);
    return ok(model, { endpoint: "GET /api/backoffice/sync/status", bounded: true, readOnly: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
