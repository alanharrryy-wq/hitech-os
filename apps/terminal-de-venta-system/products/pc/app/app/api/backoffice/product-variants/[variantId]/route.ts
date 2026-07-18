import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { readProductVariantUpdate, updateProductVariant } from "@/server/services/product-variant.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function PATCH(request: Request, context: { params: Promise<{ variantId: string }> }) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const variantId = (await context.params).variantId.trim();
    if (!variantId) return fail("PRODUCT_VARIANT_ID_REQUIRED", "La variante no es válida.", 400);
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const variant = await updateProductVariant(variantId, readProductVariantUpdate(body));
    if (!variant) return fail("PRODUCT_VARIANT_NOT_FOUND", "La variante no existe en este negocio.", 404);
    return ok({ variant }, { endpoint: "PATCH /api/backoffice/product-variants/:variantId", readAfterWrite: true });
  } catch (error) {
    const code = error instanceof Error ? error.message : "";
    if (code === "INVALID_JSON_BODY") return fail(code, "El cuerpo JSON no es válido.", 400);
    if (code === "PRODUCT_VARIANT_VERSION_REQUIRED") return fail(code, "La actualización requiere la versión leída de la variante.", 400);
    if (code === "PRODUCT_VARIANT_STATUS_INVALID") return fail(code, "El estado solicitado no es válido.", 400);
    if (code === "PRODUCT_VARIANT_LABEL_REQUIRED") return fail(code, "Captura una etiqueta de variante.", 400);
    if (code === "PRODUCT_VARIANT_VERSION_CONFLICT") return fail(code, "La variante cambió en otra sesión. Vuelve a cargarla antes de actualizar.", 409);
    return toBackofficeError(error);
  }
}
