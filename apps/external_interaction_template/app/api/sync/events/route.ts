import { NextResponse } from "next/server";

import { listSyncCenterData } from "@/lib/services/actions";

export async function GET() {
  const data = await listSyncCenterData();
  return NextResponse.json(data);
}
