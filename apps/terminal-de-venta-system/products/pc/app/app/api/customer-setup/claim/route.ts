import { NextResponse } from "next/server";
import { claimPcCustomerSetup } from "@/server/licensing/pc-customer-setup";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const result = claimPcCustomerSetup(body);
  return NextResponse.json(result, { status: result.ok ? 200 : 400 });
}
