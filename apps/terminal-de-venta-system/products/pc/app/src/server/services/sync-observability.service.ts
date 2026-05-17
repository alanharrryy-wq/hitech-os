import { randomUUID } from "node:crypto";
import { syncPayloadFingerprint, type SyncConflictFinding, type SyncEventEnvelope, type SyncIngestResult } from "@/server/validators/sync-event-contract";

const OBSERVABILITY_STALE_AFTER_SECONDS = 90;

type TxClient = any;

type PersistedAttempt = {
  id: string;
  businessId: string;
  source: string;
  deviceId: string | null;
  terminalId: string | null;
  status: string;
  lifecycleStatus: string | null;
};

function delegate(tx: TxClient, name: string) {
  return tx?.[name] ?? null;
}

function safeJson(value: unknown) {
  try {
    return JSON.stringify(value);
  } catch {
    return JSON.stringify({ warning: "UNSERIALIZABLE_DIAGNOSTICS" });
  }
}

function sourceFor(event: SyncEventEnvelope | null) {
  return event?.source || "pc.sync.ingest";
}

function deviceFor(event: SyncEventEnvelope | null) {
  return event?.terminalId || null;
}

function statusFor(result: SyncIngestResult) {
  if (result.status === "accepted") return "success";
  if (result.status === "duplicate") return "already_processed";
  if (result.status === "conflict") return "conflict";
  return "failed";
}

async function bestEffort(operation: () => Promise<any>): Promise<any | null> {
  try {
    return await operation();
  } catch {
    return null;
  }
}

export async function recordSyncAttempt(input: {
  tx: TxClient;
  event: SyncEventEnvelope | null;
  candidate: unknown;
  result: SyncIngestResult;
  startedAt: Date;
  finishedAt: Date;
}): Promise<PersistedAttempt | null> {
  const model = delegate(input.tx, "syncAttempt");
  if (!model?.create) return null;

  const event = input.event;
  const businessId = event?.businessId || "biz_hitech_default";
  const durationMs = Math.max(0, input.finishedAt.getTime() - input.startedAt.getTime());
  const status = statusFor(input.result);
  const lifecycleStatus = input.result.lifecycleStatus ?? null;
  const source = sourceFor(event);
  const deviceId = deviceFor(event);
  const created = await bestEffort(() => model.create({
    data: {
      id: `sync_attempt_${randomUUID()}`,
      businessId,
      eventId: input.result.eventId ?? event?.eventId ?? null,
      outboxEventId: input.result.eventId ?? event?.eventId ?? null,
      idempotencyKey: event?.idempotencyKey ?? null,
      source,
      deviceId,
      terminalId: event?.terminalId ?? null,
      topic: input.result.topic ?? event?.topic ?? null,
      status,
      lifecycleStatus,
      attemptNumber: 1,
      receivedAt: input.startedAt,
      startedAt: input.startedAt,
      finishedAt: input.finishedAt,
      durationMs,
      errorCode: input.result.errors[0] ?? input.result.conflicts[0]?.code ?? null,
      diagnosticsJson: safeJson({ errors: input.result.errors, conflicts: input.result.conflicts, diagnostics: input.result.diagnostics ?? [] }),
      payloadFingerprint: syncPayloadFingerprint(input.candidate)
    }
  }));

  if (!created) return null;
  return { id: created.id, businessId, source, deviceId, terminalId: event?.terminalId ?? null, status, lifecycleStatus };
}

export async function recordSyncConflicts(input: {
  tx: TxClient;
  event: SyncEventEnvelope;
  conflicts: SyncConflictFinding[];
  diagnostics?: string[];
}) {
  const model = delegate(input.tx, "syncConflict");
  if (!model?.create) return;

  for (const conflict of input.conflicts) {
    await bestEffort(() => model.create({
      data: {
        id: `sync_conflict_${randomUUID()}`,
        businessId: input.event.businessId,
        eventId: input.event.eventId,
        outboxEventId: input.event.eventId,
        idempotencyKey: input.event.idempotencyKey,
        source: sourceFor(input.event),
        deviceId: deviceFor(input.event),
        terminalId: input.event.terminalId,
        topic: input.event.topic,
        aggregateId: input.event.aggregateId ?? null,
        conflictCode: conflict.code,
        label: conflict.label,
        severity: conflict.severity,
        detail: conflict.detail,
        status: conflict.severity === "warning" ? "observed" : "open",
        detectedAt: new Date(),
        diagnosticsJson: safeJson({ diagnostics: input.diagnostics ?? [] })
      }
    }));
  }
}

export async function advanceSyncCheckpoint(input: {
  tx: TxClient;
  event: SyncEventEnvelope | null;
  result: SyncIngestResult;
  attempt: PersistedAttempt | null;
}) {
  const event = input.event;
  if (!event) return;
  const model = delegate(input.tx, "syncCheckpoint");
  if (!model?.findFirst || !model?.create || !model?.update) return;

  const source = sourceFor(event);
  const deviceId = deviceFor(event);
  const stream = event.topic || "sync.ingest";
  const now = new Date();
  const existing = await bestEffort(() => model.findFirst({
    where: { businessId: event.businessId, source, deviceId, stream },
    orderBy: { updatedAt: "desc" }
  }));
  const data = {
    cursorValue: event.occurredAt || event.eventId,
    lastEventId: event.eventId,
    lastIdempotencyKey: event.idempotencyKey,
    lastAttemptId: input.attempt?.id ?? null,
    status: input.result.status,
    lifecycleStatus: input.result.lifecycleStatus ?? null,
    checkpointAt: now,
    metadataJson: safeJson({ topic: event.topic, aggregateId: event.aggregateId ?? null, diagnostics: input.result.diagnostics ?? [] })
  };

  if (existing?.id) {
    await bestEffort(() => model.update({ where: { id: existing.id }, data }));
  } else {
    await bestEffort(() => model.create({
      data: {
        id: `sync_checkpoint_${randomUUID()}`,
        businessId: event.businessId,
        source,
        deviceId,
        terminalId: event.terminalId,
        stream,
        ...data
      }
    }));
  }
}

export async function refreshSyncOutboxStatusBuckets(input: { tx: TxClient; event: SyncEventEnvelope | null }) {
  const event = input.event;
  if (!event) return;
  const model = delegate(input.tx, "syncOutboxStatusBucket");
  if (!model?.findFirst || !model?.create || !model?.update) return;

  const rows = await bestEffort(() => input.tx.outboxEvent.groupBy({
    by: ["status", "lifecycleStatus"],
    where: { businessId: event.businessId, source: event.source || undefined },
    _count: { _all: true },
    _min: { createdAt: true },
    _max: { createdAt: true }
  }));
  if (!Array.isArray(rows)) return;

  const bucketStartAt = new Date();
  bucketStartAt.setSeconds(0, 0);
  const bucketEndAt = new Date(bucketStartAt.getTime() + 60_000);
  for (const row of rows) {
    const status = row.status ?? "unknown";
    const lifecycleStatus = row.lifecycleStatus ?? null;
    const existing = await bestEffort(() => model.findFirst({
      where: { businessId: event.businessId, source: event.source, deviceId: event.terminalId, status, lifecycleStatus, bucketStartAt },
      orderBy: { updatedAt: "desc" }
    }));
    const data = {
      count: row._count?._all ?? 0,
      oldestEventAt: row._min?.createdAt ?? null,
      newestEventAt: row._max?.createdAt ?? null,
      staleCount: 0,
      bucketEndAt
    };
    if (existing?.id) await bestEffort(() => model.update({ where: { id: existing.id }, data }));
    else await bestEffort(() => model.create({
      data: {
        id: `sync_bucket_${randomUUID()}`,
        businessId: event.businessId,
        source: event.source,
        deviceId: event.terminalId,
        terminalId: event.terminalId,
        status,
        lifecycleStatus,
        topic: event.topic,
        bucketStartAt,
        ...data
      }
    }));
  }
}

export async function markDataSourceFreshness(input: { tx: TxClient; event: SyncEventEnvelope | null; result: SyncIngestResult }) {
  const event = input.event;
  if (!event) return;
  const model = delegate(input.tx, "dataSourceFreshness");
  if (!model?.findFirst || !model?.create || !model?.update) return;

  const now = new Date();
  const eventAt = Number.isNaN(Date.parse(event.occurredAt)) ? now : new Date(event.occurredAt);
  const freshnessSeconds = Math.max(0, Math.round((now.getTime() - eventAt.getTime()) / 1000));
  const status = input.result.status === "rejected" ? "error" : freshnessSeconds > OBSERVABILITY_STALE_AFTER_SECONDS ? "stale" : input.result.status === "conflict" ? "partial" : "ok";
  const confidence = status === "ok" ? 1 : status === "partial" ? 0.72 : status === "stale" ? 0.58 : 0.25;
  const existing = await bestEffort(() => model.findFirst({
    where: { businessId: event.businessId, source: event.source, deviceId: event.terminalId },
    orderBy: { updatedAt: "desc" }
  }));
  const data = {
    surface: event.source.includes("tablet") ? "tablet" : event.source.includes("pc") ? "pc" : null,
    status,
    confidence,
    freshnessSeconds,
    latencyMs: null,
    errorCount: input.result.errors.length,
    lastSeenAt: now,
    lastEventAt: eventAt,
    lastCheckpointAt: now,
    lastError: input.result.errors[0] ?? null,
    warningsJson: safeJson(input.result.conflicts.filter((item) => item.severity === "warning")),
    metadataJson: safeJson({ topic: event.topic, lifecycleStatus: input.result.lifecycleStatus ?? null, status: input.result.status }),
    observedAt: now
  };

  if (existing?.id) await bestEffort(() => model.update({ where: { id: existing.id }, data }));
  else await bestEffort(() => model.create({
    data: {
      id: `data_fresh_${randomUUID()}`,
      businessId: event.businessId,
      source: event.source,
      deviceId: event.terminalId,
      ...data
    }
  }));
}

export async function recordSyncObservability(input: {
  tx: TxClient;
  event: SyncEventEnvelope | null;
  candidate: unknown;
  result: SyncIngestResult;
  startedAt: Date;
  finishedAt: Date;
}) {
  const attempt = await recordSyncAttempt(input);
  if (input.event && input.result.conflicts.length) {
    await recordSyncConflicts({ tx: input.tx, event: input.event, conflicts: input.result.conflicts, diagnostics: input.result.diagnostics });
  }
  await advanceSyncCheckpoint({ tx: input.tx, event: input.event, result: input.result, attempt });
  await refreshSyncOutboxStatusBuckets({ tx: input.tx, event: input.event });
  await markDataSourceFreshness({ tx: input.tx, event: input.event, result: input.result });
}
