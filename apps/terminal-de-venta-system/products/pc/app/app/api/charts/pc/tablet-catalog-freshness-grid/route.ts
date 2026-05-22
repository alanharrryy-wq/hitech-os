import { fail, ok } from "@/lib/backoffice/api-response";
import { getPcTabletCatalogFreshnessGridChart } from "@/server/services/pc-sync-chart-data.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function inputFromUrl(request: Request) {
  const url = new URL(request.url);
  return {
    businessId: url.searchParams.get("businessId"),
    terminalId: url.searchParams.get("terminalId"),
    limit: url.searchParams.get("limit")
  };
}

export async function GET(request: Request) {
  try {
    const envelope = await getPcTabletCatalogFreshnessGridChart(inputFromUrl(request));
    return ok(envelope, { endpoint: "GET /api/charts/pc/tablet-catalog-freshness-grid" });
  } catch {
    return fail("PC_SYNC_CHART_DATA_ERROR", "No fue posible cargar el chart de frescura de catalogo.", 500, { endpoint: "GET /api/charts/pc/tablet-catalog-freshness-grid" });
  }
}
