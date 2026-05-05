import { toPosApiError } from "@/server/pos-api/errors";
import { ok } from "@/server/pos-api/responses";
import { readPosListInput } from "@/server/pos-api/validators";
import { countOutboxByState } from "@/server/pos-outbox";
import { getTabletRuntimeMeta } from "@/server/pos-runtime";
import { getOutboxEvents } from "@/server/pos-reports";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const input = readPosListInput(new URL(request.url).searchParams, 50, 200);
    const [events, counts] = await Promise.all([getOutboxEvents(input), countOutboxByState(input.businessId)]);
    return ok({ events, counts, count: events.length }, undefined, {
      endpoint: "GET /api/pos/events/outbox",
      businessId: input.businessId,
      status: input.status ?? null,
      runtime: getTabletRuntimeMeta()
    });
  } catch (error) {
    return toPosApiError(error);
  }
}
