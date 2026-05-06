import { NextResponse } from "next/server";
import { getSupplierDashboardSnapshot } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const snapshot = await getSupplierDashboardSnapshot();
  return NextResponse.json({ ok: true, data: { receivingQueue: snapshot.receivingQueue, movementPreview: snapshot.lifecycle.movementPreview }, meta: { source: "pc.suppliers.receiving.v02", language: "es-MX" } });
}
