import { prisma } from "@/server/prisma/client";
import {
  extractSyncEvents,
  validateSyncEventEnvelope,
  syncPayloadFingerprint,
  RECOGNIZED_SYNC_TOPICS,
  SUPPORTED_SYNC_SCHEMA_VERSIONS,
  type SyncConflictFinding,
  type SyncEventEnvelope,
  type SyncEventStatus,
  type SyncIngestClassification,
  type SyncIngestResult
} from "@/server/validators/sync-event-contract";

const DEFAULT_REJECTED_SYNC_BUSINESS_ID = "biz_hitech_default";

function aggregateIdFor(event: SyncEventEnvelope) {
  const payload = event.payload;
  const pick = (value: unknown) => (typeof value === "string" && value.trim() ? value.trim() : "");
  return event.aggregateId || pick(payload.saleId) || pick(payload.productId) || pick(payload.ticketId) || event.eventId;
}

function conflictPayload(conflicts: SyncConflictFinding[], errors: string[]) {
  return JSON.stringify({ conflicts, errors });
}

function resultSummary(results: SyncIngestResult[]): Record<SyncEventStatus, number> {
  const summary: Record<SyncEventStatus, number> = { accepted: 0, duplicate: 0, conflict: 0, rejected: 0 };
  for (const result of results) summary[result.status] += 1;
  return summary;
}

function topStatus(summary: Record<SyncEventStatus, number>): SyncEventStatus {
  if (summary.rejected > 0) return "rejected";
  if (summary.conflict > 0) return "conflict";
  if (summary.duplicate > 0) return "duplicate";
  return "accepted";
}

async function existsOutbox(id: string) {
  const db = prisma as any;
  return Boolean(await db.outboxEvent.findUnique({ where: { id } }));
}

async function persistRejected(candidate: unknown, errors: string[], conflicts: SyncConflictFinding[]): Promise<SyncIngestResult> {
  const id = `rejected_${syncPayloadFingerprint(candidate).slice(0, 28)}`;
  if (await existsOutbox(id)) {
    return { eventId: id, topic: null, status: "duplicate", conflicts, errors: [] };
  }
  const db = prisma as any;
  await db.outboxEvent.create({
    data: {
      id,
      businessId: DEFAULT_REJECTED_SYNC_BUSINESS_ID,
      topic: "invalid_schema",
      aggregateId: id,
      payloadJson: JSON.stringify({ rejected: candidate }),
      status: "failed",
      attempts: 1,
      createdAt: new Date(),
      lastError: conflictPayload(conflicts, errors)
    }
  });
  return { eventId: id, topic: null, status: "rejected", conflicts, errors };
}

async function persistEvent(event: SyncEventEnvelope, conflicts: SyncConflictFinding[]): Promise<SyncIngestResult> {
  if (await existsOutbox(event.eventId)) {
    return {
      eventId: event.eventId,
      topic: event.topic,
      status: "duplicate",
      conflicts: [{ code: "duplicate_event", label: "Evento duplicado", severity: "warning", detail: "PC ya tiene persistido este eventId." }],
      errors: []
    };
  }
  const db = prisma as any;
  await db.outboxEvent.create({
    data: {
      id: event.eventId,
      businessId: event.businessId,
      topic: event.topic,
      aggregateId: aggregateIdFor(event),
      payloadJson: JSON.stringify(event),
      status: conflicts.length ? "conflict" : "acked",
      attempts: 1,
      createdAt: new Date(event.occurredAt),
      lastError: conflicts.length ? conflictPayload(conflicts, []) : null
    }
  });
  return { eventId: event.eventId, topic: event.topic, status: conflicts.length ? "conflict" : "accepted", conflicts, errors: [] };
}

export async function persistSyncIngestPayload(input: unknown): Promise<SyncIngestClassification> {
  const candidates = extractSyncEvents(input);
  const seenInBatch = new Set<string>();
  const results: SyncIngestResult[] = [];
  for (const candidate of candidates) {
    const validation = validateSyncEventEnvelope(candidate);
    if (validation.event && seenInBatch.has(validation.event.eventId)) {
      results.push({
        eventId: validation.event.eventId,
        topic: validation.event.topic,
        status: "duplicate",
        conflicts: [{ code: "duplicate_event", label: "Evento duplicado", severity: "warning", detail: "El eventId aparece repetido dentro del mismo lote." }],
        errors: []
      });
      continue;
    }
    if (!validation.event) {
      results.push(await persistRejected(candidate, validation.errors, validation.conflicts));
      continue;
    }
    seenInBatch.add(validation.event.eventId);
    results.push(await persistEvent(validation.event, validation.conflicts));
  }
  const summary = resultSummary(results);
  return {
    status: topStatus(summary),
    eventsReceived: candidates.length,
    results,
    summary,
    meta: {
      persistence: "outbox_event",
      idempotencyKey: "eventId",
      recognizedTopics: RECOGNIZED_SYNC_TOPICS,
      supportedSchemaVersions: SUPPORTED_SYNC_SCHEMA_VERSIONS,
      note: "PC persiste ingest en OutboxEvent con idempotencia por eventId."
    }
  };
}
