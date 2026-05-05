import { NextResponse } from "next/server";
import { confirmReceivingFromOrder } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const result = await confirmReceivingFromOrder(body);
    return NextResponse.json({ ok: result.ok, code: result.code, message: result.message, data: result.data, warnings: result.warnings, auditEvents: result.auditEvents, meta: { source: "pc.suppliers.receiving.confirm.v02", language: "es-MX" } }, { status: result.ok ? 200 : 409 });
  } catch (error) {
    return NextResponse.json({ ok: false, code: "CONFIRM_RECEIVING_FAILED", message: error instanceof Error ? error.message : "No se pudo confirmar la recepcion." }, { status: 400 });
  }
}
