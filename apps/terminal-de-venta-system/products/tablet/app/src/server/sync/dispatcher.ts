import crypto from "node:crypto";
import { prisma } from "../prisma/client";
import { checkPrismaPcHealth, loadPrismaTabletPcOriginConfig, pcUrl, type PrismaTabletPcOriginConfig } from "./pc-origin";

type TabletOutboxEvent = Awaited<ReturnType<typeof loadPendingEvents>>[number];

type DispatchResultStatus =
  | "accepted"
  | "duplicate"
  | "conflict"
  | "rejected"
  | "projected"
  | "reconciled"
  | "recognized_not_projected"
  | "failed";

type PcDispatchEventResult = {
  eventId?: string;
  status?: DispatchResultStatus;
  lifecycleStatus?: string;
  remoteEventId?: string;
  remoteLedgerId?: string;
  idempotencyKey?: string;
  conflictCode?: string | null;
  rejectionCode?: string | null;
  conflicts?: Array<{ code?: string | null }>;
  errors?: string[];
  diagnostics?: unknown;
  retryable?: boolean;
};

type PcDispatchBatchResponse = {
  batchId?: string;
  batchChecksum?: string;
  results?: PcDispatchEventResult[];
  events?: PcDispatchEventResult[];
  summary?: unknown;
  diagnostics?: unknown;
  data?: PcDispatchBatchResponse;
};

type CanonicalTransportEvent = {
  eventId: string;
  source: string;
  subject: string;
  eventType: string;
  topic: string;
  eventVersion: string;
  schemaVersion: string;
  tenantId: string;
  customerId?: string;
  businessId: string;
  storeId: string;
  terminalId: string;
  deviceId: string;
  actorId: string;
  aggregateId: string;
  originRecordId: string;
  idempotencyKey: string;
  sequence: number;
  correlationId: string;
  causationId: string;
  traceId: string;
  occurredAt: string;
  capturedAt: string;
  payloadHash: string;
  batchId: string;
  batchChecksum: string;
  payload: Record<string, unknown>;
};

class SyncScopeError extends Error {
  constructor(readonly diagnostics: Record<string, unknown>) {
    super("SYNC_SCOPE_INCOMPLETE");
  }
}

let inFlight = false;

function now() {
  return new Date();
}

function envValue(...names: string[]) {
  for (const name of names) {
    const value = process.env[name]?.trim();
    if (value) return value;
  }
  return "";
}

function forcedSyncBusinessId() {
  return envValue("PRISMA_SYNC_BUSINESS_ID", "PRISMA_TABLET_BUSINESS_ID", "NEXT_PUBLIC_PRISMA_SYNC_BUSINESS_ID");
}

function forcedSyncTerminalId() {
  return envValue("PRISMA_TABLET_TERMINAL_ID", "NEXT_PUBLIC_PRISMA_TABLET_TERMINAL_ID");
}

function toJson(value: unknown): string | null {
  if (value === undefined || value === null) return null;
  try {
    return JSON.stringify(value).slice(0, 6000);
  } catch {
    return String(value).slice(0, 6000);
  }
}

function backoffDate(attempts: number) {
  const bounded = Math.max(1, Math.min(attempts, 10));
  const seconds = Math.min(3600, Math.pow(2, bounded) * 15);
  const jitter = Math.floor(Math.random() * Math.min(30, seconds));
  return new Date(Date.now() + (seconds + jitter) * 1000);
}

const PC_SUPPORTED_SCHEMA_VERSION = "1.1.0";
const PC_SUPPORTED_EVENT_VERSION = "1.0.0";
const LEGACY_SCHEMA_VERSION_ALIASES = new Set(["boomsync2", "boom-sync-2", "v1", "1", "1.0.0"]);

function canonicalSchemaVersion(...values: unknown[]): string {
  for (const value of values) {
    if (typeof value !== "string") continue;
    const normalized = value.trim();
    if (!normalized) continue;
    if (normalized === PC_SUPPORTED_SCHEMA_VERSION) return normalized;
    if (LEGACY_SCHEMA_VERSION_ALIASES.has(normalized.toLowerCase())) return PC_SUPPORTED_SCHEMA_VERSION;
  }
  return PC_SUPPORTED_SCHEMA_VERSION;
}

const DISPATCHABLE_OUTBOX_STATUSES = ["pending", "failed", "PENDING", "FAILED"];
const OUTBOX_DISPATCH_SELECT = {
  id: true,
  topic: true,
  idempotencyKey: true,
  businessId: true,
  terminalId: true,
  aggregateId: true,
  source: true,
  schemaVersion: true,
  payloadJson: true,
  attempts: true,
  sentAt: true,
  createdAt: true
} as const;

async function loadPendingEvents(limit: number, force = false) {
  const where: any = force
    ? { status: { in: DISPATCHABLE_OUTBOX_STATUSES } }
    : {
        status: { in: DISPATCHABLE_OUTBOX_STATUSES },
        OR: [{ nextRetryAt: null }, { nextRetryAt: { lte: now() } }]
      };
  return prisma.outboxEvent.findMany({
    where,
    orderBy: [{ createdAt: "asc" }, { id: "asc" }],
    take: limit,
    select: OUTBOX_DISPATCH_SELECT
  });
}

function safePayload(payloadJson: string) {
  try {
    return JSON.parse(payloadJson);
  } catch {
    return { rawPayloadJson: payloadJson };
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function pickString(...values: unknown[]): string {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

function stable(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stable);
  if (!isRecord(value)) return value;
  return Object.keys(value).sort().reduce<Record<string, unknown>>((acc, key) => {
    acc[key] = stable(value[key]);
    return acc;
  }, {});
}

function sha256(value: unknown) {
  return crypto.createHash("sha256").update(JSON.stringify(stable(value))).digest("hex");
}

function sequenceFor(createdAt: Date, eventId: string) {
  const suffix = [...eventId].reduce((sum, char) => (sum + char.charCodeAt(0)) % 1000, 0);
  return createdAt.getTime() * 1000 + suffix;
}

function subjectFor(input: {
  tenantId: string;
  businessId: string;
  storeId: string;
  terminalId: string;
  deviceId: string;
  topic: string;
  aggregateId: string;
}) {
  return [
    "prisma://sync",
    encodeURIComponent(input.tenantId),
    encodeURIComponent(input.businessId),
    encodeURIComponent(input.storeId),
    encodeURIComponent(input.terminalId),
    encodeURIComponent(input.deviceId),
    encodeURIComponent(input.topic),
    encodeURIComponent(input.aggregateId)
  ].join("/");
}

async function resolveStoreId(businessId: string, terminalId: string) {
  const terminal = await prisma.terminal.findFirst({
    where: { id: terminalId, businessId, isActive: true },
    select: { storeId: true }
  });
  return terminal?.storeId?.trim() ?? "";
}

async function canonicalEvent(event: TabletOutboxEvent, batchId: string, capturedAt: string) {
  const envelope = safePayload(event.payloadJson);
  const record = isRecord(envelope) ? envelope : {};
  const rawPayload: Record<string, unknown> = isRecord(record.payload)
    ? record.payload
    : isRecord(envelope)
      ? envelope
      : { rawPayloadJson: event.payloadJson };

  const eventId = pickString(event.id, record.eventId);
  const topic = pickString(record.topic, record.eventType, event.topic);
  const businessId = pickString(forcedSyncBusinessId(), record.businessId, event.businessId);
  const terminalId = pickString(forcedSyncTerminalId(), record.terminalId, event.terminalId);
  const storeId = pickString(
    record.storeId,
    rawPayload.storeId,
    envValue("PRISMA_TABLET_STORE_ID", "NEXT_PUBLIC_PRISMA_TABLET_STORE_ID"),
    await resolveStoreId(businessId, terminalId)
  );
  const tenantId = pickString(
    record.tenantId,
    rawPayload.tenantId,
    envValue("PRISMA_TENANT_ID", "NEXT_PUBLIC_PRISMA_TENANT_ID")
  );
  const customerId = pickString(
    record.customerId,
    rawPayload.customerId,
    envValue("PRISMA_CUSTOMER_ID", "NEXT_PUBLIC_PRISMA_CUSTOMER_ID")
  );
  const deviceId = pickString(
    record.deviceId,
    rawPayload.deviceId,
    envValue("PRISMA_TABLET_DEVICE_ID", "NEXT_PUBLIC_PRISMA_TABLET_DEVICE_ID"),
    terminalId
  );
  const actorId = pickString(record.actorId, rawPayload.actorId, rawPayload.cashierId, rawPayload.cashier, "tablet-operator");
  const aggregateId = pickString(record.aggregateId, event.aggregateId, eventId);
  const originRecordId = pickString(record.originRecordId, rawPayload.saleId, rawPayload.returnId, rawPayload.productId, rawPayload.cashSessionId, aggregateId);
  const correlationId = pickString(record.correlationId, event.aggregateId, event.id, eventId);
  const causationId = pickString(record.causationId, rawPayload.previousEventId, correlationId);
  const traceId = pickString(record.traceId, correlationId, eventId);
  const occurredAt = pickString(record.occurredAt, event.createdAt instanceof Date ? event.createdAt.toISOString() : String(event.createdAt));
  const payload: Record<string, unknown> = { ...rawPayload };
  if (!pickString(payload.actorId)) payload.actorId = actorId;
  if (!pickString(payload.sourceEventId)) payload.sourceEventId = eventId;

  const missing = [
    ["tenantId", tenantId],
    ["businessId", businessId],
    ["storeId", storeId],
    ["terminalId", terminalId],
    ["deviceId", deviceId]
  ].filter(([, value]) => !value).map(([name]) => name);

  if (missing.length) {
    throw new SyncScopeError({ eventId, missing, businessId, terminalId });
  }

  const payloadHash = sha256(payload);
  const sequence = Number.isSafeInteger(record.sequence)
    ? Number(record.sequence)
    : sequenceFor(event.createdAt, eventId);

  return {
    eventId,
    source: pickString(record.source, event.source, "tablet-pos"),
    subject: pickString(record.subject, subjectFor({ tenantId, businessId, storeId, terminalId, deviceId, topic, aggregateId })),
    eventType: topic,
    topic,
    eventVersion: pickString(record.eventVersion, PC_SUPPORTED_EVENT_VERSION),
    schemaVersion: canonicalSchemaVersion(record.schemaVersion, event.schemaVersion),
    tenantId,
    ...(customerId ? { customerId } : {}),
    businessId,
    storeId,
    terminalId,
    deviceId,
    actorId,
    aggregateId,
    originRecordId,
    idempotencyKey: pickString(record.idempotencyKey, event.idempotencyKey, eventId),
    sequence,
    correlationId,
    causationId,
    traceId,
    occurredAt,
    capturedAt,
    payloadHash,
    batchId,
    batchChecksum: "",
    payload
  };
}

async function buildBatch(events: TabletOutboxEvent[]) {
  const batchId = `batch_${crypto.randomUUID()}`;
  const capturedAt = new Date().toISOString();
  const canonical = await Promise.all(events.map((event) => canonicalEvent(event, batchId, capturedAt)));
  const batchChecksum = sha256(canonical.map((event) => ({
    eventId: event.eventId,
    payloadHash: event.payloadHash,
    sequence: event.sequence
  })));
  const completed: CanonicalTransportEvent[] = canonical.map((event) => ({ ...event, batchChecksum }));
  return {
    batchId,
    batchChecksum,
    source: { app: "tablet", role: "pos", capability: "local-first-sale" },
    createdAt: capturedAt,
    events: completed
  };
}

function resultFor(event: TabletOutboxEvent, response: PcDispatchBatchResponse): PcDispatchEventResult | null {
  const data = isRecord(response.data) ? response.data as PcDispatchBatchResponse : response;
  const results = data.results ?? data.events ?? [];
  const idempotencyKey = pickString(event.idempotencyKey, event.id);
  return results.find((item) =>
    item.eventId === event.id ||
    item.remoteEventId === event.id ||
    item.eventId === idempotencyKey ||
    item.idempotencyKey === idempotencyKey
  ) ?? null;
}

function isAck(result: PcDispatchEventResult): boolean {
  const lifecycle = result.lifecycleStatus ?? result.status;
  return lifecycle === "projected" ||
    lifecycle === "reconciled" ||
    lifecycle === "recognized_not_projected" ||
    result.status === "duplicate";
}

function remoteIssueCode(result: PcDispatchEventResult, fallback: string) {
  return result.conflictCode ??
    result.rejectionCode ??
    result.conflicts?.find((item) => item.code)?.code ??
    result.errors?.find(Boolean) ??
    fallback;
}

async function applyAck(event: TabletOutboxEvent, result: PcDispatchEventResult) {
  const stamp = now();
  if (isAck(result)) {
    await prisma.outboxEvent.update({
      where: { id: event.id },
      data: {
        status: "acked",
        sentAt: event.sentAt ?? stamp,
        syncedAt: stamp,
        ackedAt: stamp,
        lastAttemptAt: stamp,
        nextRetryAt: null,
        remoteEventId: result.remoteEventId ?? result.eventId ?? null,
        remoteLedgerId: result.remoteLedgerId ?? null,
        remoteLifecycleStatus: result.lifecycleStatus ?? result.status ?? null,
        remoteDiagnosticsJson: toJson(result.diagnostics),
        remoteConflictCode: null,
        remoteRejectedReason: null,
        lastError: null
      }
    });
    return;
  }

  if (result.status === "failed") {
    const terminal = result.retryable === false || result.lifecycleStatus === "dead_letter";
    await prisma.outboxEvent.update({
      where: { id: event.id },
      data: {
        status: terminal ? "failed" : "pending",
        failedAt: terminal ? stamp : null,
        lastAttemptAt: stamp,
        nextRetryAt: terminal ? null : backoffDate(event.attempts + 1),
        attempts: { increment: 1 },
        remoteEventId: result.remoteEventId ?? result.eventId ?? null,
        remoteLedgerId: result.remoteLedgerId ?? null,
        remoteLifecycleStatus: result.lifecycleStatus ?? result.status ?? null,
        remoteDiagnosticsJson: toJson(result.diagnostics),
        lastError: remoteIssueCode(result, "Remote failed")
      }
    });
    return;
  }

  if (result.status === "conflict") {
    await prisma.outboxEvent.update({
      where: { id: event.id },
      data: {
        status: "conflict",
        conflictedAt: stamp,
        lastAttemptAt: stamp,
        nextRetryAt: null,
        remoteEventId: result.remoteEventId ?? result.eventId ?? null,
        remoteLedgerId: result.remoteLedgerId ?? null,
        remoteLifecycleStatus: result.lifecycleStatus ?? result.status ?? null,
        remoteConflictCode: remoteIssueCode(result, "remote_conflict"),
        remoteDiagnosticsJson: toJson(result.diagnostics),
        lastError: remoteIssueCode(result, "Remote conflict")
      }
    });
    return;
  }

  if (result.status === "rejected") {
    const terminal = result.retryable === false || result.lifecycleStatus === "dead_letter";
    await prisma.outboxEvent.update({
      where: { id: event.id },
      data: {
        status: terminal ? "failed" : "pending",
        failedAt: terminal ? stamp : null,
        lastAttemptAt: stamp,
        nextRetryAt: terminal ? null : backoffDate(event.attempts + 1),
        attempts: { increment: 1 },
        remoteEventId: result.remoteEventId ?? result.eventId ?? null,
        remoteLedgerId: result.remoteLedgerId ?? null,
        remoteLifecycleStatus: result.lifecycleStatus ?? result.status ?? null,
        remoteRejectedReason: remoteIssueCode(result, "remote_rejected"),
        remoteDiagnosticsJson: toJson(result.diagnostics),
        lastError: remoteIssueCode(result, "Remote rejected")
      }
    });
    return;
  }

  await prisma.outboxEvent.update({
    where: { id: event.id },
    data: {
      status: "sent",
      sentAt: stamp,
      lastAttemptAt: stamp,
      nextRetryAt: backoffDate(event.attempts + 1),
      attempts: { increment: 1 },
      remoteLifecycleStatus: result.lifecycleStatus ?? result.status ?? "received",
      remoteDiagnosticsJson: toJson(result.diagnostics),
      lastError: result.status === "recognized_not_projected" ? "Recognized by PC but not projected" : null
    }
  });
}

async function markNetworkFailure(events: TabletOutboxEvent[], error: unknown, maxAttempts: number) {
  const stamp = now();
  const message = error instanceof Error ? error.message : String(error);
  await Promise.all(events.map((event) => prisma.outboxEvent.update({
    where: { id: event.id },
    data: {
      status: event.attempts + 1 >= maxAttempts ? "failed" : "pending",
      attempts: { increment: 1 },
      lastAttemptAt: stamp,
      failedAt: event.attempts + 1 >= maxAttempts ? stamp : null,
      nextRetryAt: event.attempts + 1 >= maxAttempts ? null : backoffDate(event.attempts + 1),
      lastError: message.slice(0, 1000)
    }
  })));
}

async function markScopeFailure(events: TabletOutboxEvent[], error: SyncScopeError) {
  const stamp = now();
  await Promise.all(events.map((event) => prisma.outboxEvent.update({
    where: { id: event.id },
    data: {
      status: "pending",
      lastAttemptAt: stamp,
      nextRetryAt: backoffDate(Math.max(1, event.attempts + 1)),
      lastError: `SYNC_SCOPE_INCOMPLETE:${JSON.stringify(error.diagnostics).slice(0, 800)}`
    }
  })));
}

export async function dispatchTabletOutboxOnce(
  config: PrismaTabletPcOriginConfig = loadPrismaTabletPcOriginConfig(),
  options: { force?: boolean } = {}
) {
  if (inFlight) return { ok: false, reason: "dispatcher_in_flight", dispatched: 0 };
  if (!config.enabled) return { ok: false, reason: "pc_sync_disabled", dispatched: 0 };
  const url = pcUrl(config, config.ingestPath);
  if (!url) return { ok: false, reason: "missing_pc_origin", dispatched: 0 };

  const health = await checkPrismaPcHealth(config);
  if (!health.ok) return { ok: false, reason: "pc_unavailable", health, dispatched: 0 };

  inFlight = true;
  try {
    const events = await loadPendingEvents(config.batchSize, options.force === true);
    if (events.length === 0) return { ok: true, reason: "empty", dispatched: 0 };

    let batch: Awaited<ReturnType<typeof buildBatch>>;
    try {
      batch = await buildBatch(events);
    } catch (error) {
      if (error instanceof SyncScopeError) {
        await markScopeFailure(events, error);
        return { ok: false, reason: "scope_incomplete", dispatched: 0, diagnostics: error.diagnostics };
      }
      throw error;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), config.timeoutMs);
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-prisma-source": "tablet",
          "x-prisma-batch-id": batch.batchId,
          "x-prisma-batch-checksum": batch.batchChecksum
        },
        body: JSON.stringify(batch),
        signal: controller.signal
      });
      const body = await response.json().catch(() => ({
        diagnostics: { httpStatus: response.status, message: "PC ingest returned non-JSON response." }
      } as PcDispatchBatchResponse));
      const data = isRecord(body.data) ? body.data as PcDispatchBatchResponse : body;
      const remoteResults = data.results ?? data.events ?? [];
      const hasRemoteResults = Array.isArray(remoteResults) && remoteResults.length > 0;
      if (!response.ok && !hasRemoteResults) {
        throw new Error(`PC ingest HTTP ${response.status}`);
      }

      await Promise.all(events.map((event: TabletOutboxEvent) => applyAck(event, resultFor(event, body) ?? {
        status: "failed",
        retryable: response.status >= 500 || response.status === 429,
        diagnostics: data.diagnostics ?? body.diagnostics ?? { httpStatus: response.status }
      })));

      const cleanDispatch = response.status === 200;
      return {
        ok: cleanDispatch,
        reason: cleanDispatch ? "dispatched" : response.ok ? "partial" : "remote_results_applied_from_non_ok_response",
        dispatched: events.length,
        batchId: data.batchId ?? batch.batchId,
        batchChecksum: data.batchChecksum ?? batch.batchChecksum,
        httpStatus: response.status
      };
    } catch (error) {
      await markNetworkFailure(events, error, config.maxAttempts);
      return {
        ok: false,
        reason: "dispatch_failed",
        dispatched: 0,
        error: error instanceof Error ? error.message : String(error)
      };
    } finally {
      clearTimeout(timer);
    }
  } finally {
    inFlight = false;
  }
}
