import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { getSalesHistorySummary } from "@/server/pos-api/sales-summary.prisma";
import { readSalesHistoryInput } from "@/server/pos-api/validators";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const input = readSalesHistoryInput(new URL(request.url).searchParams);
    const summary = await getSalesHistorySummary(input);
    return ok({ summary }, undefined, {
      endpoint: "GET /api/pos/sales/history",
      businessId: input.businessId,
      terminalId: input.terminalId ?? null,
      preset: input.preset
    });
  } catch (error) {
    if (error instanceof Error && error.message === "HISTORY_RANGE_TOO_LARGE") {
      return fail("HISTORY_RANGE_TOO_LARGE", "El rango personalizado no puede exceder 60 días.", 400);
    }
    if (error instanceof Error && (error.message === "INVALID_HISTORY_FROM" || error.message === "INVALID_HISTORY_TO" || error.message === "INVALID_HISTORY_RANGE")) {
      return fail("INVALID_HISTORY_RANGE", "Usa fechas válidas con formato YYYY-MM-DD y rango ascendente.", 400);
    }
    if (error instanceof Error && error.message === "MISSING_HISTORY_RANGE") {
      return fail("MISSING_HISTORY_RANGE", "Captura fecha inicial y final para rango personalizado.", 400);
    }
    return toPosApiError(error);
  }
}
