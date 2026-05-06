import { NextResponse } from "next/server";
import { registerPayablePayment } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const result = await registerPayablePayment(body);
    return NextResponse.json({ ok: result.ok, code: result.code, message: result.message, data: result.data, warnings: result.warnings, auditEvents: result.auditEvents, meta: { source: "pc.suppliers.payables.payment.v02", language: "es-MX" } }, { status: result.ok ? 200 : 409 });
  } catch (error) {
    return NextResponse.json({ ok: false, code: "REGISTER_PAYMENT_FAILED", message: error instanceof Error ? error.message : "No se pudo registrar el pago." }, { status: 400 });
  }
}
