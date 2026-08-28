import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { createSupplierRecord } from "@/server/services/supplier-records.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("purchase.write");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const supplier = await createSupplierRecord(body);
    return ok({ supplier }, { endpoint: "POST /api/backoffice/suppliers/records", persistence: "canonical_prisma", wave: 3 }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message === "SUPPLIER_NAME_REQUIRED") return fail("SUPPLIER_NAME_REQUIRED", "Falta un nombre válido para el proveedor.", 400);
    if (error instanceof Error && error.message === "SUPPLIER_STATUS_INVALID") return fail("SUPPLIER_STATUS_INVALID", "El estado del proveedor no es válido.", 400);
    if (error instanceof Error && error.message === "SUPPLIER_NAME_EXISTS") return fail("SUPPLIER_NAME_EXISTS", "Ya existe un proveedor con ese nombre.", 409);
    return toBackofficeError(error);
  }
}
