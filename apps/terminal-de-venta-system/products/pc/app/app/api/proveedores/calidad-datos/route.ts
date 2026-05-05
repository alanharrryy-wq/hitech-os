import { NextResponse } from "next/server";
import { getSupplierDataQualityReport } from "../../../../src/lib/suppliers/server";

export async function GET() {
  const report = await getSupplierDataQualityReport();
  return NextResponse.json({ ok: true, data: report });
}
