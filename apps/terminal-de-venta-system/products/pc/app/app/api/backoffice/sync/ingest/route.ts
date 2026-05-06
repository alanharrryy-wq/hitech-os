import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { RECOGNIZED_EVENT_TOPICS, REQUIRED_EVENT_FIELDS, SUPPORTED_SCHEMA_VERSIONS } from "@/lib/backoffice/event-contract";
import { backofficeAuditMeta, readBackofficeAuditActor } from "@/lib/backoffice/security-audit";
import { persistIngestPayload } from "@/lib/backoffice/sync-ingest-store";

import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api"; // PRISMA_LICENSE_02AB_PC_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  
  // PRISMA_LICENSE_02AB_BEGIN:sync.managed
  const prismaLicenseGate = await guardPcFeatureForApi("sync.managed");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:sync.managed
return ok(
    {
      requiredFields: REQUIRED_EVENT_FIELDS,
      recognizedTopics: RECOGNIZED_EVENT_TOPICS,
      supportedSchemaVersions: SUPPORTED_SCHEMA_VERSIONS,
      statuses: ["accepted", "rejected", "duplicate", "conflict"],
      persistence: "outbox_event",
      storageModel: "OutboxEvent",
      idempotencyKey: "eventId"
    },
    {
      endpoint: "GET /api/backoffice/sync/ingest",
      permission: "sync.ingest.write",
      note: "Use POST con un evento, un arreglo de eventos o export JSON con events."
    }
  );
}

export async function POST(request: Request) {
  try {
    let body: unknown;
    try {
      body = await request.json();
    } catch {
      return fail("INVALID_JSON", "El cuerpo de la solicitud debe ser JSON válido.", 400);
    }

    const result = await persistIngestPayload(body);
    const actor = readBackofficeAuditActor(request);
    const audit = backofficeAuditMeta("sync.ingest.persist", {
      ...actor,
      entityType: "OutboxEvent",
      entityId: result.results.map((item) => item.eventId).filter(Boolean).join(",") || "ingest-batch",
      after: {
        status: result.status,
        summary: result.summary,
        persistence: result.meta.persistence,
        storageModel: result.meta.storageModel
      }
    });
    const status = result.status === "rejected" ? 422 : 200;
    return ok(result, { endpoint: "POST /api/backoffice/sync/ingest", persistence: result.meta.persistence, audit }, { status });
  } catch (error) {
    return toBackofficeError(error);
  }
}
