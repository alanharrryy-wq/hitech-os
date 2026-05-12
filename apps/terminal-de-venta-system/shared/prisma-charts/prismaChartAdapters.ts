import type {
  ActionPriorityStackDatum,
  CausalFlowRibbonDatum,
  ConfidenceBand,
  DecisionLedgerPoint,
  FreshnessBeacon,
  HealthRadarAxis,
  IncidentSparkCard,
  InventoryRiskNode,
  OperationalDensityCell,
  OperationalWaterfallStep,
  OwnerPulsePoint,
  PrismaChartAdapterSources,
  PrismaChartQuality,
  PrismaChartMockFallbackPolicy,
  PrismaChartSurface,
  PrismaInsightEnvelope,
  PrismaMobileChartSource,
  PrismaMobileChartsViewModel,
  PrismaPcChartSource,
  PrismaPcChartsViewModel,
  PrismaTabletChartSource,
  PrismaTabletChartsViewModel,
  PrismaTripleAppChartsViewModel,
  ServiceDependencyEdge,
  ServiceDependencyNode,
  ShiftPulseBucket,
  SyncOutboxMatrixCell
} from "./prismaChartContracts";
import { mockMobileCharts, mockPcCharts, mockTabletCharts, PRISMA_CHART_MOCK_GENERATED_AT } from "./prismaChartMocks";
import { buildAdapterQuality, buildMockQuality } from "./prismaChartQuality";

type SourceResult<T> = {
  data: T;
  quality: PrismaChartQuality;
};

const PC_FALLBACK_REASON = "Some PC chart dimensions still need a dedicated canonical source; deterministic fallback remains available.";
const TABLET_FALLBACK_REASON = "Tablet exposes current operational state; historical buckets or type breakdowns may stay deterministic fallback.";
const MOBILE_FALLBACK_REASON = "Mobile snapshot is real where available; historical trends and sparse incident series may stay fallback/partial.";

type PrismaChartAdapterOptions = {
  mockFallback?: PrismaChartMockFallbackPolicy;
};

type GraphLike = {
  nodes: unknown[];
  edges: unknown[];
};

const MOCK_FALLBACK_DISABLED_VALUES = new Set(["0", "false", "off", "no", "disabled"]);
const MOCK_FALLBACK_ENABLED_VALUES = new Set(["1", "true", "on", "yes", "enabled"]);
const MOCK_FALLBACK_DISABLED_REASON = "Mock fallback disabled by PRISMA_CHARTS_MOCKS_FALLBACK; missing dimensions must render empty/partial/unavailable instead of deterministic mock data.";

function readMockFallbackEnv(): boolean {
  const runtime = globalThis as typeof globalThis & { process?: { env?: Record<string, string | undefined> } };
  const raw = runtime.process?.env?.PRISMA_CHARTS_MOCKS_FALLBACK ?? runtime.process?.env?.NEXT_PUBLIC_PRISMA_CHARTS_MOCKS_FALLBACK;
  if (!raw) return true;
  const normalized = raw.trim().toLowerCase();
  if (MOCK_FALLBACK_DISABLED_VALUES.has(normalized)) return false;
  if (MOCK_FALLBACK_ENABLED_VALUES.has(normalized)) return true;
  return true;
}

function resolveMockFallbackPolicy(options?: PrismaChartAdapterOptions): Required<PrismaChartMockFallbackPolicy> {
  const envAllowsMockFallback = readMockFallbackEnv();
  const useMockFallback = options?.mockFallback?.useMockFallback ?? envAllowsMockFallback;
  return {
    useMockFallback,
    reason: options?.mockFallback?.reason ?? (useMockFallback
      ? "PRISMA_CHARTS_MOCKS_FALLBACK allows deterministic fallback."
      : MOCK_FALLBACK_DISABLED_REASON)
  };
}

function mockFallbackAllowed(options?: PrismaChartAdapterOptions): boolean {
  return resolveMockFallbackPolicy(options).useMockFallback;
}

function fallbackPolicyReason(defaultReason: string, options?: PrismaChartAdapterOptions): string {
  return mockFallbackAllowed(options) ? defaultReason : MOCK_FALLBACK_DISABLED_REASON;
}

function mockFallback<T>(mockData: T, options?: PrismaChartAdapterOptions): T {
  if (mockFallbackAllowed(options)) return mockData;
  if (Array.isArray(mockData)) return [] as T;
  if (mockData && typeof mockData === "object" && "nodes" in mockData && "edges" in mockData) {
    return { nodes: [], edges: [] } as GraphLike as T;
  }
  return mockData;
}

function buildUnavailableQuality(sourceLabel: string, todo: string, options?: PrismaChartAdapterOptions): PrismaChartQuality {
  return buildAdapterQuality(
    nowIso(),
    "adapter",
    sourceLabel,
    0,
    ["mock-fallback-disabled"],
    "unavailable",
    `${resolveMockFallbackPolicy(options).reason} ${todo}`
  );
}

function nowIso() {
  return new Date().toISOString();
}

function sourceTime(...values: Array<string | null | undefined>) {
  return values.find((value) => typeof value === "string" && !Number.isNaN(Date.parse(value))) ?? nowIso();
}

function minutesAgo(iso: string | null | undefined, generatedAt: string) {
  if (!iso) return 999;
  const source = Date.parse(iso);
  const generated = Date.parse(generatedAt);
  if (Number.isNaN(source) || Number.isNaN(generated)) return 999;
  return Math.max(0, Math.round((generated - source) / 60_000));
}

function clamp(value: number, min = 0, max = 100) {
  return Math.max(min, Math.min(max, Math.round(Number.isFinite(value) ? value : 0)));
}

function firstKpi(source: PrismaPcChartSource | undefined, key: string) {
  return source?.dashboard?.kpis?.find((item) => item.key === key) ?? null;
}

function parseMoneyCents(label: string | undefined) {
  if (!label) return 0;
  const normalized = label.replace(/[^\d.-]/g, "");
  const value = Number(normalized);
  return Number.isFinite(value) ? Math.round(value * 100) : 0;
}

function numberOrZero(value: unknown) {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function lower(value: string | undefined | null) {
  return (value ?? "").toLowerCase();
}

function pcGeneratedAt(source?: PrismaPcChartSource) {
  return sourceTime(source?.dashboard?.meta?.generatedAt, source?.generatedAt);
}

function buildPcQuality(source?: PrismaPcChartSource, options?: PrismaChartAdapterOptions): PrismaChartQuality {
  if (!source?.dashboard && !source?.triDbStatus) {
    if (mockFallbackAllowed(options)) return buildMockQuality(PRISMA_CHART_MOCK_GENERATED_AT, "PC mock fallback", "No safe PC source was provided to ChartOps adapters.");
    return buildUnavailableQuality("PC source unavailable", "No safe PC source was provided to ChartOps adapters.", options);
  }
  const generatedAt = pcGeneratedAt(source);
  const warnings = [
    ...(source.dashboard?.meta?.warnings ?? []),
    ...(source.triDbStatus?.warnings ?? []),
    ...(source.errors ?? [])
  ];
  const confidence = source.dashboard?.meta?.persistence === "available" ? 66 : source.triDbStatus?.mode === "real" ? 58 : 42;
  return buildAdapterQuality(
    generatedAt,
    "server",
    warnings.length ? "PC canonical/bridge adapter (partial)" : "PC canonical/bridge adapter",
    confidence,
    warnings,
    "partial",
    fallbackPolicyReason(PC_FALLBACK_REASON, options)
  );
}

function severityFromCounts(failed: number, conflicts: number): CausalFlowRibbonDatum["severity"] {
  if (conflicts > 0) return "CRITICAL";
  if (failed > 0) return "ERROR";
  return "INFO";
}

export function buildPcCausalFlowRibbonViewModel(source?: PrismaPcChartSource, options?: PrismaChartAdapterOptions): CausalFlowRibbonDatum[] {
  if (!source?.dashboard && !source?.triDbStatus) return mockFallback(mockPcCharts.causalFlowRibbon, options);
  const generatedAt = pcGeneratedAt(source);
  const pending = numberOrZero(source.dashboard?.sync?.pendingEvents);
  const failed = numberOrZero(source.dashboard?.sync?.failedEvents);
  const conflicts = numberOrZero(source.dashboard?.sync?.conflictCount);
  const lowStock = Number(firstKpi(source, "lowStockCount")?.value ?? source.triDbStatus?.pc?.lowStockCount ?? 0);
  const rows: CausalFlowRibbonDatum[] = [];
  if (pending + failed + conflicts > 0) {
    rows.push({
      sourceModule: "Sync",
      causeType: failed > 0 ? "failed_events" : conflicts > 0 ? "conflict_events" : "pending_events",
      effectType: "governance_attention",
      actionTarget: "Review PC ingest",
      weight: Math.max(1, pending + failed * 3 + conflicts * 4),
      severity: severityFromCounts(failed, conflicts),
      confidence: 68,
      evidenceCount: pending + failed + conflicts,
      incidentIds: ["pc-sync-summary"],
      firstSeenAt: source.dashboard?.sync?.lastOutboxEventAt ?? generatedAt,
      lastSeenAt: source.dashboard?.sync?.lastIngestAt ?? generatedAt,
      ownerRole: "Backoffice"
    });
  }
  if (lowStock > 0) {
    rows.push({
      sourceModule: "Inventory",
      causeType: "low_stock_count",
      effectType: "continuity_risk",
      actionTarget: "Review replenishment",
      weight: Math.max(1, lowStock),
      severity: lowStock > 5 ? "ERROR" : "WARN",
      confidence: 58,
      evidenceCount: lowStock,
      incidentIds: ["pc-low-stock"],
      firstSeenAt: generatedAt,
      lastSeenAt: generatedAt,
      ownerRole: "Inventory"
    });
  }
  if (source.triDbStatus) {
    rows.push({
      sourceModule: "Bridge Status",
      causeType: source.triDbStatus.parityOk ? "pc_covers_tablet" : "parity_gap",
      effectType: "audit_traceability",
      actionTarget: source.triDbStatus.parityOk ? "Keep event sync primary" : "Inspect parity",
      weight: Math.max(1, source.triDbStatus.bridgeTablesProjected ?? 1),
      severity: source.triDbStatus.parityOk ? "INFO" : "WARN",
      confidence: source.triDbStatus.mode === "real" ? 62 : 38,
      evidenceCount: source.triDbStatus.bridgeTablesProjected ?? 0,
      incidentIds: ["tri-db-status"],
      firstSeenAt: generatedAt,
      lastSeenAt: generatedAt,
      ownerRole: "Audit"
    });
  }
  return rows.length ? rows : mockFallback(mockPcCharts.causalFlowRibbon, options);
}

export function buildPcOperationalDensityFieldViewModel(source?: PrismaPcChartSource, options?: PrismaChartAdapterOptions): OperationalDensityCell[] {
  if (!source?.dashboard && !source?.triDbStatus) return mockFallback(mockPcCharts.operationalDensityField, options);
  const generatedAt = pcGeneratedAt(source);
  const modules = [
    { id: "sales", name: "Sales", events: numberOrZero(source.dashboard?.topSkus?.length), warn: 0, error: 0, pressure: firstKpi(source, "ticketCountToday")?.value === "0" ? 18 : 42 },
    { id: "sync", name: "Sync", events: numberOrZero(source.dashboard?.sync?.pendingEvents) + numberOrZero(source.dashboard?.sync?.failedEvents), warn: numberOrZero(source.dashboard?.sync?.pendingEvents), error: numberOrZero(source.dashboard?.sync?.failedEvents), pressure: numberOrZero(source.dashboard?.sync?.pendingEvents) * 12 + numberOrZero(source.dashboard?.sync?.failedEvents) * 24 },
    { id: "inventory", name: "Inventory", events: Number(firstKpi(source, "lowStockCount")?.value ?? 0), warn: Number(firstKpi(source, "lowStockCount")?.value ?? 0), error: 0, pressure: Number(firstKpi(source, "lowStockCount")?.value ?? 0) * 18 },
    { id: "bridge", name: "Bridge", events: source.triDbStatus?.bridgeRowsInsertedOrUpdated ?? 0, warn: source.triDbStatus?.warnings?.length ?? 0, error: source.triDbStatus?.status === "BLOCKED" ? 1 : 0, pressure: source.triDbStatus?.parityOk ? 34 : 64 }
  ];
  return modules.map((item, index) => ({
    bucketStart: new Date(Date.parse(generatedAt) - (modules.length - index) * 15 * 60_000).toISOString(),
    bucketEnd: new Date(Date.parse(generatedAt) - (modules.length - index - 1) * 15 * 60_000).toISOString(),
    moduleId: item.id,
    moduleName: item.name,
    eventCount: item.events,
    warnCount: item.warn,
    errorCount: item.error,
    avgLatencyMs: undefined,
    staleMinutesAvg: minutesAgo(source.dashboard?.sync?.lastOutboxEventAt ?? generatedAt, generatedAt),
    retryCount: item.warn,
    pressureScore: clamp(item.pressure),
    dominantCause: item.error > 0 ? "error" : item.warn > 0 ? "warning" : "normal",
    confidence: 58
  }));
}

export function buildPcServiceDependencyGraphViewModel(source?: PrismaPcChartSource, options?: PrismaChartAdapterOptions): { nodes: ServiceDependencyNode[]; edges: ServiceDependencyEdge[] } {
  if (!source?.dashboard && !source?.triDbStatus) return mockFallback(mockPcCharts.serviceDependencyGraph, options);
  const generatedAt = pcGeneratedAt(source);
  const pcStatus = source.dashboard?.meta?.persistence === "available" ? "PASS" : "DEGRADED";
  const bridgeStatus = source.triDbStatus?.status === "READY" ? "PASS" : source.triDbStatus?.status === "BLOCKED" ? "FAIL" : "DEGRADED";
  const tabletStatus = source.triDbStatus?.tablet?.saleCount !== undefined ? "PASS" : "UNKNOWN";
  const nodes: ServiceDependencyNode[] = [
    { id: "tablet-local", label: "Tablet local", kind: "app", status: tabletStatus, port: 3120, localUrl: "http://127.0.0.1:3120", healthy: tabletStatus === "PASS", criticality: "high", owner: "Operator", lastProbeAt: generatedAt },
    { id: "pc-backoffice", label: "PC Backoffice", kind: "app", status: pcStatus, port: 3130, localUrl: "http://127.0.0.1:3130", healthy: pcStatus === "PASS", criticality: "high", owner: "Backoffice", lastProbeAt: generatedAt },
    { id: "canonical-db", label: "Canonical DB", kind: "db", status: pcStatus, healthy: pcStatus === "PASS", criticality: "high", owner: "Prisma ORM", lastProbeAt: generatedAt },
    { id: "bridge-status", label: "TRI-DB status", kind: "worker", status: bridgeStatus, healthy: bridgeStatus === "PASS", criticality: "medium", owner: "Audit", lastProbeAt: generatedAt }
  ];
  const edges: ServiceDependencyEdge[] = [
    { source: "tablet-local", target: "pc-backoffice", relation: "syncs_with", status: bridgeStatus, evidence: "status.latest.json" },
    { source: "pc-backoffice", target: "canonical-db", relation: "writes_to", status: pcStatus, evidence: "getBackofficeDashboard" },
    { source: "bridge-status", target: "canonical-db", relation: "probes", status: bridgeStatus, evidence: source.triDbStatus?.sourcePath ?? "shared/tri-db/status.latest.json" }
  ];
  return { nodes, edges };
}

export function buildPcInventoryRiskTreemapViewModel(source?: PrismaPcChartSource, options?: PrismaChartAdapterOptions): InventoryRiskNode[] {
  const topSkus = source?.dashboard?.topSkus ?? [];
  const lowStock = Number(firstKpi(source, "lowStockCount")?.value ?? source?.triDbStatus?.pc?.lowStockCount ?? 0);
  if (!topSkus.length && !lowStock) return mockFallback(mockPcCharts.inventoryRiskTreemap, options);
  const root: InventoryRiskNode = {
    id: "pc-inventory-risk",
    label: "Inventario canónico",
    level: "category",
    stockOnHand: source?.triDbStatus?.pc?.productCount ?? topSkus.length,
    reorderPoint: lowStock,
    daysOfCover: lowStock > 0 ? 1 : 7,
    velocityPerDay: topSkus.reduce((sum, item) => sum + item.qty, 0),
    stockoutRisk: lowStock > 0 ? 68 : 24,
    overstockRisk: 0,
    revenueAtRisk: topSkus.reduce((sum, item) => sum + item.totalCents, 0),
    confidence: topSkus.length ? 64 : 42
  };
  return [
    root,
    ...topSkus.slice(0, 8).map((item): InventoryRiskNode => ({
      id: `sku-${item.sku}`,
      parentId: root.id,
      label: item.sku,
      level: "sku",
      stockOnHand: item.qty,
      reorderPoint: 0,
      daysOfCover: lowStock > 0 ? 2 : 8,
      velocityPerDay: item.qty,
      stockoutRisk: lowStock > 0 ? 52 : 18,
      overstockRisk: 0,
      revenueAtRisk: item.totalCents,
      confidence: 58
    }))
  ];
}

export function buildPcDecisionLedgerTimelineViewModel(source?: PrismaPcChartSource, options?: PrismaChartAdapterOptions): DecisionLedgerPoint[] {
  if (!source?.dashboard && !source?.triDbStatus) return mockFallback(mockPcCharts.decisionLedgerTimeline, options);
  const generatedAt = pcGeneratedAt(source);
  const points: DecisionLedgerPoint[] = [
    {
      decisionId: "pc-dashboard-generated",
      time: generatedAt,
      title: "Canonical dashboard generated",
      type: "evidence",
      actorName: "PC Backoffice",
      responsibleRole: "Backoffice",
      status: source.dashboard?.meta?.persistence === "available" ? "resolved" : "blocked",
      relatedIncidentIds: [],
      evidenceCount: source.dashboard?.kpis?.length ?? 0,
      impactScore: source.dashboard?.meta?.persistence === "available" ? 32 : 76,
      beforeHealthScore: 70,
      afterHealthScore: source.dashboard?.meta?.persistence === "available" ? 82 : 54,
      confidence: 66
    }
  ];
  const sync = source.dashboard?.sync;
  if (sync && (numberOrZero(sync.pendingEvents) + numberOrZero(sync.failedEvents) + numberOrZero(sync.conflictCount)) > 0) {
    points.push({
      decisionId: "pc-sync-review",
      time: sync.lastOutboxEventAt ?? generatedAt,
      title: sync.healthLabel ?? "Sync requires review",
      type: "action",
      actorName: "PC Sync",
      responsibleRole: "Backoffice",
      status: numberOrZero(sync.conflictCount) > 0 ? "blocked" : "open",
      relatedIncidentIds: ["sync-summary"],
      evidenceCount: numberOrZero(sync.pendingEvents) + numberOrZero(sync.failedEvents) + numberOrZero(sync.conflictCount),
      impactScore: clamp(numberOrZero(sync.pendingEvents) * 8 + numberOrZero(sync.failedEvents) * 18 + numberOrZero(sync.conflictCount) * 24),
      confidence: 62
    });
  }
  if (source.triDbStatus) {
    points.push({
      decisionId: "tri-db-status-read",
      time: generatedAt,
      title: `Bridge status ${source.triDbStatus.status ?? "unknown"}`,
      type: "evidence",
      actorName: "TRI-DB bridge",
      responsibleRole: "Audit",
      status: source.triDbStatus.status === "READY" ? "resolved" : "open",
      relatedIncidentIds: ["tri-db-status"],
      evidenceCount: source.triDbStatus.bridgeTablesProjected ?? 0,
      impactScore: source.triDbStatus.parityOk ? 28 : 68,
      confidence: source.triDbStatus.mode === "real" ? 62 : 38
    });
  }
  return points;
}

export function buildPcFinancialOperationalWaterfallViewModel(source?: PrismaPcChartSource, options?: PrismaChartAdapterOptions): OperationalWaterfallStep[] {
  const salesCents = parseMoneyCents(firstKpi(source, "netSalesTodayCents")?.value);
  const topSkuCents = source?.dashboard?.topSkus?.reduce((sum, item) => sum + item.totalCents, 0) ?? 0;
  const value = salesCents || topSkuCents;
  if (!value) return mockFallback(mockPcCharts.financialOperationalWaterfall, options);
  return [
    { id: "net-sales", label: "Ventas netas", kind: "positive", value, currency: "MXN", source: "sales", relatedIds: ["pc-dashboard"], confidence: 66 },
    { id: "top-sku-signal", label: "Top SKUs", kind: "neutral", value: topSkuCents, currency: "MXN", source: "sales", relatedIds: source?.dashboard?.topSkus?.map((item) => item.sku) ?? [], confidence: source?.dashboard?.topSkus?.length ? 58 : 34 },
    { id: "net-visible", label: "Neto visible", kind: "subtotal", value, currency: "MXN", source: "sales", relatedIds: ["pc-dashboard"], confidence: 62 }
  ];
}

function buildPcCharts(source?: PrismaPcChartSource, options?: PrismaChartAdapterOptions): SourceResult<PrismaPcChartsViewModel> {
  const quality = buildPcQuality(source, options);
  return {
    quality,
    data: {
      causalFlowRibbon: buildPcCausalFlowRibbonViewModel(source, options),
      operationalDensityField: buildPcOperationalDensityFieldViewModel(source, options),
      serviceDependencyGraph: buildPcServiceDependencyGraphViewModel(source, options),
      inventoryRiskTreemap: buildPcInventoryRiskTreemapViewModel(source, options),
      decisionLedgerTimeline: buildPcDecisionLedgerTimelineViewModel(source, options),
      financialOperationalWaterfall: buildPcFinancialOperationalWaterfallViewModel(source, options)
    }
  };
}

function buildTabletQuality(source?: PrismaTabletChartSource, options?: PrismaChartAdapterOptions): PrismaChartQuality {
  if (!source?.runtime) {
    if (mockFallbackAllowed(options)) return buildMockQuality(PRISMA_CHART_MOCK_GENERATED_AT, "Tablet mock fallback", "No safe Tablet runtime source was provided to ChartOps adapters.");
    return buildUnavailableQuality("Tablet source unavailable", "No safe Tablet runtime source was provided to ChartOps adapters.", options);
  }
  const generatedAt = sourceTime(source.runtime.generatedAt, source.generatedAt);
  const warnings = [...(source.runtime.warnings ?? []), ...(source.errors ?? [])];
  const status = source.runtime.connection?.state;
  const confidence = status === "online" ? 78 : status === "pending" ? 66 : status === "review" ? 58 : 48;
  return buildAdapterQuality(generatedAt, "local", "Tablet runtime/outbox adapter", confidence, warnings, "partial", TABLET_FALLBACK_REASON);
}

export function buildTabletShiftPulseStripViewModel(source?: PrismaTabletChartSource, options?: PrismaChartAdapterOptions): ShiftPulseBucket[] {
  const runtime = source?.runtime;
  if (!runtime) return mockFallback(mockTabletCharts.shiftPulseStrip, options);
  const generatedAt = sourceTime(runtime.generatedAt, source?.generatedAt);
  const pending = numberOrZero(runtime.connection?.pendingEvents);
  const failed = numberOrZero(runtime.connection?.failedEvents);
  const conflict = numberOrZero(runtime.connection?.conflictEvents);
  const queuePressure = clamp(pending * 8 + failed * 18 + conflict * 24);
  const status: ShiftPulseBucket["status"] = failed + conflict > 0 ? "risk" : queuePressure > 55 ? "busy" : "normal";
  return [{
    bucketStart: new Date(Date.parse(generatedAt) - 30 * 60_000).toISOString(),
    bucketEnd: generatedAt,
    shiftId: runtime.shift?.cashSessionId ?? "current-shift",
    terminalId: runtime.identity?.terminalId ?? "tablet-local",
    cashierId: runtime.identity?.operatorName,
    saleCount: numberOrZero(runtime.sales?.ticketsClosed),
    grossSales: numberOrZero(runtime.sales?.totalCents),
    refundCount: 0,
    cancellationCount: 0,
    avgTicket: numberOrZero(runtime.sales?.averageTicketCents),
    offlineSaleCount: runtime.connection?.state === "offline" ? numberOrZero(runtime.sales?.ticketsClosed) : 0,
    pendingSyncCount: pending + failed + conflict,
    queuePressure,
    status
  }];
}

function classifyTabletItemType(item: { title?: string; description?: string }): SyncOutboxMatrixCell["itemType"] {
  const text = lower(`${item.title ?? ""} ${item.description ?? ""}`);
  if (text.includes("venta") || text.includes("sale")) return "sale";
  if (text.includes("devol") || text.includes("refund")) return "refund";
  if (text.includes("invent") || text.includes("stock")) return "inventory_adjustment";
  if (text.includes("turno") || text.includes("caja") || text.includes("shift")) return "cash_shift";
  if (text.includes("ticket")) return "ticket";
  if (text.includes("cliente") || text.includes("customer")) return "customer";
  return "event";
}

function normalizeSyncState(status: string | undefined): SyncOutboxMatrixCell["syncState"] {
  const value = lower(status);
  if (value === "failed" || value === "conflict") return "failed";
  if (value === "sent" || value === "acked" || value === "reconciled") return "sent";
  if (value === "sending") return "sending";
  if (value === "retrying") return "retrying";
  return "pending";
}

export function buildTabletSyncOutboxStatusMatrixViewModel(source?: PrismaTabletChartSource, options?: PrismaChartAdapterOptions): SyncOutboxMatrixCell[] {
  const items = source?.syncPanel?.items ?? [];
  const generatedAt = sourceTime(source?.runtime?.generatedAt, source?.generatedAt);
  if (items.length) {
    const grouped = new Map<string, SyncOutboxMatrixCell>();
    for (const item of items) {
      const itemType = classifyTabletItemType(item);
      const syncState = normalizeSyncState(item.status);
      const key = `${itemType}:${syncState}`;
      const current = grouped.get(key) ?? { itemType, syncState, count: 0, oldestAgeMinutes: 0, retryCount: 0, blocking: false, confidence: 76 };
      current.count += 1;
      current.oldestAgeMinutes = Math.max(current.oldestAgeMinutes, minutesAgo(item.createdAt, generatedAt));
      current.retryCount += numberOrZero(item.attempts);
      current.blocking = current.blocking || syncState === "failed" || item.canRetry === true;
      grouped.set(key, current);
    }
    return Array.from(grouped.values());
  }
  const runtime = source?.runtime;
  if (!runtime) return mockFallback(mockTabletCharts.syncOutboxStatusMatrix, options);
  const pending = numberOrZero(runtime.connection?.pendingEvents);
  const failed = numberOrZero(runtime.connection?.failedEvents);
  const conflict = numberOrZero(runtime.connection?.conflictEvents);
  const cells: SyncOutboxMatrixCell[] = [];
  if (pending) cells.push({ itemType: "event", syncState: "pending", count: pending, oldestAgeMinutes: 0, retryCount: 0, blocking: false, confidence: 62 });
  if (failed) cells.push({ itemType: "event", syncState: "failed", count: failed, oldestAgeMinutes: 0, retryCount: 0, blocking: true, confidence: 62 });
  if (conflict) cells.push({ itemType: "event", syncState: "retrying", count: conflict, oldestAgeMinutes: 0, retryCount: 0, blocking: true, confidence: 58 });
  return cells.length ? cells : [{ itemType: "event", syncState: "sent", count: 0, oldestAgeMinutes: 0, retryCount: 0, blocking: false, confidence: 70 }];
}

function buildTabletCharts(source?: PrismaTabletChartSource, options?: PrismaChartAdapterOptions): SourceResult<PrismaTabletChartsViewModel> {
  const quality = buildTabletQuality(source, options);
  return {
    quality,
    data: {
      shiftPulseStrip: buildTabletShiftPulseStripViewModel(source, options),
      syncOutboxStatusMatrix: buildTabletSyncOutboxStatusMatrixViewModel(source, options)
    }
  };
}

function buildMobileQuality(source?: PrismaMobileChartSource, options?: PrismaChartAdapterOptions): PrismaChartQuality {
  const snapshot = source?.snapshot;
  if (!snapshot) {
    if (mockFallbackAllowed(options)) return buildMockQuality(PRISMA_CHART_MOCK_GENERATED_AT, "Mobile mock fallback", "No safe Mobile snapshot source was provided to ChartOps adapters.");
    return buildUnavailableQuality("Mobile source unavailable", "No safe Mobile snapshot source was provided to ChartOps adapters.", options);
  }
  const generatedAt = sourceTime(snapshot.meta?.generatedAt, snapshot.dataQuality?.generatedAt, source?.generatedAt);
  const staleSources = [...(snapshot.dataQuality?.staleSources ?? []), ...(snapshot.dataQuality?.missingSources ?? []), ...(source?.errors ?? [])];
  const confidence = clamp((snapshot.meta?.confidence ?? snapshot.dataQuality?.confidence ?? 0.45) * 100);
  const dataStatus = staleSources.length ? "partial" : snapshot.meta?.runtimeMode === "live" ? "real" : "partial";
  return buildAdapterQuality(generatedAt, "api", `Mobile snapshot adapter (${snapshot.meta?.runtimeMode ?? "unknown"})`, confidence, staleSources, dataStatus, MOBILE_FALLBACK_REASON);
}

function operationalStatusFromMobile(status: string | undefined, score: number | null | undefined): HealthRadarAxis["status"] {
  const value = lower(status);
  if (value === "healthy" || value === "ok" || value === "live") return "PASS";
  if (value === "blocked" || value === "offline" || value === "critical") return "FAIL";
  if (score === null || score === undefined || value === "unknown") return "UNKNOWN";
  return score >= 75 ? "PASS" : score >= 45 ? "DEGRADED" : "FAIL";
}

function findDimension(source: PrismaMobileChartSource | undefined, keys: string[]) {
  return source?.snapshot?.healthRadar?.dimensions?.find((item) => keys.includes(item.key)) ?? null;
}

export function buildMobileHealthRadarCompactViewModel(source?: PrismaMobileChartSource, options?: PrismaChartAdapterOptions): HealthRadarAxis[] {
  const snapshot = source?.snapshot;
  if (!snapshot) return mockFallback(mockMobileCharts.healthRadarCompact, options);
  const generatedAt = sourceTime(snapshot.meta?.generatedAt, snapshot.dataQuality?.generatedAt, source?.generatedAt);
  const definitions: Array<{ axis: HealthRadarAxis["axis"]; label: string; keys: string[]; fallbackScore?: number | null; reason?: string }> = [
    { axis: "data_quality", label: "Calidad", keys: ["core", "mobile"], fallbackScore: (snapshot.dataQuality?.completeness ?? 0) * 100, reason: "data quality" },
    { axis: "sync", label: "Sync", keys: ["sync"], fallbackScore: snapshot.sync?.status === "ok" ? 92 : snapshot.sync?.status === "delayed" ? 62 : snapshot.sync?.status === "blocked" ? 34 : null, reason: snapshot.sync?.status },
    { axis: "alerts", label: "Alertas", keys: ["alerts"], fallbackScore: clamp(100 - numberOrZero(snapshot.alertCenter?.counts?.critical) * 22 - numberOrZero(snapshot.alertCenter?.counts?.high) * 12), reason: `${snapshot.alertCenter?.counts?.total ?? 0} alertas` },
    { axis: "inventory", label: "Inventario", keys: ["inventory"], fallbackScore: snapshot.inventory?.criticalCount === null || snapshot.inventory?.criticalCount === undefined ? null : clamp(100 - numberOrZero(snapshot.inventory?.criticalCount) * 22 - numberOrZero(snapshot.inventory?.reorderCount) * 9), reason: snapshot.inventory?.riskStatus },
    { axis: "uptime", label: "Uptime", keys: ["tablet", "pc", "control"], fallbackScore: snapshot.dataQuality?.sources?.length ? clamp((snapshot.dataQuality.sources.filter((item) => item.status === "ok").length / snapshot.dataQuality.sources.length) * 100) : null, reason: "source uptime" },
    { axis: "cashflow", label: "Caja", keys: ["cash"], fallbackScore: snapshot.money?.varianceCents === null || snapshot.money?.varianceCents === undefined ? null : clamp(100 - Math.abs(snapshot.money.varianceCents) / 350), reason: snapshot.money?.varianceStatus }
  ];
  return definitions.map((definition) => {
    const dimension = findDimension(source, definition.keys);
    const value = dimension?.score ?? definition.fallbackScore ?? 0;
    const staleMinutes = Math.round((snapshot.dataQuality?.freshnessSeconds ?? 0) / 60);
    return {
      axis: definition.axis,
      label: definition.label,
      value: clamp(value),
      status: operationalStatusFromMobile(dimension?.status, dimension?.score ?? definition.fallbackScore),
      confidence: clamp((dimension?.confidence ?? snapshot.dataQuality?.confidence ?? 0.4) * 100),
      staleMinutes: Number.isFinite(staleMinutes) ? staleMinutes : minutesAgo(snapshot.meta?.generatedAt, generatedAt),
      topReason: dimension?.explanation ?? definition.reason ?? "snapshot partial"
    };
  });
}

export function buildMobileFreshnessRingsViewModel(source?: PrismaMobileChartSource, options?: PrismaChartAdapterOptions): FreshnessBeacon[] {
  const snapshot = source?.snapshot;
  if (!snapshot) return mockFallback(mockMobileCharts.freshnessBeaconGrid, options);
  const generatedAt = sourceTime(snapshot.meta?.generatedAt, snapshot.dataQuality?.generatedAt, source?.generatedAt);
  const sources = snapshot.dataQuality?.sources ?? [];
  if (!sources.length) return mockFallback(mockMobileCharts.freshnessBeaconGrid, options);
  return sources.map((item) => {
    const staleMinutes = item.freshnessSeconds === null ? minutesAgo(item.lastSeenAt, generatedAt) : Math.round(item.freshnessSeconds / 60);
    const freshnessState: FreshnessBeacon["freshnessState"] = item.status === "ok" && staleMinutes <= 15 ? "fresh" : item.status === "ok" ? "aging" : item.status === "stale" ? "stale" : item.status === "offline" ? "offline" : "unknown";
    return {
      moduleId: item.id,
      moduleName: item.label,
      lastUpdatedAt: item.lastSeenAt ?? generatedAt,
      staleMinutes,
      ttlMinutes: 15,
      freshnessState,
      confidence: clamp((snapshot.dataQuality?.confidence ?? 0.4) * 100),
      source: item.id === "pc" ? "server" : item.id === "tablet" ? "local" : item.id === "control" ? "public_sanitized" : "cache"
    };
  });
}

function priorityLabel(priority: number): ActionPriorityStackDatum["priority"] {
  if (priority <= 1) return "critical";
  if (priority === 2) return "high";
  if (priority === 3) return "medium";
  return "low";
}

export function buildMobileActionInboxPriorityStackViewModel(source?: PrismaMobileChartSource, options?: PrismaChartAdapterOptions): ActionPriorityStackDatum[] {
  const items = source?.snapshot?.actionInbox?.items ?? [];
  if (!items.length) return mockFallback(mockMobileCharts.actionInboxPriorityStack, options);
  const grouped = new Map<string, ActionPriorityStackDatum>();
  const now = Date.parse(sourceTime(source?.snapshot?.meta?.generatedAt, source?.snapshot?.dataQuality?.generatedAt, source?.generatedAt));
  for (const item of items) {
    const priority = priorityLabel(item.priority);
    const key = `${item.ownerRole}:${priority}`;
    const dueTime = item.dueAt ? Date.parse(item.dueAt) : null;
    const current = grouped.get(key) ?? {
      responsibleName: item.ownerRole,
      role: item.ownerRole,
      moduleId: item.ownerRole.toLowerCase().replace(/\s+/g, "-"),
      priority,
      openCount: 0,
      overdueCount: 0,
      blockedCount: 0,
      dueSoonCount: 0,
      evidenceMissingCount: 0
    };
    current.openCount += 1;
    if (dueTime !== null && Number.isFinite(dueTime) && dueTime < now) current.overdueCount += 1;
    if (item.priority <= 1) current.blockedCount += 1;
    if (dueTime !== null && Number.isFinite(dueTime) && dueTime >= now && dueTime - now <= 3 * 60 * 60_000) current.dueSoonCount += 1;
    if (!item.evidence?.length) current.evidenceMissingCount += 1;
    grouped.set(key, current);
  }
  return Array.from(grouped.values()).sort((a, b) => b.openCount - a.openCount).slice(0, 8);
}

export function buildMobileOwnerPulseTimelineViewModel(source?: PrismaMobileChartSource, options?: PrismaChartAdapterOptions): OwnerPulsePoint[] {
  const snapshot = source?.snapshot;
  if (!snapshot) return mockFallback(mockMobileCharts.ownerPulseTimeline, options);
  const generatedAt = sourceTime(snapshot.meta?.generatedAt, snapshot.dataQuality?.generatedAt, source?.generatedAt);
  const timeline = snapshot.timeline ?? [];
  const baseScore = snapshot.healthRadar?.globalScore ?? clamp((snapshot.dataQuality?.confidence ?? 0.4) * 100);
  if (!timeline.length) {
    return [{
      time: generatedAt,
      healthScore: baseScore,
      status: operationalStatusFromMobile(snapshot.healthRadar?.status, baseScore),
      activeIncidentCount: snapshot.alertCenter?.counts?.total ?? 0,
      openActionCount: snapshot.actionInbox?.items?.length ?? 0,
      dataConfidence: clamp((snapshot.dataQuality?.confidence ?? 0.4) * 100),
      freshnessMinutes: Math.round((snapshot.dataQuality?.freshnessSeconds ?? 0) / 60),
      annotation: snapshot.meta?.runtimeMode
    }];
  }
  return timeline.slice(-8).map((event, index) => ({
    time: event.occurredAt,
    healthScore: clamp(baseScore - (timeline.length - index - 1) * 2),
    status: operationalStatusFromMobile(event.severity, baseScore),
    activeIncidentCount: snapshot.alertCenter?.counts?.total ?? 0,
    openActionCount: snapshot.actionInbox?.items?.length ?? 0,
    dataConfidence: clamp((snapshot.dataQuality?.confidence ?? 0.4) * 100),
    freshnessMinutes: minutesAgo(event.occurredAt, generatedAt),
    annotation: event.title
  }));
}

export function buildMobileIncidentSparkCardsViewModel(source?: PrismaMobileChartSource, options?: PrismaChartAdapterOptions): IncidentSparkCard[] {
  const snapshot = source?.snapshot;
  if (!snapshot) return mockFallback(mockMobileCharts.incidentSparkCards, options);
  const alerts = snapshot.alertCenter?.alerts ?? [];
  const generatedAt = sourceTime(snapshot.meta?.generatedAt, snapshot.dataQuality?.generatedAt, source?.generatedAt);
  if (!alerts.length) return mockFallback(mockMobileCharts.incidentSparkCards, options);
  return alerts.slice(0, 4).map((alert) => {
    const lastSeen = alert.lastSeenAt ?? generatedAt;
    const severity = lower(alert.severity) === "critical" ? "CRITICAL" : lower(alert.severity) === "high" ? "ERROR" : lower(alert.severity) === "medium" ? "WARN" : "INFO";
    const impact = clamp(alert.priorityScore ?? (severity === "CRITICAL" ? 90 : severity === "ERROR" ? 74 : severity === "WARN" ? 52 : 24));
    return {
      incidentId: alert.id,
      title: alert.title,
      severity,
      state: lower(alert.status) === "resolved" ? "resolved" : "active",
      moduleId: lower(alert.category || alert.source || "mobile"),
      points: [2, 1, 0].map((offset) => ({
        time: new Date(Date.parse(lastSeen) - offset * 20 * 60_000).toISOString(),
        impactScore: clamp(impact - offset * 4),
        healthScore: snapshot.healthRadar?.globalScore ?? undefined
      })),
      recommendedNextAction: alert.recommendedAction ?? "Revisar evidencia",
      owner: alert.source,
      evidenceCount: alert.evidence?.length ?? 0
    };
  });
}

export function buildMobileConfidenceMeterBandsViewModel(source?: PrismaMobileChartSource, options?: PrismaChartAdapterOptions): ConfidenceBand[] {
  const snapshot = source?.snapshot;
  if (!snapshot) return mockFallback(mockMobileCharts.confidenceMeterBands, options);
  const report = snapshot.dataQuality;
  const sources = report?.sources ?? [];
  const totalSources = Math.max(1, sources.length);
  const okSources = sources.filter((item) => item.status === "ok").length;
  const evidenceCount = (snapshot.alertCenter?.alerts ?? []).reduce((sum, alert) => sum + (alert.evidence?.length ?? 0), 0);
  const completeness = clamp((report?.completeness ?? 0) * 100);
  const recency = report?.freshnessSeconds === null || report?.freshnessSeconds === undefined ? 0 : clamp(100 - report.freshnessSeconds / 18);
  const consistency = clamp(100 - numberOrZero(snapshot.sync?.failedCount) * 18 - (report?.staleSources?.length ?? 0) * 10);
  const evidenceValue = clamp(Math.min(100, evidenceCount * 20));
  const coverage = clamp((okSources / totalSources) * 100);
  const stateFor = (value: number): ConfidenceBand["state"] => value >= 80 ? "high" : value >= 55 ? "medium" : "low";
  return [
    { dimension: "completeness", label: "Completitud", value: completeness, state: stateFor(completeness), reason: "Medida por DataQualityReport.", affectedModules: report?.missingSources ?? [] },
    { dimension: "recency", label: "Recencia", value: recency, state: stateFor(recency), reason: "Derivada de freshnessSeconds.", affectedModules: report?.staleSources ?? [] },
    { dimension: "consistency", label: "Consistencia", value: consistency, state: stateFor(consistency), reason: "Penaliza fallos de sync y fuentes stale.", affectedModules: ["sync", ...(report?.staleSources ?? [])] },
    { dimension: "evidence", label: "Evidencia", value: evidenceValue, state: stateFor(evidenceValue), reason: "Proxy por evidencia asociada a alertas.", affectedModules: ["alerts", "actions"] },
    { dimension: "coverage", label: "Cobertura", value: coverage, state: stateFor(coverage), reason: "Fuentes OK contra fuentes esperadas.", affectedModules: sources.filter((item) => item.status !== "ok").map((item) => item.id) }
  ];
}

function buildMobileCharts(source?: PrismaMobileChartSource, options?: PrismaChartAdapterOptions): SourceResult<PrismaMobileChartsViewModel> {
  const quality = buildMobileQuality(source, options);
  return {
    quality,
    data: {
      ownerPulseTimeline: buildMobileOwnerPulseTimelineViewModel(source, options),
      actionInboxPriorityStack: buildMobileActionInboxPriorityStackViewModel(source, options),
      healthRadarCompact: buildMobileHealthRadarCompactViewModel(source, options),
      freshnessBeaconGrid: buildMobileFreshnessRingsViewModel(source, options),
      incidentSparkCards: buildMobileIncidentSparkCardsViewModel(source, options),
      confidenceMeterBands: buildMobileConfidenceMeterBandsViewModel(source, options)
    }
  };
}

export function buildPrismaTripleAppChartsViewModel(sources: PrismaChartAdapterSources = {}): PrismaTripleAppChartsViewModel {
  const options: PrismaChartAdapterOptions = { mockFallback: sources.mockFallback };
  const pc = buildPcCharts(sources.pc, options);
  const tablet = buildTabletCharts(sources.tablet, options);
  const mobile = buildMobileCharts(sources.mobile, options);
  return {
    schemaVersion: "1.0",
    generatedAt: sourceTime(pc.quality.freshness.generatedAt, tablet.quality.freshness.generatedAt, mobile.quality.freshness.generatedAt),
    pc: pc.data,
    tablet: tablet.data,
    mobile: mobile.data,
    quality: {
      pc: pc.quality,
      tablet: tablet.quality,
      mobile: mobile.quality
    }
  };
}

export function buildPrismaInsightEnvelope<T>(
  surface: PrismaChartSurface,
  data: T,
  filtersApplied: PrismaInsightEnvelope<T>["filtersApplied"] = {},
  quality?: PrismaChartQuality
): PrismaInsightEnvelope<T> {
  const fallbackQuality = surface === "pc"
    ? buildPcQuality(undefined, undefined)
    : surface === "tablet"
      ? buildTabletQuality(undefined, undefined)
      : buildMobileQuality(undefined, undefined);
  const resolvedQuality = quality ?? fallbackQuality;
  return {
    schemaVersion: "1.0",
    generatedAt: resolvedQuality.freshness.generatedAt,
    surface,
    freshness: resolvedQuality.freshness,
    confidence: resolvedQuality.confidence,
    filtersApplied,
    data,
    quality: resolvedQuality
  };
}
