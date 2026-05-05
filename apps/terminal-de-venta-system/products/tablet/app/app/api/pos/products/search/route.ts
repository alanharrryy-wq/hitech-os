import { toPosApiError } from "@/server/pos-api/errors";
import { searchProducts } from "@/server/pos-api/product-queries.prisma";
import { fail, ok } from "@/server/pos-api/responses";
import { readProductSearchInput } from "@/server/pos-api/validators";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const input = readProductSearchInput(new URL(request.url).searchParams);
    const products = await searchProducts(input);
    return ok({ products, count: products.length }, undefined, {
      endpoint: "GET /api/pos/products/search",
      query: input.q,
      businessId: input.businessId
    });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_DATE") {
      return fail("INVALID_DATE", "Fecha invalida.", 400);
    }
    return toPosApiError(error);
  }
}
