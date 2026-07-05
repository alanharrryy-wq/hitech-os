import { NextResponse } from "next/server";
import { resolveMobileCustomerSetup } from "@/lib/prisma-app/prisma-mobile-customer-setup";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const setupCode = url.searchParams.get("code") || url.searchParams.get("setupCode") || "";
  const result = resolveMobileCustomerSetup(setupCode);
  return NextResponse.json({ ok: "setupCode" in result, data: result, secretsExposed: false }, { status: "setupCode" in result ? 200 : 400 });
}
