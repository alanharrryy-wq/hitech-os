import { toPosApiError } from "@/server/pos-api/errors";
import { ok } from "@/server/pos-api/responses";
import { DEFAULT_POS_API_BUSINESS_ID } from "@/server/pos-api/validators";
import { buildContextualExportReport } from "@/server/pos-export/contextual";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const params = new URL(request.url).searchParams;
    const surface = params.get("surface") ?? "home";
    const businessId = params.get("businessId") ?? DEFAULT_POS_API_BUSINESS_ID;
    const report = await buildContextualExportReport({ businessId, surface });
    return ok(report, undefined, {
      endpoint: "GET /api/pos/export/contextual",
      businessId,
      surface,
      message: "Reporte contextual listo",
    });
  } catch (error) {
    return toPosApiError(error);
  }
}
