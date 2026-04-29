import crypto from "node:crypto";
import { prisma } from "@/server/prisma/client";
import {
  extractIngestEvents,
  SUPPORTED_SCHEMA_VERSIONS,
  RECOGNIZED_EVENT_TOPICS,
  validateBackofficeEvent,
  type BackofficeEventEnvelope,
  type IngestClassification,
  type IngestEventResult,
  type IngestResultStatus
} from "./event-contract";
import { conflictFinding, type ConflictFinding } from "./conflicts";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asString(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function stableJsonDeep(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stableJsonDeep);
  if (!isRecord(value)) return value;
  return Object.keys(value).sort().reduce<Record<string, unknown>>((acc, key) => {
    acc[key] = stableJsonDeep(value[key]);
    return acc;
  }, {});
}

function stableJson(value: unknown): string {
  return JSON.stringify(stableJsonDeep(value));
}

function rejectedId(candidate: unknown) {
  const hash = crypto.createHash("sha256").update(stableJson(candidate)).digest("hex").slice(0, 24);
  return `rejected_${hash}`;
}

function aggregateIdFor(event: BackofficeEventEnvelope) {
  const payload = event.payload;
  return (
    asString(event.aggregateId) ||
    asString(payload.saleId) ||
    asString(payload.productId) ||
    asString(payload.ticketId) ||
    event.eventId
  );
}

function resultSummary(results: IngestEventResult[]): Record<IngestResultStatus, number> {
  const summary: Record<IngestResultStatus, number> = {
    accepted: 0,
    rejected: 0,
    duplicate: 0,
    conflict: 0
  };
  for (const result of results) summary[result.status] += 1;
  return summary;
}

function topStatus(summary: Record<IngestResultStatus, number>): IngestResultStatus {
  if (summary.rejected > 0) return "rejected";
  if (summary.conflict > 0) return "conflict";
  if (summary.duplicate > 0) return "duplicate";
  return "accepted";
}

function conflictPayload(conflicts: ConflictFinding[], errors: string[]) {
  return JSON.stringify({
    conflicts: conflicts.map((conflict) => ({
      code: conflict.code,
      severity: conflict.severity,
      detail: conflict.detail
    })),
    errors
  });
}

async function persistRejected(candidate: unknown, errors: string[], conflicts: ConflictFinding[]): Promise<IngestEventResult> {
  const eventId = isRecord(candidate) ? asString(candidate.eventId) || null : null;
  const topic = isRecord(candidate) ? asString(candidate.topic) || null : null;
  const id = eventId || rejectedId(candidate);
  const businessId = isRecord(candidate) ? asString(candidate.businessId) || "unknown_business" : "unknown_business";
  const aggregateId = eventId || id;

  const existing = await prisma.outboxEvent.findUnique({ where: { id } });
  if (existing) {
    return {
      eventId: id,
      topic,
      status: "duplicate",
      conflicts: [conflictFinding("duplicate_event", "El eventId o hash estable del rechazo ya existe en PC.")],
      errors: []
    };
  }

  await prisma.outboxEvent.create({
    data: {
      id,
      businessId,
      topic: topic || "invalid_schema",
      aggregateId,
      payloadJson: JSON.stringify({ rejected: candidate }),
      status: "failed",
      attempts: 1,
      createdAt: new Date(),
      lastError: conflictPayload(conflicts.length ? conflicts : [conflictFinding("invalid_schema", "Evento rechazado por contrato.")], errors)
    }
  });

  return {
    eventId: id,
    topic,
    status: "rejected",
    conflicts: conflicts.length ? conflicts : [conflictFinding("invalid_schema", "Evento rechazado por contrato.")],
    errors
  };
}

async function persistAccepted(event: BackofficeEventEnvelope, conflicts: ConflictFinding[]): Promise<IngestEventResult> {
  const existing = await prisma.outboxEvent.findUnique({ where: { id: event.eventId } });
  if (existing) {
    return {
      eventId: event.eventId,
      topic: event.topic,
      status: "duplicate",
      conflicts: [conflictFinding("duplicate_event", "PC ya tiene persistido este eventId.")],
      errors: []
    };
  }

  await prisma.outboxEvent.create({
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

  return {
    eventId: event.eventId,
    topic: event.topic,
    status: conflicts.length ? "conflict" : "accepted",
    conflicts,
    errors: []
  };
}

export async function persistIngestPayload(input: unknown): Promise<IngestClassification> {
  const candidates = extractIngestEvents(input);
  const seenInBatch = new Set<string>();
  const results: IngestEventResult[] = [];

  for (const candidate of candidates) {
    const validation = validateBackofficeEvent(candidate);

    if (validation.event && seenInBatch.has(validation.event.eventId)) {
      results.push({
        eventId: validation.event.eventId,
        topic: validation.event.topic,
        status: "duplicate",
        conflicts: [conflictFinding("duplicate_event", "El mismo eventId aparece más de una vez en el lote recibido.")],
        errors: []
      });
      continue;
    }

    if (!validation.event) {
      results.push(await persistRejected(candidate, validation.errors, validation.conflicts));
      continue;
    }

    seenInBatch.add(validation.event.eventId);
    results.push(await persistAccepted(validation.event, validation.conflicts));
  }

  const summary = resultSummary(results);

  return {
    status: topStatus(summary),
    eventsReceived: candidates.length,
    results,
    summary,
    meta: {
      persistence: "outbox_event",
      durable: true,
      storageModel: "OutboxEvent",
      idempotencyKey: "eventId",
      supportedSchemaVersions: SUPPORTED_SCHEMA_VERSIONS,
      recognizedTopics: RECOGNIZED_EVENT_TOPICS,
      note: "PC persiste ingest en OutboxEvent con idempotencia por eventId; rechazados sin eventId usan hash estable del payload."
    }
  };
}
