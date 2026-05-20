import { NextResponse } from "next/server";
import { checkPrismaPcHealth, loadPrismaTabletPcOriginConfig } from "@/server/sync/pc-origin";

export const dynamic = "force-dynamic";

export async function GET() {
  const result = await checkPrismaPcHealth(loadPrismaTabletPcOriginConfig());
  return NextResponse.json(result, { status: 200 });
}
