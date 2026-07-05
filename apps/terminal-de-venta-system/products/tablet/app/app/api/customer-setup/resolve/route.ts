import { NextResponse } from "next/server";
import { resolveTabletCustomerSetup } from "@/server/licensing/tablet-customer-setup";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const setupCode = url.searchParams.get("code") || url.searchParams.get("setupCode") || "";
  const result = resolveTabletCustomerSetup(setupCode);
  return NextResponse.json({ ok: "setupCode" in result, data: result, secretsExposed: false }, { status: "setupCode" in result ? 200 : 400 });
}
