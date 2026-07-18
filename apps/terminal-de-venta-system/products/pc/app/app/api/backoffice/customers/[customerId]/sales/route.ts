import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { attachCustomerToSale } from "@/server/services/customer.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type RouteContext = { params: Promise<{ customerId: string }> };

export async function POST(request: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const { customerId } = await context.params;
    const body = await request.json().catch(() => ({}));
    const saleId = typeof body?.saleId === "string" ? body.saleId.trim() : "";
    if (!customerId.trim()) return fail("CUSTOMER_ID_REQUIRED", "Falta el cliente solicitado.", 400);
    if (!saleId) return fail("SALE_ID_REQUIRED", "Falta la venta a asociar.", 400);
    const result = await attachCustomerToSale(customerId.trim(), saleId);
    return ok(result, { endpoint: "POST /api/backoffice/customers/:customerId/sales" });
  } catch (error) {
    if (error instanceof Error && error.message === "CUSTOMER_NOT_FOUND") return fail("CUSTOMER_NOT_FOUND", "No existe el cliente solicitado.", 404);
    if (error instanceof Error && error.message === "SALE_NOT_FOUND_OR_ALREADY_ASSIGNED") return fail("SALE_NOT_FOUND_OR_ALREADY_ASSIGNED", "La venta no existe o ya pertenece a otro cliente.", 409);
    return toBackofficeError(error);
  }
}
