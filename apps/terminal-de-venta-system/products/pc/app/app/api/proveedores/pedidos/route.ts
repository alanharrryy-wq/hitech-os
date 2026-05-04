import { NextResponse } from "next/server";
import { getSupplierDashboardSnapshot } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const snapshot = await getSupplierDashboardSnapshot();
  return NextResponse.json({ ok: true, data: { orders: snapshot.openOrders, workflow: snapshot.lifecycle.orderWorkflow }, meta: { source: "pc.suppliers.orders.v02", language: "es-MX" } });
}
