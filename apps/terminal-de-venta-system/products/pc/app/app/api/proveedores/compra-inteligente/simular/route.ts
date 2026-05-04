import { NextResponse } from "next/server";
import { runSmartPurchaseSimulation } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const simulation = await runSmartPurchaseSimulation(body);
    return NextResponse.json({ ok: true, data: simulation, meta: { source: "pc.smart_purchase.simulator.v02", language: "es-MX" } });
  } catch (error) {
    return NextResponse.json({ ok: false, code: "SMART_PURCHASE_SIMULATION_FAILED", message: error instanceof Error ? error.message : "No se pudo simular la compra." }, { status: 400 });
  }
}
