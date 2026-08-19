import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { createProductVariant, readProductVariantCreate } from "@/server/services/product-variant.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const result = await createProductVariant(readProductVariantCreate(body));
    return ok(result, { endpoint: "POST /api/backoffice/product-variants", idempotent: result.replayed }, { status: result.replayed ? 200 : 201 });
  } catch (error) {
    const code = error instanceof Error ? error.message : "";
    if (code === "INVALID_JSON_BODY") return fail(code, "No pudimos leer la solicitud. Intenta de nuevo.", 400);
    if (code === "PRODUCT_VARIANT_PRODUCTS_REQUIRED") return fail(code, "Selecciona el producto base y el producto variante.", 400);
    if (code === "PRODUCT_VARIANT_LABEL_REQUIRED") return fail(code, "Captura una etiqueta para la variante.", 400);
    if (code === "PRODUCT_VARIANT_IDEMPOTENCY_REQUIRED") return fail(code, "No pudimos validar la solicitud. Intenta crear la variante nuevamente.", 400);
    if (code === "PRODUCT_VARIANT_SELF_REFERENCE") return fail(code, "Un producto no puede ser variante de sí mismo.", 422);
    if (code === "PRODUCT_VARIANT_PRODUCT_NOT_AVAILABLE") return fail(code, "Los dos productos deben existir y estar activos.", 422);
    if (code === "PRODUCT_VARIANT_NESTED_PARENT") return fail(code, "Una variante no puede contener otra variante.", 422);
    if (code === "PRODUCT_VARIANT_SELLABLE_ALREADY_LINKED") return fail(code, "Ese producto ya pertenece a otra variante.", 409);
    return toBackofficeError(error);
  }
}
