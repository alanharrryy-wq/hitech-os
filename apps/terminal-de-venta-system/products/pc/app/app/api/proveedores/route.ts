import { NextResponse } from "next/server";
import { getSupplierOperationsSnapshot } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const snapshot = await getSupplierOperationsSnapshot();
  return NextResponse.json({
    ok: true,
    data: snapshot,
    meta: {
      endpoint: "GET /api/proveedores",
      aliasOf: "GET /api/proveedores/operacion",
      source: "pc.suppliers.lifecycle.v02",
      readOnly: true,
      language: "es-MX"
    }
  });
}
