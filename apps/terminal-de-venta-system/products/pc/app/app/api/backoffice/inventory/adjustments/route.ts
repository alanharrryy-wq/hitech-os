import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { adjustInventoryStock } from "@/server/services/inventory-mutations.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("stock.adjust");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const adjustment = await adjustInventoryStock(body);
    return ok({ adjustment }, { endpoint: "POST /api/backoffice/inventory/adjustments", persistence: "canonical_prisma", wave: 3 }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message === "STOCK_PRODUCT_NOT_FOUND") return fail("STOCK_PRODUCT_NOT_FOUND", "No existe el producto solicitado.", 404);
    if (error instanceof Error && error.message === "STOCK_NEGATIVE_BLOCKED") return fail("STOCK_NEGATIVE_BLOCKED", "El ajuste dejaría existencias negativas y fue bloqueado.", 409);
    if (error instanceof Error && error.message.startsWith("STOCK_")) return fail(error.message, "El ajuste de inventario no es válido.", 400);
    return toBackofficeError(error);
  }
}
