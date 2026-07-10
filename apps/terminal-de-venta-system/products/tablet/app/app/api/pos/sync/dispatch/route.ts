import { NextResponse } from "next/server";
import { dispatchTabletOutboxOnce } from "@/server/sync/dispatcher";
import { loadPrismaTabletPcOriginConfig } from "@/server/sync/pc-origin";
import { reconcileTabletSentOutboxWithPc } from "@/server/sync/reconciliation";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(request: Request) {
  const config = loadPrismaTabletPcOriginConfig();
  const body = await request.json().catch(() => ({}));
  const force = body?.force === true;
  const reconcileSent = body?.reconcileSent !== false;
  const result = await dispatchTabletOutboxOnce(config, { force });
  const reconciliation = reconcileSent
    ? await reconcileTabletSentOutboxWithPc({
      config,
      businessId: typeof body?.businessId === "string" ? body.businessId : null,
      limit: body?.reconcileLimit,
      source: typeof body?.source === "string" ? body.source : "tablet-sync-dispatch"
    }).catch((error) => ({
      ok: false,
      reason: "reconciliation_failed",
      url: null,
      checked: 0,
      sent: 0,
      counts: { acked: 0, conflict: 0, failed: 0, skipped: 0 },
      results: [],
      errors: [error instanceof Error ? error.message : "Unknown reconciliation error"]
    }))
    : null;
  const reconciliationConfirmed = (reconciliation?.counts?.acked ?? 0) > 0;
  const ok = result.ok || reconciliationConfirmed;
  return NextResponse.json({ ...result, ok, forced: force, reconciliation }, { status: ok ? 200 : 202 });
}
