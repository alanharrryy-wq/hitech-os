import { NextResponse } from "next/server";
import { dispatchTabletOutboxOnce } from "@/server/sync/dispatcher";
import { loadPrismaTabletPcOriginConfig } from "@/server/sync/pc-origin";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(request: Request) {
  const config = loadPrismaTabletPcOriginConfig();
  const body = await request.json().catch(() => ({}));
  const force = body?.force === true;
  const result = await dispatchTabletOutboxOnce(config, { force });
  return NextResponse.json({ ...result, forced: force }, { status: result.ok ? 200 : 202 });
}
