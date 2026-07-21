import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { buildCustomerProjectionDelta } from "@/server/services/customer-projection-export.service";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const params = new URL(request.url).searchParams;
    const businessId = await resolvePcBusinessScope();
    const requestedBusinessId = params.get("businessId")?.trim();
    if (requestedBusinessId && requestedBusinessId !== businessId) return fail("CUSTOMER_PROJECTION_SCOPE_DENIED", "La proyección solicitada no pertenece al negocio PC activo.", 403);
    return ok(await buildCustomerProjectionDelta({ businessId, cursor: params.get("cursor"), limit: Number(params.get("limit")) || undefined }), { endpoint: "GET /api/sync/export/customer-projection" });
  } catch (error) {
    if (error instanceof Error && error.message === "CUSTOMER_PROJECTION_INVALID_CURSOR") return fail("CUSTOMER_PROJECTION_INVALID_CURSOR", "Cursor de clientes inválido.", 400);
    return toBackofficeError(error);
  }
}
