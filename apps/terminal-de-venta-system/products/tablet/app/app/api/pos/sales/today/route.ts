import { toPosApiError } from "@/server/pos-api/errors";
import { ok, fail } from "@/server/pos-api/responses";
import { getTodaySalesSummary } from "@/server/pos-api/sales-summary.prisma";
import { readSalesTodayInput } from "@/server/pos-api/validators";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const input = readSalesTodayInput(new URL(request.url).searchParams);
    const summary = await getTodaySalesSummary(input);
    return ok({ summary }, undefined, {
      endpoint: "GET /api/pos/sales/today",
      businessId: input.businessId,
      terminalId: input.terminalId ?? null
    });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_DATE") {
      return fail("INVALID_DATE", "Usa date con formato YYYY-MM-DD.", 400);
    }
    return toPosApiError(error);
  }
}
