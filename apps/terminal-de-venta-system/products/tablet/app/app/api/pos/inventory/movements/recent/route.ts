import { toPosApiError } from "@/server/pos-api/errors";
import { ok } from "@/server/pos-api/responses";
import { readPosListInput } from "@/server/pos-api/validators";
import { getTabletRuntimeMeta } from "@/server/pos-runtime";
import { getRecentInventoryMovements } from "@/server/pos-reports";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const input = readPosListInput(new URL(request.url).searchParams, 50, 200);
    const movements = await getRecentInventoryMovements(input);
    return ok({ movements, count: movements.length }, undefined, {
      endpoint: "GET /api/pos/inventory/movements/recent",
      businessId: input.businessId,
      runtime: getTabletRuntimeMeta()
    });
  } catch (error) {
    return toPosApiError(error);
  }
}
