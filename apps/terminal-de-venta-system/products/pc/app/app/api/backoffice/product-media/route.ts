import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { readProductMediaUpdate, updateProductMedia } from "@/server/services/product-media.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function PATCH(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const product = await updateProductMedia(readProductMediaUpdate(body));
    if (!product) return fail("PRODUCT_MEDIA_PRODUCT_NOT_FOUND", "El producto no existe en este negocio.", 404);
    return ok({ product }, { endpoint: "PATCH /api/backoffice/product-media", readAfterWrite: true });
  } catch (error) {
    const code = error instanceof Error ? error.message : "";
    if (code === "INVALID_JSON_BODY") return fail(code, "El cuerpo JSON no es válido.", 400);
    if (code === "PRODUCT_MEDIA_PRODUCT_REQUIRED") return fail(code, "Selecciona un producto.", 400);
    if (code === "PRODUCT_MEDIA_VERSION_REQUIRED") return fail(code, "La actualización requiere la versión temporal leída del producto.", 400);
    if (code === "PRODUCT_MEDIA_REFERENCE_INVALID") return fail(code, "Usa una URL HTTPS o una referencia portable bajo /product-media/.", 400);
    if (code === "PRODUCT_MEDIA_VERSION_CONFLICT") return fail(code, "El producto cambió en otra sesión. Vuelve a cargarlo antes de guardar la imagen.", 409);
    return toBackofficeError(error);
  }
}
