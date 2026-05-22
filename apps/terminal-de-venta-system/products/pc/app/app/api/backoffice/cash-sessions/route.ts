import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getPcCashSessions } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const model = await getPcCashSessions(new URL(request.url).searchParams);
    return ok(model, { endpoint: "GET /api/backoffice/cash-sessions", bounded: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
