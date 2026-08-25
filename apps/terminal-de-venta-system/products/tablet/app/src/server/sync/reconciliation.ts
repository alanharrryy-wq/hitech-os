import { prisma } from "@/server/prisma/client";
import { DEFAULT_POS_API_BUSINESS_ID } from "@/server/pos-api/validators";
import { loadPrismaTabletPcOriginConfig, pcUrl, type PrismaTabletPcOriginConfig } from "@/server/sync/pc-origin";

type ReconcileStatus = "acked" | "conflict" | "failed" | "skipped";

export type TabletSentReconciliationInput = {
  businessId?: string | null;
  limit?: number | string | null;
  source?: string | null;
  config?: PrismaTabletPcOriginConfig;
};

export type TabletSentReconciliationResult = {
  ok: boolean;
  reason: string;
  url: string | null;
  checked: number;
  sent: number;
  counts: Record<ReconcileStatus, number>;
  results: Array<{
    id: string;
    status: ReconcileStatus;
    remoteStatus: string | null;
    lifecycleStatus: string | null;
    remoteEventId: string | null;
    remoteLedgerId: string | null;
    conflictCode: string | null;
    rejectedReason: string | null;
    reason: string;
  }>;
  errors: string[];
};

const DEFAULT_LIMIT = 80;
const DEFAULT_TIMEOUT_MS = 2500;

function asString(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : "";
}

function asNumber(value: unknown, fallback: number) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(1, Math.min(Math.trunc(parsed), 250));
}

function iso(value: unknown) {
  if (value instanceof Date) return value.toISOString();
  const text = asString(value);
  if (!text) return new Date().toISOString();
  const date = new Date(text);
  return Number.isNaN(date.getTime()) ? new Date().toISOString() : date.toISOString();
}

function safeJsonParse(value: unknown) {
  if (value && typeof value === "object") return value as Record<string, unknown>;
  if (typeof value !== "string" || !value.trim()) return {};
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed as Record<string, unknown> : {};
  } catch {
    return {};
  }
}

function payloadFromRow(row: any) {
  return safeJsonParse(row.payloadJson ?? row.payload ?? row.bodyJson ?? row.dataJson);
}

function envelopeFromRow(row: any) {
  const parsed = payloadFromRow(row);
  if (asString(parsed.eventId) && asString(parsed.topic) && parsed.payload && typeof parsed.payload === "object") {
    return parsed;
  }

  const payload = parsed.payload && typeof parsed.payload === "object" ? parsed.payload as Record<string, unknown> : parsed;
  const eventId = asString(row.id ?? parsed.eventId);
  const topic = asString(row.topic ?? row.eventType ?? parsed.topic ?? parsed.eventType);
  const businessId = asString(row.businessId ?? parsed.businessId) || DEFAULT_POS_API_BUSINESS_ID;
  const terminalId = asString(row.terminalId ?? parsed.terminalId) || "tablet-terminal";
  if (!eventId || !topic) return null;

  return {
    eventId,
    eventType: asString(row.eventType ?? parsed.eventType) || topic,
    topic,
    idempotencyKey: asString(row.idempotencyKey ?? parsed.idempotencyKey) || eventId,
    correlationId: asString(row.correlationId ?? parsed.correlationId) || null,
    businessId,
    terminalId,
    actorId: asString(row.actorId ?? parsed.actorId) || "tablet-sync-reconciliation",
    source: asString(row.source ?? parsed.source) || "tablet.pos.outbox",
    occurredAt: iso(row.createdAt ?? row.occurredAt ?? parsed.occurredAt),
    schemaVersion: asString(row.schemaVersion ?? parsed.schemaVersion) || "sync-event.v1",
    payload
  };
}

function extractRemoteResults(payload: any): any[] {
  const data = payload?.data ?? payload;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.events)) return data.events;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
}

function remoteKey(result: any) {
  return asString(result?.eventId ?? result?.remoteEventId ?? result?.id);
}

function diagnostics(result: any): string[] {
  return Array.isArray(result?.diagnostics) ? result.diagnostics.map(asString).filter(Boolean) : [];
}

function diagnosticsContain(result: any, token: string) {
  return diagnostics(result).some((item) => item.toUpperCase().includes(token));
}

function diagnosticValue(result: any, prefix: string) {
  const hit = diagnostics(result).find((item) => item.startsWith(prefix));
  return hit ? hit.slice(prefix.length).trim() : "";
}

function remoteLedgerId(result: any) {
  return asString(result?.remoteLedgerId) || diagnosticValue(result, "REMOTE_LEDGER_ID:") || "";
}

function conflictCode(result: any) {
  const conflicts = Array.isArray(result?.conflicts) ? result.conflicts : [];
  return asString(result?.conflictCode ?? result?.rejectionCode ?? conflicts.find((item: any) => asString(item?.code))?.code);
}

function rejectedReason(result: any) {
  const errors = Array.isArray(result?.errors) ? result.errors : [];
  return asString(result?.rejectedReason ?? result?.rejectionCode ?? errors.find((item: unknown) => asString(item)));
}

function toJson(value: unknown) {
  try {
    return JSON.stringify(value ?? null).slice(0, 6000);
  } catch {
    return String(value ?? "").slice(0, 6000);
  }
}

function classifyRemoteResult(result: any): { status: ReconcileStatus; reason: string } {
  if (!result) return { status: "skipped", reason: "missing_remote_result" };
  const remoteStatus = asString(result.status).toLowerCase();
  const lifecycleStatus = asString(result.lifecycleStatus).toLowerCase();

  if (
    remoteStatus === "accepted" ||
    remoteStatus === "duplicate" ||
    lifecycleStatus === "accepted" ||
    lifecycleStatus === "projected" ||
    lifecycleStatus === "reconciled" ||
    lifecycleStatus === "recognized_not_projected" ||
    diagnosticsContain(result, "ALREADY_PROCESSED")
  ) {
    return { status: "acked", reason: remoteStatus === "duplicate" ? "pc_duplicate_means_idempotent_ack" : "pc_acceptance_confirmed" };
  }

  if (remoteStatus === "conflict" || lifecycleStatus === "conflict") return { status: "conflict", reason: "pc_conflict" };
  if (remoteStatus === "rejected" || lifecycleStatus === "failed" || lifecycleStatus === "dead_letter") return { status: "failed", reason: "pc_rejected_or_dead_letter" };
  return { status: "skipped", reason: "remote_status_not_actionable" };
}

async function updateLocalStatus(rowId: string, nextStatus: Exclude<ReconcileStatus, "skipped">, remote: any) {
  const db = prisma as any;
  const stamp = new Date();
  const remoteStatus = asString(remote?.status) || null;
  const lifecycleStatus = asString(remote?.lifecycleStatus) || remoteStatus;
  const remoteEventId = asString(remote?.remoteEventId ?? remote?.eventId) || null;
  const ledgerId = remoteLedgerId(remote) || null;
  const issueCode = conflictCode(remote) || null;
  const rejection = rejectedReason(remote) || null;
  const diagnosticPayload = toJson(diagnostics(remote));
  const data: Record<string, unknown> = {
    status: nextStatus,
    lastAttemptAt: stamp,
    nextRetryAt: null,
    remoteEventId,
    remoteLedgerId: ledgerId,
    remoteLifecycleStatus: lifecycleStatus,
    remoteDiagnosticsJson: diagnosticPayload
  };

  if (nextStatus === "acked") {
    Object.assign(data, {
      syncedAt: stamp,
      ackedAt: stamp,
      failedAt: null,
      conflictedAt: null,
      remoteConflictCode: null,
      remoteRejectedReason: null,
      lastError: null
    });
  } else if (nextStatus === "conflict") {
    Object.assign(data, {
      conflictedAt: stamp,
      failedAt: null,
      remoteConflictCode: issueCode ?? "remote_conflict",
      remoteRejectedReason: null,
      lastError: issueCode ?? "Remote conflict"
    });
  } else {
    Object.assign(data, {
      failedAt: stamp,
      remoteConflictCode: null,
      remoteRejectedReason: rejection ?? issueCode ?? "pc_rejected_or_dead_letter",
      lastError: rejection ?? issueCode ?? "PC rejected or dead-lettered the event"
    });
  }

  try {
    await db.outboxEvent.update({ where: { id: rowId }, data });
  } catch {
    await db.outboxEvent.update({
      where: { id: rowId },
      data: {
        status: nextStatus,
        lastError: nextStatus === "acked" ? null : toJson({
          source: "tablet.sent.reconciliation",
          remoteStatus,
          lifecycleStatus,
          remoteEventId,
          remoteLedgerId: ledgerId,
          conflictCode: issueCode,
          rejectedReason: rejection,
          diagnostics: diagnostics(remote)
        })
      }
    });
  }
}

export async function reconcileTabletSentOutboxWithPc(input: TabletSentReconciliationInput = {}): Promise<TabletSentReconciliationResult> {
  const config = input.config ?? loadPrismaTabletPcOriginConfig();
  const url = pcUrl(config, "/api/sync/ingest");
  const counts: Record<ReconcileStatus, number> = { acked: 0, conflict: 0, failed: 0, skipped: 0 };
  const errors: string[] = [];

  if (!config.enabled) {
    return { ok: false, reason: "pc_sync_disabled", url, checked: 0, sent: 0, counts, results: [], errors: ["PC sync disabled."] };
  }
  if (!url) {
    return { ok: false, reason: "missing_pc_origin", url: null, checked: 0, sent: 0, counts, results: [], errors: ["Missing PC origin."] };
  }

  const db = prisma as any;
  const businessId = asString(input.businessId) || DEFAULT_POS_API_BUSINESS_ID;
  const limit = asNumber(input.limit, DEFAULT_LIMIT);
  const rows = await db.outboxEvent.findMany({
    where: { businessId, status: "sent" },
    orderBy: [{ createdAt: "asc" }, { id: "asc" }],
    take: limit
  }).catch((error: unknown) => {
    throw new Error(error instanceof Error ? error.message : "No se pudo leer outbox local.");
  });

  const events = rows.map(envelopeFromRow).filter(Boolean);
  if (!rows.length || !events.length) {
    return { ok: true, reason: "empty", url, checked: rows.length, sent: events.length, counts, results: [], errors };
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), config.timeoutMs || DEFAULT_TIMEOUT_MS);
  let payload: any = null;
  let httpStatus = 0;

  try {
    const response = await fetch(url, {
      method: "POST",
      cache: "no-store",
      signal: controller.signal,
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        events,
        source: input.source || "tablet.sent.reconciliation",
        requestedBy: "tablet-sync-reconciliation"
      })
    });
    httpStatus = response.status;
    payload = await response.json().catch(() => null);
  } catch (error) {
    errors.push(error instanceof Error ? error.message : String(error));
    return { ok: false, reason: "pc_unavailable", url, checked: rows.length, sent: events.length, counts, results: [], errors };
  } finally {
    clearTimeout(timeout);
  }

  const remoteResults = extractRemoteResults(payload);
  if (!remoteResults.length) {
    return {
      ok: false,
      reason: "invalid_pc_response",
      url,
      checked: rows.length,
      sent: events.length,
      counts,
      results: [],
      errors: [`PC response did not include per-event results. HTTP ${httpStatus}.`]
    };
  }

  const byEventId = new Map<string, any>();
  for (const result of remoteResults) {
    const key = remoteKey(result);
    if (key) byEventId.set(key, result);
  }

  const results: TabletSentReconciliationResult["results"] = [];
  for (const row of rows) {
    const remote = byEventId.get(asString(row.id));
    const classified = classifyRemoteResult(remote);
    counts[classified.status] += 1;
    results.push({
      id: asString(row.id),
      status: classified.status,
      remoteStatus: asString(remote?.status) || null,
      lifecycleStatus: asString(remote?.lifecycleStatus) || null,
      remoteEventId: asString(remote?.remoteEventId ?? remote?.eventId) || null,
      remoteLedgerId: remoteLedgerId(remote) || null,
      conflictCode: conflictCode(remote) || null,
      rejectedReason: rejectedReason(remote) || null,
      reason: classified.reason
    });
    if (classified.status !== "skipped") await updateLocalStatus(asString(row.id), classified.status, remote);
  }

  const ok = counts.acked > 0 || (httpStatus >= 200 && httpStatus < 300 && counts.failed === 0);
  const reason = counts.conflict || counts.failed ? "partial" : counts.acked ? "reconciled" : "no_actionable_remote_results";
  return { ok, reason, url, checked: rows.length, sent: events.length, counts, results, errors };
}
