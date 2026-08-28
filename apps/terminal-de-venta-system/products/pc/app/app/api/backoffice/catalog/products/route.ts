import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { createCatalogProduct } from "@/server/services/catalog-mutations.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("catalog.write");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const product = await createCatalogProduct(body);
    return ok({ product }, { endpoint: "POST /api/backoffice/catalog/products", persistence: "canonical_prisma", wave: 3 }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message === "CATALOG_SKU_REQUIRED") return fail("CATALOG_SKU_REQUIRED", "Falta un SKU válido.", 400);
    if (error instanceof Error && error.message === "CATALOG_NAME_REQUIRED") return fail("CATALOG_NAME_REQUIRED", "Falta el nombre del producto.", 400);
    if (error instanceof Error && error.message === "CATALOG_CATEGORY_REQUIRED") return fail("CATALOG_CATEGORY_REQUIRED", "Falta la categoría del producto.", 400);
    if (error instanceof Error && ["CATALOG_PRICE_INVALID", "CATALOG_COST_INVALID", "CATALOG_STOCK_INVALID"].includes(error.message)) return fail(error.message, "Los importes y existencias deben ser enteros no negativos.", 400);
    if (error instanceof Error && error.message === "CATALOG_SKU_EXISTS") return fail("CATALOG_SKU_EXISTS", "Ese SKU ya existe en el catálogo.", 409);
    return toBackofficeError(error);
  }
}
