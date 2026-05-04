import { NextResponse } from "next/server";
import { createOrderFromSmartPurchase } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const result = await createOrderFromSmartPurchase(body);
    return NextResponse.json({ ok: result.ok, code: result.code, message: result.message, data: result.data, warnings: result.warnings, auditEvents: result.auditEvents, meta: { source: "pc.smart_purchase.convert_to_order.v02", language: "es-MX" } }, { status: result.ok ? 200 : 409 });
  } catch (error) {
    return NextResponse.json({ ok: false, code: "CREATE_SUGGESTED_ORDER_FAILED", message: error instanceof Error ? error.message : "No se pudo crear el pedido sugerido." }, { status: 400 });
  }
}
