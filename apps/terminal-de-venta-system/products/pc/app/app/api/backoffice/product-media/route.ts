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
    if (!product) return fail("PRODUCT_MEDIA_PRODUCT_NOT_FOUND", "No encontramos ese producto.", 404);
    return ok({ product }, { endpoint: "PATCH /api/backoffice/product-media", readAfterWrite: true });
  } catch (error) {
    const code = error instanceof Error ? error.message : "";
    if (code === "INVALID_JSON_BODY") return fail(code, "No pudimos leer la solicitud. Intenta de nuevo.", 400);
    if (code === "PRODUCT_MEDIA_PRODUCT_REQUIRED") return fail(code, "Selecciona un producto.", 400);
    if (code === "PRODUCT_MEDIA_VERSION_REQUIRED") return fail(code, "Vuelve a cargar el producto antes de guardar la imagen.", 400);
    if (code === "PRODUCT_MEDIA_REFERENCE_INVALID") return fail(code, "Usa una dirección HTTPS o selecciona una imagen de la biblioteca.", 400);
    if (code === "PRODUCT_MEDIA_VERSION_CONFLICT") return fail(code, "El producto cambió en otra sesión. Vuelve a cargarlo antes de guardar la imagen.", 409);
    return toBackofficeError(error);
  }
}
