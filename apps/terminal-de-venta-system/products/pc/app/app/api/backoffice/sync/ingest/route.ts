import { NextResponse } from "next/server";
import { RECOGNIZED_SYNC_TOPICS, REQUIRED_SYNC_EVENT_FIELDS, SUPPORTED_SYNC_SCHEMA_VERSIONS } from "@/server/validators/sync-event-contract";
import { persistIngestPayload } from "@/lib/backoffice/sync-ingest-store";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api"; // PRISMA_LICENSE_02AB_PC_IMPORT

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function statusFrom(result: { summary: { rejected: number; conflict: number; duplicate: number } }) {
  if (result.summary.rejected > 0) return 207;
  if (result.summary.conflict > 0 || result.summary.duplicate > 0) return 202;
  return 200;
}

function safeErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}

export async function GET() {
  // PRISMA_LICENSE_02AB_BEGIN:sync.managed
  const prismaLicenseGate = await guardPcFeatureForApi("sync.managed");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:sync.managed
  return NextResponse.json({
    ok: true,
    requiredFields: REQUIRED_SYNC_EVENT_FIELDS,
    recognizedTopics: RECOGNIZED_SYNC_TOPICS,
    supportedSchemaVersions: SUPPORTED_SYNC_SCHEMA_VERSIONS,
    statuses: ["accepted", "rejected", "duplicate", "conflict"],
    lifecycleStatuses: ["received", "validated", "accepted", "projected", "reconciled", "conflict", "failed", "dead_letter"],
    persistence: "outbox_event",
    storageModel: "OutboxEvent",
    idempotencyKey: "idempotencyKey/eventId",
    endpoint: "GET /api/backoffice/sync/ingest",
    note: "Use POST con un evento, un arreglo de eventos o export JSON con events."
  });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  if (!body) {
    return NextResponse.json({ ok: false, code: "INVALID_JSON", message: "El cuerpo de la solicitud debe ser JSON válido." }, { status: 400 });
  }

  try {
    const result = await persistIngestPayload(body);
    return NextResponse.json({
      ok: result.summary.rejected === 0,
      data: result,
      endpoint: "POST /api/backoffice/sync/ingest",
      persistence: result.meta.persistence
    }, { status: statusFrom(result) });
  } catch (error) {
    return NextResponse.json({
      ok: false,
      code: "SYNC_INGEST_FAILED",
      message: safeErrorMessage(error),
      endpoint: "POST /api/backoffice/sync/ingest"
    }, { status: 500 });
  }
}
