import { NextResponse } from "next/server";
import { dispatchTabletOutboxOnce } from "@/server/sync/dispatcher";
import { loadPrismaTabletPcOriginConfig } from "@/server/sync/pc-origin";

export const dynamic = "force-dynamic";

export async function POST() {
  const config = loadPrismaTabletPcOriginConfig();
  const result = await dispatchTabletOutboxOnce(config);
  return NextResponse.json(result, { status: result.ok ? 200 : 202 });
}
