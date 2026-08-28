import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { deleteSupplierRecord, getSupplierRecord, updateSupplierRecord } from "@/server/services/supplier-records.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type RouteContext = { params: Promise<{ supplierId: string }> };
const supplierIdFrom = (context: RouteContext) => context.params.then(({ supplierId }) => supplierId.trim());

export async function GET(_: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const supplierId = await supplierIdFrom(context);
    if (!supplierId) return fail("SUPPLIER_ID_REQUIRED", "Falta el proveedor solicitado.", 400);
    const supplier = await getSupplierRecord(supplierId);
    if (!supplier) return fail("SUPPLIER_NOT_FOUND", "No existe el proveedor solicitado.", 404);
    return ok({ supplier }, { endpoint: "GET /api/backoffice/suppliers/records/:supplierId", persistence: "canonical_prisma", wave: 3 });
  } catch (error) { return toBackofficeError(error); }
}

export async function PATCH(request: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("purchase.write");
    if (licenseGate) return licenseGate;
    const supplierId = await supplierIdFrom(context);
    if (!supplierId) return fail("SUPPLIER_ID_REQUIRED", "Falta el proveedor solicitado.", 400);
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const supplier = await updateSupplierRecord(supplierId, body);
    if (!supplier) return fail("SUPPLIER_NOT_FOUND", "No existe el proveedor solicitado.", 404);
    return ok({ supplier }, { endpoint: "PATCH /api/backoffice/suppliers/records/:supplierId", persistence: "canonical_prisma", wave: 3 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message === "SUPPLIER_UPDATE_EMPTY") return fail("SUPPLIER_UPDATE_EMPTY", "No hay cambios para guardar.", 400);
    if (error instanceof Error && error.message === "SUPPLIER_NAME_EXISTS") return fail("SUPPLIER_NAME_EXISTS", "Ya existe un proveedor con ese nombre.", 409);
    if (error instanceof Error && error.message.startsWith("SUPPLIER_")) return fail(error.message, "Los datos del proveedor no son válidos.", 400);
    return toBackofficeError(error);
  }
}

export async function DELETE(_: Request, context: RouteContext) {
  try {
    const licenseGate = await guardPcFeatureForApi("purchase.write");
    if (licenseGate) return licenseGate;
    const supplierId = await supplierIdFrom(context);
    if (!supplierId) return fail("SUPPLIER_ID_REQUIRED", "Falta el proveedor solicitado.", 400);
    const supplier = await deleteSupplierRecord(supplierId);
    if (!supplier) return fail("SUPPLIER_NOT_FOUND", "No existe el proveedor solicitado.", 404);
    return ok({ supplier, deleted: true }, { endpoint: "DELETE /api/backoffice/suppliers/records/:supplierId", persistence: "canonical_prisma", wave: 3 });
  } catch (error) {
    if (error instanceof Error && error.message === "SUPPLIER_IN_USE") return fail("SUPPLIER_IN_USE", "El proveedor tiene relaciones operativas y no puede eliminarse.", 409);
    return toBackofficeError(error);
  }
}
