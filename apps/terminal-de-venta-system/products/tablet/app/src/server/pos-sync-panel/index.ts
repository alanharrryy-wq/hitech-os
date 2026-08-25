import { prisma } from "../prisma/client";
import { getTabletRuntimeMeta } from "../pos-runtime";
import { riskForStatus, statusLabel, summarizeSync, topicTitle } from "@/lib/pending-offline-sync/sync-panel-view-model";
import type { PendingSendStatus, SyncPanelItem, SyncRetryPreparationResult } from "@/lib/pending-offline-sync/sync-panel-contract";

type RawEvent = {
  id: string;
  businessId: string;
  terminalId: string | null;
  topic: string;
  aggregateId: string;
  idempotencyKey: string;
  payloadJson: string;
  source: string | null;
  schemaVersion: string | null;
  status: string;
  attempts: number;
  createdAt: Date;
  sentAt: Date | null;
  syncedAt: Date | null;
  ackedAt: Date | null;
  failedAt: Date | null;
  conflictedAt: Date | null;
  lastAttemptAt: Date | null;
  nextRetryAt: Date | null;
  remoteEventId: string | null;
  remoteLedgerId: string | null;
  remoteLifecycleStatus: string | null;
  remoteConflictCode: string | null;
  remoteRejectedReason: string | null;
  lastError: string | null;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function pickString(...values: unknown[]) {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

function payloadEnvelope(payloadJson: string) {
  try {
    const parsed = JSON.parse(payloadJson);
    return isRecord(parsed) ? parsed : {};
  } catch {
    return {};
  }
}

function nestedPayload(envelope: Record<string, unknown>) {
  return isRecord(envelope.payload) ? envelope.payload : envelope;
}

function isoOrNull(value: Date | null | undefined) {
  return value instanceof Date ? value.toISOString() : null;
}

function safeDescription(r: RawEvent) {
  const status = r.status.toLowerCase();
  const base = status === "conflict"
    ? "Requiere revisión; no se reintenta automáticamente."
    : r.lastError
      ? "Necesita revisión antes de volver a enviar."
      : "Guardado localmente para continuidad de operación.";
  if (r.topic.includes("sale")) return `Venta registrada en la Tablet. ${base}`;
  if (r.topic.includes("stock") || r.topic.includes("inventory")) return `Movimiento de inventario guardado. ${base}`;
  if (r.topic.includes("shift")) return `Movimiento de turno guardado. ${base}`;
  return `Evento operativo guardado. ${base}`;
}

function toItem(r: RawEvent): SyncPanelItem {
  const status = r.status.toLowerCase() as PendingSendStatus;
  const envelope = payloadEnvelope(r.payloadJson);
  const payload = nestedPayload(envelope);
  const eventId = pickString(envelope.eventId, r.id) || r.id;
  const terminalId = pickString(envelope.terminalId, payload.terminalId, r.terminalId) || null;
  const aggregateId = pickString(envelope.aggregateId, r.aggregateId, r.id) || r.id;
  return {
    id: r.id,
    eventId,
    title: topicTitle(r.topic),
    description: safeDescription(r),
    status,
    statusLabel: statusLabel(status),
    risk: riskForStatus(status, r.attempts),
    attempts: r.attempts,
    createdAt: r.createdAt.toISOString(),
    canRetry: status === "pending" || status === "failed",
    provenance: {
      source: pickString(envelope.source, r.source) || null,
      businessId: pickString(envelope.businessId, r.businessId) || r.businessId,
      storeId: pickString(envelope.storeId, payload.storeId) || null,
      terminalId,
      deviceId: pickString(envelope.deviceId, payload.deviceId, terminalId) || null,
      actorId: pickString(envelope.actorId, payload.actorId, payload.cashierId, payload.cashier) || null,
      aggregateId,
      originRecordId: pickString(
        envelope.originRecordId,
        payload.sourceRecordId,
        payload.saleId,
        payload.returnId,
        payload.productId,
        payload.cashSessionId,
        aggregateId
      ) || null,
      idempotencyKey: pickString(envelope.idempotencyKey, r.idempotencyKey) || null,
      correlationId: pickString(envelope.correlationId) || null,
      traceId: pickString(envelope.traceId) || null
    },
    delivery: {
      sentAt: isoOrNull(r.sentAt),
      syncedAt: isoOrNull(r.syncedAt),
      ackedAt: isoOrNull(r.ackedAt),
      failedAt: isoOrNull(r.failedAt),
      conflictedAt: isoOrNull(r.conflictedAt),
      lastAttemptAt: isoOrNull(r.lastAttemptAt),
      nextRetryAt: isoOrNull(r.nextRetryAt),
      remoteEventId: r.remoteEventId,
      remoteLedgerId: r.remoteLedgerId,
      remoteLifecycleStatus: r.remoteLifecycleStatus,
      remoteConflictCode: r.remoteConflictCode,
      remoteRejectedReason: r.remoteRejectedReason
    },
    resolutionOwner: status === "conflict" ? "pc_backoffice" : null,
    resolutionLabel: status === "conflict" ? "Revisión en PC / Backoffice" : null
  };
}

export async function buildPendingOfflineSyncPanel(input: { businessId: string; limit: number; status?: string | null }) {
  const where: any = { businessId: input.businessId };
  if (input.status) where.status = { in: [input.status, input.status.toUpperCase(), input.status.toLowerCase()] };
  const rows = await prisma.outboxEvent.findMany({ where, orderBy: { createdAt: "desc" }, take: input.limit });
  const items = rows.map((r: any) => toItem(r));
  const summary = summarizeSync(items);
  const runtime = getTabletRuntimeMeta();
  return {
    summary,
    items,
    diagnostics: [
      runtime.localSalesAllowed ? "Venta local disponible" : "Revisar venta local",
      summary.offlineVisible ? "Hay trabajo local por enviar" : "No hay pendientes visibles",
      `Última revisión ${new Date(summary.lastCheckedAt).toLocaleString("es-MX")}`
    ]
  };
}

export async function requestPendingRetry(input: { businessId: string; ids?: string[]; includeFailed?: boolean; includePending?: boolean }): Promise<SyncRetryPreparationResult> {
  const states: string[] = [];
  if (input.includeFailed !== false) states.push("failed", "FAILED");
  if (input.includePending) states.push("pending", "PENDING");
  const requestedIds = [...new Set((input.ids ?? []).filter((id): id is string => typeof id === "string" && Boolean(id.trim())).map((id) => id.trim()))];
  const scope: SyncRetryPreparationResult["scope"] = requestedIds.length ? "selected" : "all_failed";

  if (states.length === 0) {
    return {
      scope,
      requested: requestedIds.length || null,
      eligible: 0,
      updated: 0,
      skipped: requestedIds.length || null,
      eligibleIds: [],
      skippedIds: requestedIds,
      message: "No había eventos listos para reintentar."
    };
  }

  const where: any = { businessId: input.businessId, status: { in: states } };
  let eligibleIds: string[] = [];
  let skippedIds: string[] = [];
  let eligible = 0;

  if (requestedIds.length) {
    const rows = await prisma.outboxEvent.findMany({
      where: { businessId: input.businessId, id: { in: requestedIds } },
      select: { id: true, status: true }
    });
    const allowed = new Set(states.map((state) => state.toLowerCase()));
    eligibleIds = rows.filter((row) => allowed.has(String(row.status).toLowerCase())).map((row) => row.id);
    const eligibleSet = new Set(eligibleIds);
    skippedIds = requestedIds.filter((id) => !eligibleSet.has(id));
    eligible = eligibleIds.length;
    where.id = { in: eligibleIds };
  } else {
    eligible = await prisma.outboxEvent.count({ where });
  }

  if (eligible === 0) {
    return {
      scope,
      requested: requestedIds.length || null,
      eligible: 0,
      updated: 0,
      skipped: requestedIds.length ? skippedIds.length : null,
      eligibleIds,
      skippedIds,
      message: requestedIds.length && skippedIds.length
        ? `Ninguna de las ${requestedIds.length} operaciones seleccionadas puede reintentarse.`
        : "No había eventos listos para reintentar."
    };
  }

  const result = await prisma.outboxEvent.updateMany({
    where,
    data: {
      status: "pending",
      attempts: { increment: 1 },
      nextRetryAt: null,
      failedAt: null,
      lastError: null,
      remoteRejectedReason: null
    }
  });

  const skipped = requestedIds.length ? skippedIds.length : null;
  const detail = requestedIds.length
    ? `Preparadas ${result.count} de ${requestedIds.length}; omitidas ${skipped ?? 0}.`
    : `Preparadas ${result.count} operación(es) fallida(s).`;
  return {
    scope,
    requested: requestedIds.length || null,
    eligible,
    updated: result.count,
    skipped,
    eligibleIds,
    skippedIds,
    message: result.count > 0
      ? `${detail} Se enviarán cuando haya conexión.`
      : "No había eventos listos para reintentar."
  };
}
