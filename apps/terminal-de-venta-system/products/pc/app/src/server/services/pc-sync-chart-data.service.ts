import { buildPcSyncCommandLifecycleTimelineViewModel, buildPcTabletCatalogFreshnessGridViewModel, buildPrismaInsightEnvelope } from "@prisma-charts/prismaChartAdapters";
import type {
  PcSyncCommandType,
  PrismaChartQuality,
  PrismaInsightEnvelope,
  SyncCommandLifecycleEvent,
  TabletCatalogEntityName,
  TabletCatalogFreshnessGridRow,
  TabletCatalogFreshnessStatus,
  TabletCatalogRecommendedAction
} from "@prisma-charts/prismaChartContracts";
import { buildAdapterQuality } from "@prisma-charts/prismaChartQuality";
import { getPcCatalogDeltaStatus } from "@/server/services/catalog-delta-export.service";
import { prisma } from "@/server/prisma/client";

const DEFAULT_BUSINESS_ID = "biz_hitech_default";
const CATALOG_STREAM = "pc.catalog.delta.v1";
const EXPORT_AUDIT_TOPIC = "pc.catalog.delta.exported";
const GOVERNANCE_COMMAND_TOPIC = "pc.tablet.governance_command";
const CATALOG_ENTITIES: TabletCatalogEntityName[] = [
  "Product",
  "Brand",
  "Supplier",
  "ProductSupplier",
  "PriceList",
  "PriceListItem",
  "TaxRate",
  "DropdownCatalog",
  "DropdownOption"
];

type ChartQuery = {
  businessId?: string | null;
  terminalId?: string | null;
  limit?: number | string | null;
};

function asString(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function clampLimit(value: unknown, fallback = 80) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(1, Math.min(Math.trunc(parsed), 200));
}

function iso(value: unknown) {
  if (value instanceof Date) return value.toISOString();
  if (!value) return null;
  const date = new Date(String(value));
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function parseJson(value: unknown): Record<string, any> {
  if (!value || typeof value !== "string") return {};
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
  } catch {
    return {};
  }
}

function numberValue(...values: unknown[]) {
  for (const value of values) {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return 0;
}

function summarizeError(value: unknown) {
  const raw = asString(value);
  if (!raw) return null;
  return raw.replace(/\s+/g, " ").slice(0, 180);
}

function minutesSince(value: string | null, nowMs = Date.now()) {
  if (!value) return null;
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) return null;
  return Math.max(0, Math.round((nowMs - parsed) / 60_000));
}

async function safe<T>(operation: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await operation();
  } catch {
    return fallback;
  }
}

async function resolveBusinessId(input?: string | null) {
  const explicit = asString(input);
  if (explicit) return explicit;
  const db = prisma as any;
  const business = await safe<any | null>(() => db.business.findFirst({ select: { id: true }, orderBy: { createdAt: "asc" } }), null);
  return business?.id ?? DEFAULT_BUSINESS_ID;
}

function deviceKey(row: any) {
  return asString(row?.deviceId) || asString(row?.terminalId) || asString(row?.source) || "unknown-tablet";
}

function terminalLabel(heartbeat: any, checkpoint: any, key: string) {
  const heartbeatMeta = parseJson(heartbeat?.metadataJson);
  const checkpointMeta = parseJson(checkpoint?.metadataJson);
  return asString(heartbeatMeta.label) || asString(heartbeatMeta.terminalLabel) || asString(checkpointMeta.terminalLabel) || key;
}

function commandTypeFromMode(mode: unknown): PcSyncCommandType {
  const value = asString(mode).toLowerCase();
  if (value === "bootstrap") return "bootstrap";
  if (value === "resync") return "resync";
  if (value.includes("runtime")) return "runtime_refresh";
  return "catalog_delta";
}

function freshnessStatus(input: {
  latestCursor: string | null;
  checkpointCursor: string | null;
  lastSuccessfulPullAt: string | null;
  lastAttemptedPullAt: string | null;
  lastError: string | null;
}): TabletCatalogFreshnessStatus {
  if (input.lastError) return "error";
  if (!input.latestCursor) return "unknown";
  if (input.checkpointCursor && input.checkpointCursor === input.latestCursor) return "fresh";
  const successfulAge = minutesSince(input.lastSuccessfulPullAt);
  const attemptedAge = minutesSince(input.lastAttemptedPullAt);
  if (successfulAge !== null && successfulAge <= 60 && attemptedAge !== null && attemptedAge <= 60) return "warning";
  if (successfulAge !== null && successfulAge > 24 * 60) return "stale";
  if (!input.checkpointCursor) return "unknown";
  return "warning";
}

function recommendedAction(status: TabletCatalogFreshnessStatus, hasCheckpoint: boolean, latestMode: string | null): TabletCatalogRecommendedAction {
  if (status === "fresh") return "none";
  if (status === "error") return "investigate";
  if (!hasCheckpoint) return "bootstrap";
  if (status === "stale" || latestMode === "resync") return "resync";
  if (status === "warning") return "pull_delta";
  return "investigate";
}

function resultCounts(meta: Record<string, any>, conflicts: any[], attempts: any[]) {
  const result = meta.result ?? meta.resultCounts ?? meta.counts ?? {};
  const duplicateAttempts = attempts.filter((attempt) => String(attempt.status ?? attempt.lifecycleStatus ?? "").toLowerCase().includes("duplicate")).length;
  return {
    applied: numberValue(result.applied, meta.applied),
    rejected: numberValue(result.rejected, meta.rejected),
    conflicted: numberValue(result.conflicted, result.conflicts, meta.conflicted, conflicts.length),
    duplicated: numberValue(result.duplicated, result.duplicates, meta.duplicated, duplicateAttempts)
  };
}

function entityCountsFrom(value: unknown) {
  const output: Partial<Record<TabletCatalogEntityName, number>> = {};
  const record = value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
  for (const entity of CATALOG_ENTITIES) output[entity] = numberValue(record[entity]);
  return output;
}

function buildQuality(generatedAt: string, rows: number, warnings: string[], label: string): PrismaChartQuality {
  const confidence = rows > 0 ? 74 : warnings.length ? 52 : 60;
  return buildAdapterQuality(
    generatedAt,
    "server",
    label,
    confidence,
    warnings,
    "partial",
    "PC chart endpoints use the real PC catalog export ledger. Tablet-local checkpoint visibility is partial unless reported back through PC heartbeat/checkpoint evidence."
  );
}

export async function getPcTabletCatalogFreshnessGridChart(input: ChartQuery = {}): Promise<PrismaInsightEnvelope<TabletCatalogFreshnessGridRow[]>> {
  const db = prisma as any;
  const businessId = await resolveBusinessId(input.businessId);
  const terminalFilter = asString(input.terminalId);
  const [catalogStatus, heartbeats, checkpoints, conflicts, attempts] = await Promise.all([
    getPcCatalogDeltaStatus({ businessId }),
    safe(() => db.deviceHeartbeat.findMany({ where: { businessId, ...(terminalFilter ? { deviceId: terminalFilter } : {}) }, orderBy: { lastSeenAt: "desc" }, take: 160 }), [] as any[]),
    safe(() => db.syncCheckpoint.findMany({ where: { businessId, stream: CATALOG_STREAM, ...(terminalFilter ? { OR: [{ deviceId: terminalFilter }, { terminalId: terminalFilter }] } : {}) }, orderBy: { checkpointAt: "desc" }, take: 160 }), [] as any[]),
    safe(() => db.syncConflict.findMany({ where: { businessId, ...(terminalFilter ? { OR: [{ deviceId: terminalFilter }, { terminalId: terminalFilter }] } : {}) }, orderBy: { detectedAt: "desc" }, take: 160 }), [] as any[]),
    safe(() => db.syncAttempt.findMany({ where: { businessId, ...(terminalFilter ? { OR: [{ deviceId: terminalFilter }, { terminalId: terminalFilter }] } : {}) }, orderBy: { createdAt: "desc" }, take: 160 }), [] as any[])
  ]);
  const latestCursor = catalogStatus.latestExport?.cursor ?? null;
  const latestMode = catalogStatus.latestExport?.mode ?? null;
  const keys = new Map<string, { heartbeat: any | null; checkpoint: any | null }>();
  for (const heartbeat of heartbeats) keys.set(deviceKey(heartbeat), { heartbeat, checkpoint: null });
  for (const checkpoint of checkpoints) {
    const key = deviceKey(checkpoint);
    const current = keys.get(key) ?? { heartbeat: null, checkpoint: null };
    if (!current.checkpoint) current.checkpoint = checkpoint;
    keys.set(key, current);
  }

  const rows = Array.from(keys.entries()).map(([key, value]): TabletCatalogFreshnessGridRow => {
    const heartbeatMeta = parseJson(value.heartbeat?.metadataJson);
    const checkpointMeta = parseJson(value.checkpoint?.metadataJson);
    const catalogMeta = checkpointMeta.catalogPull ?? checkpointMeta.catalog ?? heartbeatMeta.catalogPull ?? heartbeatMeta.catalog ?? {};
    const deviceConflicts = conflicts.filter((conflict) => deviceKey(conflict) === key || !conflict.deviceId);
    const deviceAttempts = attempts.filter((attempt) => deviceKey(attempt) === key || !attempt.deviceId);
    const lastSuccessfulPullAt = iso(catalogMeta.lastSuccessfulPullAt ?? catalogMeta.lastSuccessAt ?? value.checkpoint?.checkpointAt) ?? null;
    const lastAttemptedPullAt = iso(catalogMeta.lastAttemptedPullAt ?? catalogMeta.lastAttemptAt ?? deviceAttempts[0]?.createdAt ?? value.heartbeat?.lastSeenAt) ?? null;
    const checkpointCursor = asString(catalogMeta.cursor ?? catalogMeta.checkpointCursor ?? value.checkpoint?.cursorValue) || null;
    const lastErrorSummary = summarizeError(catalogMeta.lastError ?? value.checkpoint?.lastError ?? deviceAttempts.find((attempt) => attempt.errorCode)?.errorCode ?? deviceConflicts[0]?.detail);
    const status = freshnessStatus({ latestCursor, checkpointCursor, lastSuccessfulPullAt, lastAttemptedPullAt, lastError: lastErrorSummary });
    const counts = resultCounts(catalogMeta, deviceConflicts, deviceAttempts);
    const behind = checkpointCursor && latestCursor && checkpointCursor === latestCursor ? 0 : numberValue(catalogStatus.latestExport?.total);
    const action = recommendedAction(status, Boolean(checkpointCursor), latestMode);
    const entityResults = catalogMeta.byEntity ?? catalogMeta.entities ?? {};
    const entityStatuses = CATALOG_ENTITIES.map((entityType) => {
      const entityMeta = entityResults[entityType] ?? {};
      const exportedCount = numberValue(catalogStatus.latestExport?.byEntity?.[entityType]);
      const conflictedCount = deviceConflicts.filter((conflict) => String(conflict.aggregateId ?? conflict.topic ?? "").includes(entityType)).length;
      const appliedCount = numberValue(entityMeta.applied, status === "fresh" ? exportedCount : 0);
      const rejectedCount = numberValue(entityMeta.rejected);
      const duplicatedCount = numberValue(entityMeta.duplicated);
      const entityStatus: TabletCatalogFreshnessStatus = lastErrorSummary
        ? "error"
        : conflictedCount > 0 || rejectedCount > 0
          ? "warning"
          : status === "fresh" || appliedCount >= exportedCount
            ? "fresh"
            : status;
      return {
        entityType,
        status: entityStatus,
        pcRowCount: numberValue(catalogStatus.tableCounts[entityType]),
        exportedCount,
        appliedCount,
        rejectedCount,
        conflictedCount,
        duplicatedCount,
        lastCursor: checkpointCursor,
        note: entityStatus === "fresh" ? "Checkpoint evidence is current for this entity." : "PC has partial or stale Tablet checkpoint evidence."
      };
    });
    return {
      terminalId: key,
      terminalLabel: terminalLabel(value.heartbeat, value.checkpoint, key),
      storeId: asString(heartbeatMeta.storeId ?? checkpointMeta.storeId) || null,
      stream: CATALOG_STREAM,
      lastSuccessfulPullAt,
      lastAttemptedPullAt,
      checkpointCursor,
      checkpointSummary: checkpointCursor ? `cursor ${checkpointCursor}` : "no PC-visible Tablet catalog checkpoint",
      freshnessStatus: status,
      entityStatuses,
      counts: {
        applied: counts.applied,
        rejected: counts.rejected,
        conflicted: counts.conflicted,
        duplicated: counts.duplicated,
        pending: status === "fresh" ? 0 : Math.max(0, behind - counts.applied),
        behind
      },
      recommendedAction: action,
      lastErrorSummary,
      evidenceRefs: [value.checkpoint?.id, value.heartbeat?.id, catalogStatus.latestExport?.id].filter(Boolean)
    };
  }).sort((a, b) => a.terminalId.localeCompare(b.terminalId));

  const generatedAt = new Date().toISOString();
  const warnings = [
    rows.length ? "" : "No PC-visible Tablet heartbeat/checkpoint rows for catalog pull.",
    catalogStatus.latestExport ? "" : "No PC catalog export has been generated yet."
  ].filter(Boolean);
  const data = buildPcTabletCatalogFreshnessGridViewModel({
    generatedAt,
    catalogSync: {
      generatedAt,
      sourceLabel: "PC catalog export ledger + DeviceHeartbeat/SyncCheckpoint partial Tablet evidence",
      warnings,
      tabletCatalogFreshnessGrid: rows
    }
  }, { mockFallback: { useMockFallback: false, reason: "Production PC chart endpoint does not use shared mocks." } });
  const quality = buildQuality(generatedAt, rows.length, warnings, "PC catalog export ledger + Tablet checkpoint evidence (partial)");
  return buildPrismaInsightEnvelope("pc", data, { endpoint: "GET /api/charts/pc/tablet-catalog-freshness-grid", businessId, terminalId: terminalFilter || null }, quality);
}

function lifecycleFromAuditEvent(event: any): SyncCommandLifecycleEvent {
  const after = parseJson(event.afterJson);
  const meta = parseJson(event.metadataJson);
  const counts = after.counts ?? {};
  return {
    commandId: event.id,
    terminalId: after.terminalId ?? null,
    terminalLabel: after.target ?? after.terminalId ?? "all",
    commandType: commandTypeFromMode(after.mode),
    status: event.topic === EXPORT_AUDIT_TOPIC ? "exported" : "queued",
    timestamp: iso(event.createdAt) ?? new Date(0).toISOString(),
    elapsedMs: null,
    actor: after.requestedBy ?? meta.requestedBy ?? "pc-operator",
    source: "pc.audit_event",
    stream: after.stream ?? CATALOG_STREAM,
    entityCounts: entityCountsFrom(counts.byEntity),
    resultCounts: { applied: 0, rejected: 0, conflicted: 0, duplicated: meta.status === "duplicate" ? 1 : 0 },
    reason: summarizeError(meta.error ?? after.error) ?? null,
    recommendedAction: event.topic === EXPORT_AUDIT_TOPIC ? "pull_delta" : "none",
    evidenceRef: event.id
  };
}

function lifecycleStatusFrom(value: unknown): SyncCommandLifecycleEvent["status"] {
  const status = asString(value).toLowerCase();
  if (status.includes("applied") || status.includes("reconciled") || status.includes("projected")) return "applied";
  if (status.includes("reject")) return "rejected";
  if (status.includes("conflict")) return "conflicted";
  if (status.includes("duplicate")) return "duplicated";
  if (status.includes("fail") || status.includes("dead")) return "failed";
  if (status.includes("pull")) return "pulled";
  if (status.includes("queue") || status.includes("pending")) return "queued";
  if (status.includes("export")) return "exported";
  if (status.includes("apply")) return "applying";
  return "unknown";
}

export async function getPcSyncCommandLifecycleTimelineChart(input: ChartQuery = {}): Promise<PrismaInsightEnvelope<SyncCommandLifecycleEvent[]>> {
  const db = prisma as any;
  const businessId = await resolveBusinessId(input.businessId);
  const limit = clampLimit(input.limit, 80);
  const terminalFilter = asString(input.terminalId);
  const whereTerminal = terminalFilter ? { OR: [{ deviceId: terminalFilter }, { terminalId: terminalFilter }] } : {};
  const [exportEvents, commandEvents, attempts, conflicts, checkpoints] = await Promise.all([
    safe(() => db.auditEvent.findMany({ where: { businessId, topic: EXPORT_AUDIT_TOPIC }, orderBy: { createdAt: "desc" }, take: limit }), [] as any[]),
    safe(() => db.auditEvent.findMany({ where: { businessId, topic: GOVERNANCE_COMMAND_TOPIC }, orderBy: { createdAt: "desc" }, take: limit }), [] as any[]),
    safe(() => db.syncAttempt.findMany({ where: { businessId, ...whereTerminal }, orderBy: { createdAt: "desc" }, take: limit }), [] as any[]),
    safe(() => db.syncConflict.findMany({ where: { businessId, ...whereTerminal }, orderBy: { detectedAt: "desc" }, take: limit }), [] as any[]),
    safe(() => db.syncCheckpoint.findMany({ where: { businessId, stream: CATALOG_STREAM, ...whereTerminal }, orderBy: { checkpointAt: "desc" }, take: limit }), [] as any[])
  ]);
  const events: SyncCommandLifecycleEvent[] = [
    ...exportEvents.map(lifecycleFromAuditEvent),
    ...commandEvents.map(lifecycleFromAuditEvent),
    ...attempts.map((attempt): SyncCommandLifecycleEvent => {
      const diagnostics = parseJson(attempt.diagnosticsJson);
      const status = lifecycleStatusFrom(attempt.lifecycleStatus ?? attempt.status);
      return {
        commandId: attempt.id,
        terminalId: attempt.deviceId ?? attempt.terminalId ?? null,
        terminalLabel: attempt.deviceId ?? attempt.terminalId ?? "tablet",
        commandType: commandTypeFromMode(attempt.topic),
        status,
        timestamp: iso(attempt.finishedAt ?? attempt.createdAt) ?? new Date(0).toISOString(),
        elapsedMs: numberValue(attempt.durationMs),
        actor: attempt.source ?? "sync-attempt",
        source: "pc.sync_attempt",
        stream: attempt.topic?.includes("catalog") ? CATALOG_STREAM : (attempt.topic ?? CATALOG_STREAM),
        entityCounts: entityCountsFrom(diagnostics.byEntity ?? diagnostics.entityCounts),
        resultCounts: { applied: status === "applied" ? 1 : 0, rejected: status === "rejected" ? 1 : 0, conflicted: status === "conflicted" ? 1 : 0, duplicated: status === "duplicated" ? 1 : 0 },
        reason: summarizeError(attempt.errorCode ?? diagnostics.error ?? diagnostics.reason),
        recommendedAction: status === "failed" || status === "rejected" || status === "conflicted" ? "investigate" : "none",
        evidenceRef: attempt.id
      };
    }),
    ...conflicts.map((conflict): SyncCommandLifecycleEvent => ({
      commandId: conflict.id,
      terminalId: conflict.deviceId ?? conflict.terminalId ?? null,
      terminalLabel: conflict.deviceId ?? conflict.terminalId ?? "tablet",
      commandType: commandTypeFromMode(conflict.topic),
      status: "conflicted",
      timestamp: iso(conflict.detectedAt) ?? new Date(0).toISOString(),
      elapsedMs: null,
      actor: conflict.source ?? "sync-conflict",
      source: "pc.sync_conflict",
      stream: conflict.topic?.includes("catalog") ? CATALOG_STREAM : (conflict.topic ?? CATALOG_STREAM),
      entityCounts: {},
      resultCounts: { applied: 0, rejected: 0, conflicted: 1, duplicated: 0 },
      reason: summarizeError(conflict.conflictCode ?? conflict.detail),
      recommendedAction: "investigate",
      evidenceRef: conflict.id
    })),
    ...checkpoints.map((checkpoint): SyncCommandLifecycleEvent => {
      const meta = parseJson(checkpoint.metadataJson);
      const counts = resultCounts(meta, [], []);
      return {
        commandId: checkpoint.id,
        terminalId: checkpoint.deviceId ?? checkpoint.terminalId ?? null,
        terminalLabel: checkpoint.deviceId ?? checkpoint.terminalId ?? "tablet",
        commandType: "catalog_delta",
        status: lifecycleStatusFrom(checkpoint.lifecycleStatus ?? checkpoint.status) === "unknown" ? "applied" : lifecycleStatusFrom(checkpoint.lifecycleStatus ?? checkpoint.status),
        timestamp: iso(checkpoint.checkpointAt) ?? new Date(0).toISOString(),
        elapsedMs: null,
        actor: checkpoint.source ?? "sync-checkpoint",
        source: "pc.sync_checkpoint",
        stream: checkpoint.stream ?? CATALOG_STREAM,
        entityCounts: entityCountsFrom(meta.byEntity ?? meta.entityCounts),
        resultCounts: counts,
        reason: summarizeError(meta.error ?? meta.lastError),
        recommendedAction: "none",
        evidenceRef: checkpoint.id
      };
    })
  ].filter((event) => !terminalFilter || event.terminalId === terminalFilter || event.terminalLabel === terminalFilter);

  const sorted = events
    .sort((a, b) => Date.parse(b.timestamp) - Date.parse(a.timestamp) || a.commandId.localeCompare(b.commandId))
    .slice(0, limit);
  const generatedAt = new Date().toISOString();
  const warnings = sorted.length ? [] : ["No PC-visible catalog sync lifecycle events for the selected scope."];
  const data = buildPcSyncCommandLifecycleTimelineViewModel({
    generatedAt,
    catalogSync: {
      generatedAt,
      sourceLabel: "PC catalog export, governance command, attempt, conflict, and checkpoint ledger",
      warnings,
      syncCommandLifecycleTimeline: sorted
    }
  }, { mockFallback: { useMockFallback: false, reason: "Production PC chart endpoint does not use shared mocks." } });
  const quality = buildQuality(generatedAt, sorted.length, warnings, "PC sync command lifecycle ledger (partial Tablet evidence)");
  return buildPrismaInsightEnvelope("pc", data, { endpoint: "GET /api/charts/pc/sync-command-lifecycle-timeline", businessId, terminalId: terminalFilter || null, limit }, quality);
}
