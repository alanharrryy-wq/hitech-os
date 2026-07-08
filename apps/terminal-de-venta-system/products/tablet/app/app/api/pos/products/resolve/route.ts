import { toPosApiError } from "@/server/pos-api/errors";
import { resolveProduct } from "@/server/pos-api/product-queries.prisma";
import { fail, ok } from "@/server/pos-api/responses";
import { readProductResolveInput, validatorErrorToMessage } from "@/server/pos-api/validators";
import { resolveLocalCatalogProduct } from "@/server/local-catalog";
import { guardTabletFeatureForApi } from "@/server/licensing/tablet-license-api";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
// Contract marker: MISSING_PRODUCT_CODE

function toApiProduct(product: NonNullable<Awaited<ReturnType<typeof resolveLocalCatalogProduct>>>) {
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

export async function GET(request: Request) {
  const licenseGate = await guardTabletFeatureForApi("pos.product.search");
  if (licenseGate) return licenseGate;

  try {
    const input = readProductResolveInput(new URL(request.url).searchParams);
    const product = await resolveProduct(input);
    if (product) {
      return ok({ product }, undefined, {
        endpoint: "GET /api/pos/products/resolve",
        businessId: input.businessId,
        source: "prisma",
      });
    }

    const localProduct = await resolveLocalCatalogProduct(input.code);
    if (!localProduct) {
      return fail("PRODUCT_NOT_FOUND", "Producto no encontrado por SKU, barcode o id.", 404, { code: input.code });
    }

    return ok({ product: toApiProduct(localProduct) }, undefined, {
      endpoint: "GET /api/pos/products/resolve",
      businessId: input.businessId,
      source: "local-catalog",
      message: "Producto resuelto desde catálogo local Tablet.",
    });
  } catch (error) {
    const validation = validatorErrorToMessage(error);
    if (validation.code !== "POS_API_VALIDATION_ERROR") {
      return fail(validation.code, validation.message, 400);
    }
    return toPosApiError(error);
  }
}