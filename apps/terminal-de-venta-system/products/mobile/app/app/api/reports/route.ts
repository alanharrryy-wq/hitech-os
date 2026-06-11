import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export function GET(request: Request) {
  const target = new URL("/api/mobile/reports/daily", request.url);
  return NextResponse.redirect(target, 307);
}
