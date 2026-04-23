import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    app: "tablet",
    status: "ok",
    version: "6.1.0",
    readyFor: ["preview-shell", "domain-iteration", "prisma-wiring"]
  });
}
