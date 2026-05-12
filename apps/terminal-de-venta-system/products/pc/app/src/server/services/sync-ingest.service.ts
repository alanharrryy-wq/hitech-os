import { prisma } from "@/server/prisma/client";
import { projectAcceptedSyncEvent } from "@/server/services/sync-projectors.service";
import { recordSyncObservability } from "@/server/services/sync-observability.service";
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
  type SyncIngestResult,
  type SyncLifecycleState
} from "@/server/validators/sync-event-contract";

const DEFAULT_REJECTED_SYNC_BUSINESS_ID = "biz_hitech_default";

function aggregateIdFor(event: SyncEventEnvelope) {
  const payload = event.payload;
  const pick = (value: unknown) => (typeof value === "string" && value.trim() ? value.trim() : "");
  return event.aggregateId || pick(payload.saleId) || pick(payload.productId) || pick(payload.ticketId) || event.eventId;
}

function diagnosticsPayload(input: {
  lifecycleStatus: SyncLifecycleState;
  conflicts: SyncConflictFinding[];
  errors: string[];
  diagnostics?: string[];
  projectedModels?: string[];
}) {
  return JSON.stringify({
    lifecycleStatus: input.lifecycleStatus,
    conflicts: input.conflicts,
    errors: input.errors,
    diagnostics: input.diagnostics ?? [],
    projectedModels: input.projectedModels ?? []
  });
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

function statusForLifecycle(lifecycleStatus: SyncLifecycleState): string {
  if (lifecycleStatus === "conflict") return "conflict";
  if (lifecycleStatus === "failed" || lifecycleStatus === "dead_letter") return "failed";
  if (lifecycleStatus === "projected" || lifecycleStatus === "reconciled") return "acked";
  return "sent";
}

async function findExistingEvent(tx: any, event: SyncEventEnvelope) {
  if (event.idempotencyKey) {
    const byIdempotencyKey = await tx.outboxEvent.findFirst({
      where: { businessId: event.businessId, idempotencyKey: event.idempotencyKey },
      orderBy: { createdAt: "desc" }
    });
    if (byIdempotencyKey) return byIdempotencyKey;
  }

  return tx.outboxEvent.findUnique({ where: { id: event.eventId } });
}

function duplicateResult(event: SyncEventEnvelope, existing: any): SyncIngestResult {
  return {
    eventId: event.eventId,
    topic: event.topic,
    status: "duplicate",
    lifecycleStatus: existing.lifecycleStatus ?? "reconciled",
    conflicts: [{ code: "duplicate_event", label: "Evento duplicado", severity: "warning", detail: "PC ya procesó este businessId + idempotencyKey o eventId; no se crea otro ledger." }],
    errors: [],
    diagnostics: ["ALREADY_PROCESSED", event.idempotencyKey ? "DUPLICATE_IDEMPOTENCY_KEY" : "DUPLICATE_EVENT_ID"]
  };
}

async function persistRejected(tx: any, candidate: unknown, errors: string[], conflicts: SyncConflictFinding[]): Promise<SyncIngestResult> {
  const id = `rejected_${syncPayloadFingerprint(candidate).slice(0, 28)}`;
  const existing = await tx.outboxEvent.findUnique({ where: { id } });
  if (existing) {
    return { eventId: id, topic: null, status: "duplicate", lifecycleStatus: "dead_letter", conflicts, errors: [], diagnostics: ["REJECTED_EVENT_ALREADY_PERSISTED"] };
  }
  const now = new Date();
  await tx.outboxEvent.create({
    data: {
      id,
      businessId: DEFAULT_REJECTED_SYNC_BUSINESS_ID,
      topic: "invalid_schema",
      eventType: "invalid_schema",
      aggregateId: id,
      idempotencyKey: id,
      payloadJson: JSON.stringify({ rejected: candidate }),
      status: "failed",
      lifecycleStatus: "dead_letter",
      attempts: 1,
      createdAt: now,
      receivedAt: now,
      failedAt: now,
      deadLetterAt: now,
      conflictCode: conflicts[0]?.code ?? "invalid_schema",
      diagnosticsJson: diagnosticsPayload({ lifecycleStatus: "dead_letter", conflicts, errors, diagnostics: ["EVENT_REJECTED_BY_CONTRACT"] }),
      lastError: diagnosticsPayload({ lifecycleStatus: "dead_letter", conflicts, errors })
    }
  });
  return { eventId: id, topic: null, status: "rejected", lifecycleStatus: "dead_letter", conflicts, errors, diagnostics: ["EVENT_REJECTED_BY_CONTRACT"] };
}

async function persistConflict(tx: any, event: SyncEventEnvelope, conflicts: SyncConflictFinding[], diagnostics: string[]): Promise<SyncIngestResult> {
  const existing = await findExistingEvent(tx, event);
  if (existing) return duplicateResult(event, existing);

  const now = new Date();
  await tx.outboxEvent.create({
    data: {
      id: event.eventId,
      businessId: event.businessId,
      terminalId: event.terminalId,
      topic: event.topic,
      eventType: event.eventType,
      aggregateId: aggregateIdFor(event),
      idempotencyKey: event.idempotencyKey,
      correlationId: event.correlationId ?? null,
      payloadJson: JSON.stringify(event),
      source: event.source,
      schemaVersion: event.schemaVersion,
      status: "conflict",
      lifecycleStatus: "conflict",
      attempts: 1,
      createdAt: new Date(event.occurredAt),
      receivedAt: now,
      validatedAt: now,
      conflictCode: conflicts[0]?.code ?? "inconsistent_sequence",
      diagnosticsJson: diagnosticsPayload({ lifecycleStatus: "conflict", conflicts, errors: [], diagnostics }),
      lastError: diagnosticsPayload({ lifecycleStatus: "conflict", conflicts, errors: [], diagnostics })
    }
  });
  return { eventId: event.eventId, topic: event.topic, status: "conflict", lifecycleStatus: "conflict", conflicts, errors: [], diagnostics };
}

async function persistAndProjectEvent(tx: any, event: SyncEventEnvelope): Promise<SyncIngestResult> {
  const existing = await findExistingEvent(tx, event);
  if (existing) return duplicateResult(event, existing);

  const now = new Date();
  const projection = await projectAcceptedSyncEvent(tx, event);
  const lifecycleStatus = projection.status === "projected" ? "reconciled" : projection.status;
  const status = projection.status === "conflict" || projection.status === "dead_letter" ? projection.status === "conflict" ? "conflict" : "rejected" : "accepted";
  const storageStatus = statusForLifecycle(lifecycleStatus);
  await tx.outboxEvent.create({
    data: {
      id: event.eventId,
      businessId: event.businessId,
      terminalId: event.terminalId,
      topic: event.topic,
      eventType: event.eventType,
      aggregateId: aggregateIdFor(event),
      idempotencyKey: event.idempotencyKey,
      correlationId: event.correlationId ?? null,
      payloadJson: JSON.stringify(event),
      source: event.source,
      schemaVersion: event.schemaVersion,
      status: storageStatus,
      lifecycleStatus,
      attempts: 1,
      createdAt: new Date(event.occurredAt),
      receivedAt: now,
      validatedAt: now,
      acceptedAt: projection.status === "dead_letter" ? null : now,
      projectedAt: projection.status === "projected" || projection.status === "reconciled" ? now : null,
      reconciledAt: lifecycleStatus === "reconciled" ? now : null,
      failedAt: projection.status === "dead_letter" ? now : null,
      deadLetterAt: projection.status === "dead_letter" ? now : null,
      conflictCode: projection.conflicts[0]?.code ?? null,
      diagnosticsJson: diagnosticsPayload({
        lifecycleStatus,
        conflicts: projection.conflicts,
        errors: [],
        diagnostics: projection.diagnostics,
        projectedModels: projection.touchedModels
      }),
      lastError: projection.conflicts.length
        ? diagnosticsPayload({ lifecycleStatus, conflicts: projection.conflicts, errors: [], diagnostics: projection.diagnostics })
        : null
    }
  });
  return {
    eventId: event.eventId,
    topic: event.topic,
    status,
    lifecycleStatus,
    conflicts: projection.conflicts,
    errors: [],
    diagnostics: projection.diagnostics,
    projectedModels: projection.touchedModels
  };
}

export async function persistSyncIngestPayload(input: unknown): Promise<SyncIngestClassification> {
  const candidates = extractSyncEvents(input);
  const seenInBatch = new Set<string>();
  const results = await (prisma as any).$transaction(async (tx: any) => {
    const batchResults: SyncIngestResult[] = [];
    for (const candidate of candidates) {
      const startedAt = new Date();
      const validation = validateSyncEventEnvelope(candidate);
      let result: SyncIngestResult;
      if (validation.event && seenInBatch.has(validation.event.idempotencyKey)) {
        result = {
          eventId: validation.event.eventId,
          topic: validation.event.topic,
          status: "duplicate",
          lifecycleStatus: "received",
          conflicts: [{ code: "duplicate_event", label: "Evento duplicado", severity: "warning", detail: "El idempotencyKey aparece repetido dentro del mismo lote." }],
          errors: [],
          diagnostics: ["DUPLICATE_IN_BATCH", "ALREADY_PROCESSED"]
        };
        batchResults.push(result);
        await recordSyncObservability({ tx, event: validation.event, candidate, result, startedAt, finishedAt: new Date() });
        continue;
      }
      if (!validation.event) {
        result = await persistRejected(tx, candidate, validation.errors, validation.conflicts);
        batchResults.push(result);
        await recordSyncObservability({ tx, event: null, candidate, result, startedAt, finishedAt: new Date() });
        continue;
      }
      seenInBatch.add(validation.event.idempotencyKey);
      if (validation.conflicts.length) {
        result = await persistConflict(tx, validation.event, validation.conflicts, ["VALIDATION_CONFLICT"]);
        batchResults.push(result);
        await recordSyncObservability({ tx, event: validation.event, candidate, result, startedAt, finishedAt: new Date() });
        continue;
      }
      result = await persistAndProjectEvent(tx, validation.event);
      batchResults.push(result);
      await recordSyncObservability({ tx, event: validation.event, candidate, result, startedAt, finishedAt: new Date() });
    }
    return batchResults;
  });

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
      idempotencyKey: "idempotencyKey",
      recognizedTopics: RECOGNIZED_SYNC_TOPICS,
      supportedSchemaVersions: SUPPORTED_SYNC_SCHEMA_VERSIONS,
      note: "PC validates, stores lifecycle ledger rows, runs Prisma ORM projectors, and keeps acked as compatibility only after projection/reconciliation."
    }
  };
}
