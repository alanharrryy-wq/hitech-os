import { NextResponse } from "next/server";
import { getSupplierDashboardSnapshot } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const snapshot = await getSupplierDashboardSnapshot();
  return NextResponse.json({ ok: true, data: snapshot.lifecycle.surfaceSignals, meta: { source: "pc.suppliers.surface_signals.v02", language: "es-MX", rule: "Tablet y App movil reciben solo senales ligeras." } });
}
