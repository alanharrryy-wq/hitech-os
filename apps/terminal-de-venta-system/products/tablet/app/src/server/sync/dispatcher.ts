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
  conflictCode?: string | null;
  rejectionCode?: string | null;
  diagnostics?: unknown;
  retryable?: boolean;
};

type PcDispatchBatchResponse = {
  batchId?: string;
  results?: PcDispatchEventResult[];
  events?: PcDispatchEventResult[];
  summary?: unknown;
  diagnostics?: unknown;
};

let inFlight = false;

function now() {
  return new Date();
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

async function loadPendingEvents(limit: number) {
  return prisma.outboxEvent.findMany({
    where: {
      status: { in: ["pending", "failed"] },
      OR: [{ nextRetryAt: null }, { nextRetryAt: { lte: now() } }]
    },
    orderBy: [{ createdAt: "asc" }],
    take: limit
  });
}

function buildBatch(events: TabletOutboxEvent[]) {
  return {
    source: { app: "tablet", role: "pos", capability: "local-first-sale" },
    createdAt: new Date().toISOString(),
    events: events.map((event) => ({
      eventId: event.id,
      eventType: event.topic,
      topic: event.topic,
      idempotencyKey: event.idempotencyKey,
      businessId: event.businessId,
      terminalId: event.terminalId,
      aggregateId: event.aggregateId,
      source: event.source ?? "tablet-pos",
      schemaVersion: event.schemaVersion ?? "1.0.0",
      occurredAt: event.createdAt instanceof Date ? event.createdAt.toISOString() : String(event.createdAt),
      payload: safePayload(event.payloadJson)
    }))
  };
}

function safePayload(payloadJson: string) {
  try {
    return JSON.parse(payloadJson);
  } catch {
    return { rawPayloadJson: payloadJson };
  }
}

function resultFor(event: TabletOutboxEvent, response: PcDispatchBatchResponse): PcDispatchEventResult | null {
  const results = response.results ?? response.events ?? [];
  return results.find((item) => item.eventId === event.id || item.remoteEventId === event.id) ?? null;
}

function isAck(result: PcDispatchEventResult): boolean {
  const lifecycle = result.lifecycleStatus ?? result.status;
  return lifecycle === "projected" || lifecycle === "reconciled" || result.status === "duplicate";
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
        remoteConflictCode: result.conflictCode ?? null,
        remoteRejectedReason: result.rejectionCode ?? null,
        lastError: null
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
        remoteConflictCode: result.conflictCode ?? "remote_conflict",
        remoteDiagnosticsJson: toJson(result.diagnostics),
        lastError: result.conflictCode ?? "Remote conflict"
      }
    });
    return;
  }

  if (result.status === "rejected") {
    await prisma.outboxEvent.update({
      where: { id: event.id },
      data: {
        status: result.retryable === false ? "failed" : "pending",
        failedAt: result.retryable === false ? stamp : null,
        lastAttemptAt: stamp,
        nextRetryAt: result.retryable === false ? null : backoffDate(event.attempts + 1),
        attempts: { increment: 1 },
        remoteEventId: result.remoteEventId ?? result.eventId ?? null,
        remoteLedgerId: result.remoteLedgerId ?? null,
        remoteLifecycleStatus: result.lifecycleStatus ?? result.status ?? null,
        remoteRejectedReason: result.rejectionCode ?? "remote_rejected",
        remoteDiagnosticsJson: toJson(result.diagnostics),
        lastError: result.rejectionCode ?? "Remote rejected"
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

export async function dispatchTabletOutboxOnce(config: PrismaTabletPcOriginConfig = loadPrismaTabletPcOriginConfig()) {
  if (inFlight) return { ok: false, reason: "dispatcher_in_flight", dispatched: 0 };
  if (!config.enabled) return { ok: false, reason: "pc_sync_disabled", dispatched: 0 };
  const url = pcUrl(config, config.ingestPath);
  if (!url) return { ok: false, reason: "missing_pc_origin", dispatched: 0 };

  const health = await checkPrismaPcHealth(config);
  if (!health.ok) return { ok: false, reason: "pc_unavailable", health, dispatched: 0 };

  inFlight = true;
  try {
    const events = await loadPendingEvents(config.batchSize);
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
      const body = await response.json().catch(() => ({} as PcDispatchBatchResponse));
      if (!response.ok) throw new Error(`PC ingest HTTP ${response.status}`);
      await Promise.all(events.map((event: TabletOutboxEvent) => applyAck(event, resultFor(event, body) ?? { status: "failed", retryable: true, diagnostics: body.diagnostics })));
      return { ok: true, reason: "dispatched", dispatched: events.length, batchId: body.batchId ?? null };
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
