import { NextResponse } from "next/server";
import { getSupplierDashboardSnapshot } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const snapshot = await getSupplierDashboardSnapshot();
  return NextResponse.json({ ok: true, data: snapshot.lifecycle.auditEvents, meta: { source: "pc.suppliers.audit.v02", language: "es-MX" } });
}
