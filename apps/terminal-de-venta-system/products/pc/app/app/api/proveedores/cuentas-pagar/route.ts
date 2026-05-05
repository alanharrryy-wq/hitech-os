import { NextResponse } from "next/server";
import { getSupplierDashboardSnapshot } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const snapshot = await getSupplierDashboardSnapshot();
  return NextResponse.json({ ok: true, data: { payables: snapshot.payables, plan: snapshot.lifecycle.payablePlan }, meta: { source: "pc.suppliers.payables.v02", language: "es-MX" } });
}
