import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getSupplierOperationsSnapshot } from "@/lib/suppliers/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const suppliers = await getSupplierOperationsSnapshot();
    return ok(suppliers, { endpoint: "GET /api/backoffice/suppliers", aliasOf: "GET /api/proveedores/operacion", source: "pc.suppliers.lifecycle.v02", readOnly: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
