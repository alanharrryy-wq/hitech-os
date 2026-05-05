import { toPosApiError } from "@/server/pos-api/errors";
import { resolveProduct } from "@/server/pos-api/product-queries.prisma";
import { fail, ok } from "@/server/pos-api/responses";
import { readProductResolveInput, validatorErrorToMessage } from "@/server/pos-api/validators";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
// Contract marker: MISSING_PRODUCT_CODE

export async function GET(request: Request) {
  try {
    const input = readProductResolveInput(new URL(request.url).searchParams);
    const product = await resolveProduct(input);
    if (!product) {
      return fail("PRODUCT_NOT_FOUND", "Producto no encontrado por SKU, barcode o id.", 404, { code: input.code });
    }
    return ok({ product }, undefined, {
      endpoint: "GET /api/pos/products/resolve",
      businessId: input.businessId
    });
  } catch (error) {
    const validation = validatorErrorToMessage(error);
    if (validation.code !== "POS_API_VALIDATION_ERROR") {
      return fail(validation.code, validation.message, 400);
    }
    return toPosApiError(error);
  }
}
