import { NextResponse } from "next/server";
import { getTabletCatalogPullStatus, pullCatalogDeltaFromPc } from "@/server/sync/catalog-pull";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function inputFromUrl(request: Request) {
  const url = new URL(request.url);
  return {
    pcBusinessId: url.searchParams.get("pcBusinessId"),
    targetBusinessId: url.searchParams.get("targetBusinessId"),
    terminalId: url.searchParams.get("terminalId"),
    storeId: url.searchParams.get("storeId")
  };
}

export async function GET(request: Request) {
  const data = await getTabletCatalogPullStatus(inputFromUrl(request));
  return NextResponse.json({ ok: true, data, meta: { endpoint: "GET /api/pos/sync/pull" } });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const result = await pullCatalogDeltaFromPc({
    mode: typeof body?.mode === "string" ? body.mode : "delta",
    resetCheckpoint: body?.resetCheckpoint === true,
    pcBusinessId: typeof body?.pcBusinessId === "string" ? body.pcBusinessId : null,
    targetBusinessId: typeof body?.targetBusinessId === "string" ? body.targetBusinessId : null,
    terminalId: typeof body?.terminalId === "string" ? body.terminalId : null,
    storeId: typeof body?.storeId === "string" ? body.storeId : null,
    cursor: typeof body?.cursor === "string" ? body.cursor : null,
    limit: body?.limit,
    requestedBy: typeof body?.requestedBy === "string" ? body.requestedBy : "tablet-sync-screen"
  });
  const status = result.ok ? 200 : 202;
  return NextResponse.json(result, { status });
}
