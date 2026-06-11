import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({
    ok: false,
    code: "TABLET_BACKOFFICE_GUARDED",
    message: "Backoffice vive en PC. Tablet conserva venta local, outbox y sync sin convertirse en consola PC.",
    details: {
      surface: "tablet",
      allowedLocalContracts: ["/api/pos/*", "/api/license/*", "/api/charts/tablet/*"],
      pcBackofficeContracts: ["/api/backoffice/*", "/api/proveedores/*"],
      readOnlyGuard: true
    }
  }, { status: 409 });
}
