import { toPosApiError } from "@/server/pos-api/errors";
import { ok } from "@/server/pos-api/responses";
import { readPosListInput } from "@/server/pos-api/validators";
import {
  getLowStockProducts,
  getOperationalTodayReport,
  getOutboxEvents,
  getRecentInventoryMovements
} from "@/server/pos-reports";
import { getTabletRuntimeMeta } from "@/server/pos-runtime";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function withQuery(path: string, query: Record<string, string | number | null | undefined>) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === null || value === undefined || value === "") continue;
    params.set(key, String(value));
  }
  const qs = params.toString();
  return qs ? `${path}?${qs}` : path;
}

export async function GET(request: Request) {
  try {
    const input = readPosListInput(new URL(request.url).searchParams, 30, 120);
    const [report, outboxEvents, recentMovements, lowStockProducts] = await Promise.all([
      getOperationalTodayReport(input),
      getOutboxEvents(input),
      getRecentInventoryMovements(input),
      getLowStockProducts(input)
    ]);

    const exportQuery = {
      businessId: input.businessId,
      terminalId: input.terminalId,
      date: input.date,
      limit: input.limit
    };

    const audit = {
      generatedAt: new Date().toISOString(),
      businessId: input.businessId,
      terminalId: input.terminalId ?? null,
      runtime: getTabletRuntimeMeta(),
      report,
      outbox: {
        events: outboxEvents,
        count: outboxEvents.length,
        counts: report.outboxCounts,
        pending: report.pendingOutboxCount,
        failed: report.failedOutboxCount
      },
      inventory: {
        recentMovements,
        recentMovementsCount: recentMovements.length,
        lowStockProducts,
        lowStockCount: lowStockProducts.length
      },
      exports: {
        salesCsv: withQuery("/api/pos/export/sales-today", { ...exportQuery, format: "csv" }),
        salesJson: withQuery("/api/pos/export/sales-today", { ...exportQuery, format: "json" }),
        eventsCsv: withQuery("/api/pos/export/events", { ...exportQuery, format: "csv" }),
        eventsJson: withQuery("/api/pos/export/events", { ...exportQuery, format: "json" }),
        inventoryMovementsCsv: withQuery("/api/pos/export/inventory-movements", { ...exportQuery, format: "csv" }),
        inventoryMovementsJson: withQuery("/api/pos/export/inventory-movements", { ...exportQuery, format: "json" })
      },
      diagnostics: [
        "Tablet opera con datos locales.",
        "Outbox conserva eventos pendientes para sincronización posterior.",
        "Los exports salen desde endpoints locales de Tablet.",
        "Este endpoint no depende de PC para consultar el estado operativo local."
      ]
    };

    return ok({ audit }, undefined, {
      endpoint: "GET /api/pos/offline/audit",
      businessId: input.businessId,
      terminalId: input.terminalId ?? null,
      generatedAt: audit.generatedAt
    });
  } catch (error) {
    return toPosApiError(error);
  }
}
