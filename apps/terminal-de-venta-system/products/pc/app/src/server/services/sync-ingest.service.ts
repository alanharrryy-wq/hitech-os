import { prisma } from "@/server/prisma/client";
import { projectAcceptedSyncEvent } from "@/server/services/sync-projectors.service";
import { canonicalSyncCheckpointSource, recordSyncObservability } from "@/server/services/sync-observability.service";
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

async function ensureLedgerBusiness(tx: any, businessId: string) {
  const id = businessId?.trim();
  if (!id) return;
  await tx.business.upsert({
    where: { id },
    create: {
      id,
      name: `PRISMA Sync ${id}`,
      currency: "MXN"
    },
    update: {}
  });
}

function aggregateIdFor(event: { payload: Record<string, unknown>; eventId: string; aggregateId?: string }) {
  const payload = event.payload;
  const pick = (value: unknown) => (typeof value === "string" && value.trim() ? value.trim() : "");
  return event.aggregateId || pick(payload.saleId) || pick(payload.productSupplierId) || pick(payload.linkId) || pick(payload.supplierId) || pick(payload.productId) || pick(payload.ticketId) || event.eventId;
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

function candidateString(candidate: unknown, key: string) {
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) return "";
  const value = (candidate as Record<string, unknown>)[key];
  return typeof value === "string" && value.trim() ? value.trim() : "";
}

function canonicalProjectionSource(event: SyncEventEnvelope) {
  return `pc-canonical-projection:${event.source}`;
}

function storedPayloadHash(existing: any) {
  try {
    const parsed = JSON.parse(existing?.payloadJson ?? "{}");
    if (typeof parsed?.payloadHash === "string" && parsed.payloadHash.trim()) return parsed.payloadHash.trim().toLowerCase();
    if (parsed?.payload && typeof parsed.payload === "object") return syncPayloadFingerprint(parsed.payload);
  } catch {
    // Treat unreadable historical payload as unknown instead of inventing equality.
  }
  return "";
}

function batchConflict(detail: string): SyncConflictFinding {
  return {
    code: "batch_checksum_mismatch",
    label: "Checksum de lote inválido",
    severity: "rejected",
    detail
  };
}

function batchValidationErrors(input: unknown, candidates: unknown[]) {
  if (!input || typeof input !== "object" || Array.isArray(input)) return [];
  const record = input as Record<string, unknown>;
  if (!Array.isArray(record.events)) return [];
  const batchId = candidateString(record, "batchId");
  const batchChecksum = candidateString(record, "batchChecksum").toLowerCase();
  const fingerprints = candidates.map((candidate) => {
    const event = candidate && typeof candidate === "object" && !Array.isArray(candidate)
      ? candidate as Record<string, unknown>
      : {};
    return {
      eventId: candidateString(event, "eventId"),
      payloadHash: candidateString(event, "payloadHash").toLowerCase(),
      sequence: typeof event.sequence === "number" ? event.sequence : Number(event.sequence)
    };
  });
  const expected = syncPayloadFingerprint(fingerprints);
  const errors: string[] = [];
  if (!batchId) errors.push("batchId debe ser texto no vacío.");
  if (!batchChecksum) errors.push("batchChecksum debe ser texto no vacío.");
  if (batchChecksum && batchChecksum !== expected) errors.push(`batchChecksum no coincide; expected=${expected}.`);
  for (const candidate of candidates) {
    if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) continue;
    const event = candidate as Record<string, unknown>;
    if (candidateString(event, "batchId") !== batchId) errors.push(`Evento ${candidateString(event, "eventId")} no pertenece al batchId recibido.`);
    if (candidateString(event, "batchChecksum").toLowerCase() !== batchChecksum) errors.push(`Evento ${candidateString(event, "eventId")} no conserva batchChecksum.`);
  }
  return [...new Set(errors)];
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
  const priorHash = storedPayloadHash(existing);
  if (priorHash && priorHash !== event.payloadHash) {
    return {
      eventId: event.eventId,
      topic: event.topic,
      status: "conflict",
      lifecycleStatus: "conflict",
      conflicts: [{
        code: "idempotency_payload_mismatch",
        label: "Idempotencia con payload distinto",
        severity: "conflict",
        detail: "PC ya recibió el mismo businessId + idempotencyKey con un payloadHash distinto."
      }],
      errors: [],
      diagnostics: ["IDEMPOTENCY_PAYLOAD_MISMATCH", `REMOTE_LEDGER_ID:${existing.id}`]
    };
  }
  return {
    eventId: event.eventId,
    topic: event.topic,
    status: "duplicate",
    lifecycleStatus: existing.lifecycleStatus ?? "reconciled",
    conflicts: [{ code: "duplicate_event", label: "Evento duplicado", severity: "warning", detail: "PC ya procesó este businessId + idempotencyKey o eventId; no se crea otro ledger." }],
    errors: [],
    diagnostics: ["ALREADY_PROCESSED", event.idempotencyKey ? "DUPLICATE_IDEMPOTENCY_KEY" : "DUPLICATE_EVENT_ID", `REMOTE_LEDGER_ID:${existing.id}`]
  };
}

async function sequenceConflict(tx: any, event: SyncEventEnvelope): Promise<SyncConflictFinding | null> {
  const model = tx?.syncCheckpoint;
  if (!model?.findFirst) return null;
  const existing = await model.findFirst({
    where: {
      businessId: event.businessId,
      source: canonicalSyncCheckpointSource(event),
      deviceId: event.deviceId,
      stream: event.topic
    },
    orderBy: { updatedAt: "desc" }
  }).catch(() => null);
  if (!existing?.cursorValue) return null;
  const prior = Number(existing.cursorValue);
  if (!Number.isSafeInteger(prior)) return null;
  if (event.sequence < prior) {
    return {
      code: "stale_sequence",
      label: "Secuencia vencida",
      severity: "conflict",
      detail: `sequence=${event.sequence} es menor que checkpoint=${prior}.`
    };
  }
  if (event.sequence === prior && existing.lastEventId && existing.lastEventId !== event.eventId) {
    return {
      code: "inconsistent_sequence",
      label: "Secuencia inconsistente",
      severity: "conflict",
      detail: `sequence=${event.sequence} ya pertenece a ${existing.lastEventId}.`
    };
  }
  return null;
}

async function persistRejected(tx: any, candidate: unknown, errors: string[], conflicts: SyncConflictFinding[]): Promise<SyncIngestResult> {
  const id = `rejected_${syncPayloadFingerprint(candidate).slice(0, 28)}`;
  const eventId = candidateString(candidate, "eventId") || id;
  const topic = candidateString(candidate, "topic") || candidateString(candidate, "eventType") || null;
  const existing = await tx.outboxEvent.findUnique({ where: { id } });
  if (existing) {
    return { eventId, topic, status: "duplicate", lifecycleStatus: "dead_letter", conflicts, errors: [], diagnostics: ["REJECTED_EVENT_ALREADY_PERSISTED", `REMOTE_LEDGER_ID:${id}`] };
  }
  const now = new Date();
  await ensureLedgerBusiness(tx, DEFAULT_REJECTED_SYNC_BUSINESS_ID);
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
  return { eventId, topic, status: "rejected", lifecycleStatus: "dead_letter", conflicts, errors, diagnostics: ["EVENT_REJECTED_BY_CONTRACT", `REMOTE_LEDGER_ID:${id}`] };
}

async function persistConflict(tx: any, event: SyncEventEnvelope, conflicts: SyncConflictFinding[], diagnostics: string[]): Promise<SyncIngestResult> {
  const existing = await findExistingEvent(tx, event);
  if (existing) return duplicateResult(event, existing);

  const now = new Date();
  await ensureLedgerBusiness(tx, event.businessId);
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
      source: canonicalProjectionSource(event),
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

  const sequenceFinding = await sequenceConflict(tx, event);
  if (sequenceFinding) {
    return {
      eventId: event.eventId,
      topic: event.topic,
      status: "conflict",
      lifecycleStatus: "conflict",
      conflicts: [sequenceFinding],
      errors: [],
      diagnostics: ["SEQUENCE_CHECKPOINT_CONFLICT"]
    };
  }

  const now = new Date();
  const projection = await projectAcceptedSyncEvent(tx, event);
  await ensureLedgerBusiness(tx, event.businessId);
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
      source: canonicalProjectionSource(event),
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

function safeErrorMessage(error: unknown) {
  const message = error instanceof Error ? error.message : String(error);
  return message.slice(0, 1200);
}

function unexpectedFailureConflict(message: string): SyncConflictFinding {
  return {
    code: "ingest_internal_error",
    label: "Error interno de ingest",
    severity: "rejected",
    detail: message
  };
}

async function persistUnexpectedFailure(candidate: unknown, error: unknown): Promise<SyncIngestResult> {
  const message = safeErrorMessage(error);
  const validation = validateSyncEventEnvelope(candidate);
  const fallbackId = `failed_${syncPayloadFingerprint(candidate).slice(0, 28)}`;
  const event = validation.event;
  const eventId = event?.eventId || candidateString(candidate, "eventId") || fallbackId;
  const topic = event?.topic || candidateString(candidate, "topic") || candidateString(candidate, "eventType") || "sync.ingest.failed";
  const businessId = event?.businessId || candidateString(candidate, "businessId") || DEFAULT_REJECTED_SYNC_BUSINESS_ID;
  const conflict = unexpectedFailureConflict(message);

  try {
    await (prisma as any).$transaction(async (tx: any) => {
      await ensureLedgerBusiness(tx, businessId);
      const existing = await tx.outboxEvent.findUnique({ where: { id: eventId } }).catch(() => null);
      if (existing) return;
      const now = new Date();
      await tx.outboxEvent.create({
        data: {
          id: eventId,
          businessId,
          terminalId: event?.terminalId || candidateString(candidate, "terminalId") || null,
          topic,
          eventType: topic,
          aggregateId: event?.aggregateId || aggregateIdFor(event ?? { eventId, payload: {} }),
          idempotencyKey: event?.idempotencyKey || candidateString(candidate, "idempotencyKey") || eventId,
          correlationId: event?.correlationId ?? null,
          payloadJson: JSON.stringify({ failed: candidate }),
          source: event?.source || candidateString(candidate, "source") || "pc.sync.ingest",
          schemaVersion: event?.schemaVersion || candidateString(candidate, "schemaVersion") || SUPPORTED_SYNC_SCHEMA_VERSIONS[0],
          status: "failed",
          lifecycleStatus: "failed",
          attempts: 1,
          createdAt: event?.occurredAt ? new Date(event.occurredAt) : now,
          receivedAt: now,
          validatedAt: validation.event ? now : null,
          failedAt: now,
          conflictCode: conflict.code,
          diagnosticsJson: diagnosticsPayload({ lifecycleStatus: "failed", conflicts: [conflict], errors: [message], diagnostics: ["SYNC_INGEST_EVENT_CAUGHT"] }),
          lastError: diagnosticsPayload({ lifecycleStatus: "failed", conflicts: [conflict], errors: [message], diagnostics: ["SYNC_INGEST_EVENT_CAUGHT"] })
        }
      });
    });
  } catch {
    // Keep the API response classified even if the failure ledger cannot be persisted.
  }

  return {
    eventId,
    topic,
    status: "rejected",
    lifecycleStatus: "failed",
    conflicts: [conflict],
    errors: [message],
    diagnostics: ["SYNC_INGEST_EVENT_CAUGHT"]
  };
}

async function processSyncCandidate(tx: any, candidate: unknown, seenInBatch: Set<string>): Promise<SyncIngestResult> {
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
    await recordSyncObservability({ tx, event: validation.event, candidate, result, startedAt, finishedAt: new Date() });
    return result;
  }
  if (!validation.event) {
    result = await persistRejected(tx, candidate, validation.errors, validation.conflicts);
    await recordSyncObservability({ tx, event: null, candidate, result, startedAt, finishedAt: new Date() });
    return result;
  }
  seenInBatch.add(validation.event.idempotencyKey);
  if (validation.conflicts.some((item) => item.severity === "rejected")) {
    result = await persistRejected(tx, candidate, validation.errors, validation.conflicts);
    await recordSyncObservability({ tx, event: validation.event, candidate, result, startedAt, finishedAt: new Date() });
    return result;
  }
  if (validation.conflicts.length) {
    result = await persistConflict(tx, validation.event, validation.conflicts, ["VALIDATION_CONFLICT"]);
    await recordSyncObservability({ tx, event: validation.event, candidate, result, startedAt, finishedAt: new Date() });
    return result;
  }
  result = await persistAndProjectEvent(tx, validation.event);
  await recordSyncObservability({ tx, event: validation.event, candidate, result, startedAt, finishedAt: new Date() });
  return result;
}

export async function persistSyncIngestPayload(input: unknown): Promise<SyncIngestClassification> {
  const candidates = extractSyncEvents(input);
  const seenInBatch = new Set<string>();
  const results: SyncIngestResult[] = [];
  const batchErrors = batchValidationErrors(input, candidates);

  if (batchErrors.length) {
    for (const candidate of candidates) {
      const result = await (prisma as any).$transaction(async (tx: any) =>
        persistRejected(tx, candidate, batchErrors, [batchConflict(batchErrors.join(" "))])
      );
      results.push(result);
    }
    const rejectedSummary = resultSummary(results);
    return {
      status: topStatus(rejectedSummary),
      eventsReceived: candidates.length,
      results,
      summary: rejectedSummary,
      meta: {
        persistence: "outbox_event",
        durable: true,
        storageModel: "OutboxEvent",
        idempotencyKey: "idempotencyKey",
        recognizedTopics: RECOGNIZED_SYNC_TOPICS,
        supportedSchemaVersions: SUPPORTED_SYNC_SCHEMA_VERSIONS,
        note: "El lote fue rechazado y persistido como dead-letter porque batchId/batchChecksum no probaron integridad."
      }
    };
  }

  for (const candidate of candidates) {
    try {
      const result = await (prisma as any).$transaction(async (tx: any) => processSyncCandidate(tx, candidate, seenInBatch));
      results.push(result);
    } catch (error) {
      results.push(await persistUnexpectedFailure(candidate, error));
    }
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
      idempotencyKey: "idempotencyKey",
      recognizedTopics: RECOGNIZED_SYNC_TOPICS,
      supportedSchemaVersions: SUPPORTED_SYNC_SCHEMA_VERSIONS,
      note: "PC validates each event in an isolated transaction, stores lifecycle ledger rows, runs Prisma ORM projectors, and returns per-event diagnostics instead of failing the whole batch."
    }
  };
}
