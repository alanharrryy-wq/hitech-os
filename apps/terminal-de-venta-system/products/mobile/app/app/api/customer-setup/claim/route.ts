import { NextResponse } from "next/server";
import { claimMobileCustomerSetup } from "@/lib/prisma-app/prisma-mobile-customer-setup";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const result = claimMobileCustomerSetup(body);
  return NextResponse.json(result, { status: result.ok ? 200 : 400 });
}
