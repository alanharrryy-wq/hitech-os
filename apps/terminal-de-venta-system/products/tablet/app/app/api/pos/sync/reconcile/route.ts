import { NextResponse } from "next/server";
import { reconcileTabletSentOutboxWithPc } from "@/server/sync/reconciliation";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  return NextResponse.json({
    ok: true,
    route: "/api/pos/sync/reconcile",
    mode: "tablet-sent-ack-reconciliation",
    methods: ["GET", "POST"],
    note: "POST reconcilia outbox local status=sent contra PC ingest idempotente; no controla procesos ni puertos."
  });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const result = await reconcileTabletSentOutboxWithPc({
    businessId: typeof body?.businessId === "string" ? body.businessId : null,
    limit: body?.limit,
    source: typeof body?.source === "string" ? body.source : "tablet-sync-reconcile-route"
  });
  return NextResponse.json(result, { status: result.ok ? 200 : 202 });
}
