import { prisma } from "../prisma/client";
import { checkPrismaPcHealth, loadPrismaTabletPcOriginConfig, pcUrl, type PrismaTabletPcOriginConfig } from "./pc-origin";

type TabletOutboxEvent = Awaited<ReturnType<typeof loadPendingEvents>>[number];

type DispatchResultStatus = "accepted" | "duplicate" | "conflict" | "rejected" | "projected" | "reconciled" | "recognized_not_projected" | "failed";

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
  results?: PcDispatchEventResult[];
  events?: PcDispatchEventResult[];
  summary?: unknown;
  diagnostics?: unknown;
  data?: PcDispatchBatchResponse;
};

let inFlight = false;

function now() {
  return new Date();
}

function forcedSyncBusinessId() {
  return process.env.PRISMA_SYNC_BUSINESS_ID?.trim() || process.env.PRISMA_TABLET_BUSINESS_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_SYNC_BUSINESS_ID?.trim() || "";
}

function forcedSyncTerminalId() {
  return process.env.PRISMA_TABLET_TERMINAL_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_TABLET_TERMINAL_ID?.trim() || "";
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

const PC_SUPPORTED_SCHEMA_VERSION = "1.0.0";
const LEGACY_SCHEMA_VERSION_ALIASES = new Set(["boomsync2", "boom-sync-2", "v1", "1"]);

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
    orderBy: [{ createdAt: "asc" }],
    take: limit,
    select: OUTBOX_DISPATCH_SELECT
  });
}

function buildBatch(events: TabletOutboxEvent[]) {
  return {
    source: { app: "tablet", role: "pos", capability: "local-first-sale" },
    createdAt: new Date().toISOString(),
    events: events.map((event) => {
      const envelope = safePayload(event.payloadJson);
      const record = isRecord(envelope) ? envelope : {};
      const rawPayload: Record<string, unknown> = isRecord(record.payload) ? record.payload : isRecord(envelope) ? envelope : { rawPayloadJson: event.payloadJson };
      const eventId = pickString(event.id, record.eventId);
      const topic = pickString(record.topic, record.eventType, event.topic);
      const actorId = pickString(record.actorId, rawPayload.actorId, rawPayload.cashierId, rawPayload.cashier, "tablet-operator");
      const payload: Record<string, unknown> = { ...rawPayload };
      if (!pickString(payload.actorId)) payload.actorId = actorId;
      if (!pickString(payload.sourceEventId)) payload.sourceEventId = eventId;
      return {
        eventId,
        eventType: topic,
        topic,
        idempotencyKey: pickString(record.idempotencyKey, event.idempotencyKey, eventId),
        businessId: pickString(forcedSyncBusinessId(), record.businessId, event.businessId),
        terminalId: pickString(forcedSyncTerminalId(), record.terminalId, event.terminalId, "tablet-terminal-local"),
        actorId,
        aggregateId: pickString(record.aggregateId, event.aggregateId, eventId),
        correlationId: pickString(record.correlationId, event.aggregateId, event.id, eventId),
        source: pickString(record.source, event.source, "tablet-pos"),
        schemaVersion: canonicalSchemaVersion(record.schemaVersion, event.schemaVersion),
        occurredAt: pickString(record.occurredAt, event.createdAt instanceof Date ? event.createdAt.toISOString() : String(event.createdAt)),
        payload
      };
    })
  };
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
  return lifecycle === "projected" || lifecycle === "reconciled" || lifecycle === "recognized_not_projected" || result.status === "duplicate";
}

function remoteIssueCode(result: PcDispatchEventResult, fallback: string) {
  return result.conflictCode ?? result.rejectionCode ?? result.conflicts?.find((item) => item.code)?.code ?? result.errors?.find(Boolean) ?? fallback;
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
        remoteConflictCode: result.lifecycleStatus === "conflict" ? remoteIssueCode(result, "remote_conflict") : null,
        remoteRejectedReason: result.lifecycleStatus === "dead_letter" ? remoteIssueCode(result, "remote_rejected") : null,
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

export async function dispatchTabletOutboxOnce(config: PrismaTabletPcOriginConfig = loadPrismaTabletPcOriginConfig(), options: { force?: boolean } = {}) {
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
    const batch = buildBatch(events);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), config.timeoutMs);
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "content-type": "application/json", "x-prisma-source": "tablet" },
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
      return {
        ok: response.ok,
        reason: response.ok ? "dispatched" : "remote_results_applied_from_non_ok_response",
        dispatched: events.length,
        batchId: data.batchId ?? null,
        httpStatus: response.status
      };
    } catch (error) {
      await markNetworkFailure(events, error, config.maxAttempts);
      return { ok: false, reason: "dispatch_failed", dispatched: 0, error: error instanceof Error ? error.message : String(error) };
    } finally {
      clearTimeout(timer);
    }
  } finally {
    inFlight = false;
  }
}
