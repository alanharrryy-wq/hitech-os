import { NextResponse } from "next/server";
import { classifySyncIngestPayload } from "@/server/validators/sync-event-contract";
import { persistSyncIngestPayload } from "@/server/services/sync-ingest.service";

function statusFrom(result: { summary: { rejected: number; conflict: number; duplicate: number } }) {
  if (result.summary.rejected > 0) return 207;
  if (result.summary.conflict > 0 || result.summary.duplicate > 0) return 202;
  return 200;
}

export async function GET() {
  return NextResponse.json({
    ok: true,
    route: "/api/sync/ingest",
    mode: "pc-backoffice-sync-ingest",
    methods: ["GET", "POST"],
    dryRun: "POST /api/sync/ingest?dryRun=1 classifica sin persistir",
    persistence: "OutboxEvent por eventId cuando dryRun no está activo"
  });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  if (!body) {
    return NextResponse.json({ ok: false, code: "INVALID_JSON", message: "Body JSON inválido o vacío." }, { status: 400 });
  }

  const url = new URL(request.url);
  const dryRun = url.searchParams.get("dryRun") === "1" || url.searchParams.get("dryRun") === "true";

  try {
    const result = dryRun ? classifySyncIngestPayload(body) : await persistSyncIngestPayload(body);
    return NextResponse.json({ ok: result.summary.rejected === 0, dryRun, data: result }, { status: statusFrom(result) });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Error desconocido en sync ingest.";
    return NextResponse.json({ ok: false, code: "SYNC_INGEST_FAILED", message }, { status: 500 });
  }
}
