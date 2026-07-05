import { NextResponse } from "next/server";
import { claimTabletCustomerSetup } from "@/server/licensing/tablet-customer-setup";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const result = claimTabletCustomerSetup(body);
  return NextResponse.json(result, { status: result.ok ? 200 : 400 });
}
