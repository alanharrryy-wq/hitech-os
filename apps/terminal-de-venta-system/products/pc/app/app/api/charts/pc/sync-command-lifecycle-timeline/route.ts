import { fail, ok } from "@/lib/backoffice/api-response";
import { getPcSyncCommandLifecycleTimelineChart } from "@/server/services/pc-sync-chart-data.service";

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
    const envelope = await getPcSyncCommandLifecycleTimelineChart(inputFromUrl(request));
    return ok(envelope, { endpoint: "GET /api/charts/pc/sync-command-lifecycle-timeline" });
  } catch {
    return fail("PC_SYNC_CHART_DATA_ERROR", "No fue posible cargar el timeline de lifecycle de sync.", 500, { endpoint: "GET /api/charts/pc/sync-command-lifecycle-timeline" });
  }
}
