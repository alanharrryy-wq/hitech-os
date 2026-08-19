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
    if (!variant) return fail("PRODUCT_VARIANT_NOT_FOUND", "No encontramos esa variante.", 404);
    return ok({ variant }, { endpoint: "PATCH /api/backoffice/product-variants/:variantId", readAfterWrite: true });
  } catch (error) {
    const code = error instanceof Error ? error.message : "";
    if (code === "INVALID_JSON_BODY") return fail(code, "No pudimos leer la solicitud. Intenta de nuevo.", 400);
    if (code === "PRODUCT_VARIANT_VERSION_REQUIRED") return fail(code, "Vuelve a cargar la variante antes de actualizarla.", 400);
    if (code === "PRODUCT_VARIANT_STATUS_INVALID") return fail(code, "El estado solicitado no es válido.", 400);
    if (code === "PRODUCT_VARIANT_LABEL_REQUIRED") return fail(code, "Captura una etiqueta para la variante.", 400);
    if (code === "PRODUCT_VARIANT_VERSION_CONFLICT") return fail(code, "La variante cambió en otra sesión. Vuelve a cargarla antes de actualizar.", 409);
    return toBackofficeError(error, { customerSafe: true });
  }
}
