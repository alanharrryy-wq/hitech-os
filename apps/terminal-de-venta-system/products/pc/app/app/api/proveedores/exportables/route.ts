import { NextResponse } from "next/server";
import { getSupplierExportBundle } from "../../../../src/lib/suppliers/server";

export async function GET() {
  const bundle = await getSupplierExportBundle();
  return NextResponse.json({ ok: true, data: bundle });
}
