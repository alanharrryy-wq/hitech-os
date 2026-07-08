import { toPosApiError } from "@/server/pos-api/errors";
import { searchProducts } from "@/server/pos-api/product-queries.prisma";
import { fail, ok } from "@/server/pos-api/responses";
import { readProductSearchInput } from "@/server/pos-api/validators";
import { listLocalCatalogProducts } from "@/server/local-catalog";
import { guardTabletFeatureForApi } from "@/server/licensing/tablet-license-api";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function toApiProduct(product: Awaited<ReturnType<typeof listLocalCatalogProducts>>[number]) {
  return {
    id: product.id,
    businessId: product.businessId,
    sku: product.sku,
    name: product.name,
    category: product.category || "Local",
    barcode: product.barcode,
    barcodes: product.barcode ? [product.barcode] : [],
    priceCents: product.priceCents,
    price: product.priceCents / 100,
    costCents: 0,
    stockOnHand: product.stockOnHand,
    lowStockThreshold: product.lowStockThreshold,
    isActive: product.isActive,
    updatedAt: product.updatedAt,
  };
}

async function searchLocalFallback(input: ReturnType<typeof readProductSearchInput>) {
  const local = await listLocalCatalogProducts({ q: input.q, includeInactive: input.includeInactive });
  return local.slice(0, input.limit).map(toApiProduct);
}

export async function GET(request: Request) {
  const licenseGate = await guardTabletFeatureForApi("pos.product.search");
  if (licenseGate) return licenseGate;

  try {
    const input = readProductSearchInput(new URL(request.url).searchParams);
    let products = await searchProducts(input);
    let source: "prisma" | "local-catalog" = "prisma";

    if (!products.length) {
      products = await searchLocalFallback(input);
      source = "local-catalog";
    }

    return ok({ products, count: products.length }, undefined, {
      endpoint: "GET /api/pos/products/search",
      query: input.q,
      businessId: input.businessId,
      source,
      message: source === "local-catalog" ? "Catálogo local Tablet usado como respaldo operativo." : "Productos consultados en DB local POS.",
    });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_DATE") {
      return fail("INVALID_DATE", "Fecha invalida.", 400);
    }
    return toPosApiError(error);
  }
}