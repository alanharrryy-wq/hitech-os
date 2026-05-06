import { NextResponse } from "next/server";
import { getSupplierOperationsSnapshot } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const snapshot = await getSupplierOperationsSnapshot();
  return NextResponse.json({ ok: true, data: snapshot, meta: { source: "pc.suppliers.lifecycle.v02", language: "es-MX" } });
}
