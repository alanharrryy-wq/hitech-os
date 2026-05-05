import { NextResponse } from "next/server";
import { getSupplierDashboardSnapshot } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const snapshot = await getSupplierDashboardSnapshot();
  return NextResponse.json({
    ok: true,
    data: {
      generatedAt: snapshot.generatedAt,
      recommendations: snapshot.recommendations,
      signals: snapshot.signals,
      payables: snapshot.payables,
      openOrders: snapshot.openOrders,
      receivingQueue: snapshot.receivingQueue,
      lifecycle: snapshot.lifecycle,
      inventoryBridge: snapshot.inventoryBridge
    },
    meta: {
      source: "pc.suppliers.smart_purchase.inventory_bridge_v11",
      language: "es-MX",
      rule: "PRISMA recomienda; el usuario aprueba. Tablet vende local y solo recibe senales ligeras."
    }
  });
}
