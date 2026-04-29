import { toPosApiError } from "@/server/pos-api/errors";
import { ok } from "@/server/pos-api/responses";
import { readPosListInput } from "@/server/pos-api/validators";
import { getTabletRuntimeMeta } from "@/server/pos-runtime";
import { getLowStockProducts } from "@/server/pos-reports";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const input = readPosListInput(new URL(request.url).searchParams, 50, 200);
    const products = await getLowStockProducts(input);
    return ok({ products, count: products.length }, undefined, {
      endpoint: "GET /api/pos/inventory/low-stock",
      businessId: input.businessId,
      threshold: input.threshold,
      runtime: getTabletRuntimeMeta()
    });
  } catch (error) {
    return toPosApiError(error);
  }
}
