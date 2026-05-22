import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { commandCenterToCsv, getPcSalesControl } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const params = new URL(request.url).searchParams;
    const model = await getPcSalesControl(params);
    if (params.get("format") === "csv") {
      return new Response(commandCenterToCsv(model), {
        headers: {
          "content-type": "text/csv; charset=utf-8",
          "content-disposition": "attachment; filename=pc-sales-control.csv"
        }
      });
    }
    return ok(model, { endpoint: "GET /api/backoffice/sales-control", bounded: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
