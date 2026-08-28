import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { deleteCatalogProduct, getCatalogProduct, updateCatalogProduct } from "@/server/services/catalog-mutations.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type RouteContext = { params: Promise<{ productId: string }> };
const productIdFrom = (context: RouteContext) => context.params.then(({ productId }) => productId.trim());

export async function GET(_: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const productId = await productIdFrom(context);
    if (!productId) return fail("CATALOG_PRODUCT_ID_REQUIRED", "Falta el producto solicitado.", 400);
    const product = await getCatalogProduct(productId);
    if (!product) return fail("CATALOG_PRODUCT_NOT_FOUND", "No existe el producto solicitado.", 404);
    return ok({ product }, { endpoint: "GET /api/backoffice/catalog/products/:productId", persistence: "canonical_prisma", wave: 3 });
  } catch (error) { return toBackofficeError(error); }
}

export async function PATCH(request: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("catalog.write");
    if (licenseGate) return licenseGate;
    const productId = await productIdFrom(context);
    if (!productId) return fail("CATALOG_PRODUCT_ID_REQUIRED", "Falta el producto solicitado.", 400);
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const product = await updateCatalogProduct(productId, body);
    if (!product) return fail("CATALOG_PRODUCT_NOT_FOUND", "No existe el producto solicitado.", 404);
    return ok({ product }, { endpoint: "PATCH /api/backoffice/catalog/products/:productId", persistence: "canonical_prisma", wave: 3 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message === "CATALOG_UPDATE_EMPTY") return fail("CATALOG_UPDATE_EMPTY", "No hay cambios para guardar.", 400);
    if (error instanceof Error && error.message === "CATALOG_SKU_EXISTS") return fail("CATALOG_SKU_EXISTS", "Ese SKU ya existe en el catálogo.", 409);
    if (error instanceof Error && error.message.startsWith("CATALOG_")) return fail(error.message, "Los datos del producto no son válidos.", 400);
    return toBackofficeError(error);
  }
}

export async function DELETE(_: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("catalog.write");
    if (licenseGate) return licenseGate;
    const productId = await productIdFrom(context);
    if (!productId) return fail("CATALOG_PRODUCT_ID_REQUIRED", "Falta el producto solicitado.", 400);
    const product = await deleteCatalogProduct(productId);
    if (!product) return fail("CATALOG_PRODUCT_NOT_FOUND", "No existe el producto solicitado.", 404);
    return ok({ product, deleted: true }, { endpoint: "DELETE /api/backoffice/catalog/products/:productId", persistence: "canonical_prisma", wave: 3 });
  } catch (error) {
    if (error instanceof Error && error.message === "CATALOG_PRODUCT_IN_USE") return fail("CATALOG_PRODUCT_IN_USE", "El producto tiene movimientos o relaciones operativas y no puede eliminarse.", 409);
    return toBackofficeError(error);
  }
}
