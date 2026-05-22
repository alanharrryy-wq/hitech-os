
/*
 * PRISMA Chart Runtime Plug Readiness V1
 *
 * This module accepts optional runtime chart payloads already shaped as shared chart view models.
 * It does not fetch, persist, write to browser storage, touch DBs, or claim live readiness.
 * If a runtime payload is absent, each adapter keeps its existing derived adapter path or deterministic mock fallback.
 *
 * Safe producer shape example:
 * buildPrismaTripleAppChartsViewModel({
 *   pc: { runtime: { generatedAt, financialOperationalWaterfall: [...] } },
 *   tablet: { runtime: { generatedAt, shiftPulseBuckets: [...], syncOutboxStatusMatrix: [...] } },
 *   mobile: { snapshot: { meta: { generatedAt, runtimeMode: "runtime" }, ownerPulseTimeline: [...] } }
 * })
 */

export type PrismaChartSurface = "pc" | "tablet" | "mobile";
export type PrismaChartRenderer = "canvas" | "svg";
export type PrismaSeverity = "INFO" | "WARN" | "ERROR" | "CRITICAL";
export type PrismaOperationalStatus = "PASS" | "DEGRADED" | "FAIL" | "UNKNOWN";
export type PrismaConfidenceLevel = "high" | "medium" | "low";
export type PrismaChartDataSource = "mock" | "adapter" | "api" | "local" | "server" | "public_sanitized" | "cache";
export type PrismaChartDataStatus = "real" | "partial" | "mock" | "unavailable";

export type PrismaChartMockFallbackPolicy = {
  useMockFallback?: boolean;
  reason?: string;
};

export type PrismaChartFreshness = {
  generatedAt: string;
  maxStaleMinutes: number;
  staleSources: string[];
};

export type PrismaChartConfidence = {
  score: number;
  level: PrismaConfidenceLevel;
  reasons: string[];
};

export type PrismaChartQuality = {
  source: PrismaChartDataSource;
  dataStatus: PrismaChartDataStatus;
  sourceLabel: string;
  freshness: PrismaChartFreshness;
  confidence: PrismaChartConfidence;
  emptyState: string;
  fallbackReason?: string;
  todo?: string;
};

export type PrismaChartFilter = {
  id: string;
  label: string;
  values: string[];
};

export type PrismaChartInteraction = {
  event: "hover" | "click" | "tap" | "brush" | "legend" | "reset" | "swipe" | "long_press";
  label: string;
  safe: boolean;
};

export type PrismaChartDefinition = {
  id: PrismaChartId;
  surface: PrismaChartSurface;
  title: string;
  componentName: string;
  renderer: PrismaChartRenderer;
  echartsSeries: string[];
  purpose: string;
  visualEncoding: string;
  filters: PrismaChartFilter[];
  interactions: PrismaChartInteraction[];
  accessibility: string;
  responsive: string;
  dataContract: string;
  route: string;
};

export type PrismaChartFlags = {
  enabled: boolean;
  masterEnabled: boolean;
  surfaceEnabled: boolean;
  previewEnabled: boolean;
  useMockFallback: boolean;
  reason: string;
};

export type PrismaInsightEnvelope<T> = {
  schemaVersion: "1.0";
  generatedAt: string;
  surface: PrismaChartSurface;
  freshness: PrismaChartFreshness;
  confidence: PrismaChartConfidence;
  filtersApplied: Record<string, string | number | boolean | null>;
  data: T;
  quality: PrismaChartQuality;
};

export type CausalFlowRibbonDatum = {
  sourceModule: string;
  causeType: string;
  effectType: string;
  actionTarget: string;
  weight: number;
  severity: PrismaSeverity;
  confidence: number;
  evidenceCount: number;
  incidentIds: string[];
  firstSeenAt: string;
  lastSeenAt: string;
  ownerRole?: string;
};

export type OperationalDensityCell = {
  bucketStart: string;
  bucketEnd: string;
  moduleId: string;
  moduleName: string;
  eventCount: number;
  warnCount: number;
  errorCount: number;
  avgLatencyMs?: number;
  staleMinutesAvg?: number;
  retryCount?: number;
  pressureScore: number;
  dominantCause?: string;
  confidence: number;
  /** Optional display label used by premium lab heatmaps to preserve exact bucket copy independent of browser timezone. */
  bucketLabel?: string;
  /** Visual state for matrix cells; does not alter canonical event semantics. */
  state?: "normal" | "peak" | "anomaly" | "cold" | "gap";
  /** Human-readable anomaly/callout label for hover and premium overlays. */
  anomalyLabel?: string;
  /** Safe next-action hint shown in lab tooltip only. */
  actionHint?: string;
  /** Public-safe evidence pointer, not a secret log path. */
  evidenceRef?: string;
};

export type ServiceDependencyNode = {
  id: string;
  label: string;
  kind: "app" | "service" | "endpoint" | "cloudflare" | "db" | "worker";
  status: PrismaOperationalStatus;
  port?: number;
  localUrl?: string;
  publicUrl?: string;
  latencyMs?: number;
  healthy: boolean;
  criticality: "low" | "medium" | "high";
  owner?: string;
  lastProbeAt?: string;
};

export type ServiceDependencyEdge = {
  source: string;
  target: string;
  relation: "routes_to" | "depends_on" | "probes" | "syncs_with" | "writes_to";
  status: PrismaOperationalStatus;
  latencyMs?: number;
  evidence?: string;
};

export type InventoryRiskNode = {
  id: string;
  parentId?: string;
  label: string;
  level: "category" | "subcategory" | "sku" | "supplier" | "warehouse";
  stockOnHand: number;
  reorderPoint: number;
  daysOfCover: number;
  velocityPerDay: number;
  stockoutRisk: number;
  overstockRisk: number;
  shrinkRisk?: number;
  marginImpact?: number;
  revenueAtRisk?: number;
  supplierId?: string;
  lastMovementAt?: string;
  confidence: number;
};

export type DecisionLedgerPoint = {
  decisionId: string;
  time: string;
  title: string;
  type: "decision" | "action" | "evidence" | "incident" | "resolution";
  actorId?: string;
  actorName?: string;
  responsibleRole?: string;
  status: "open" | "in_progress" | "resolved" | "blocked" | "expired";
  relatedIncidentIds: string[];
  evidenceCount: number;
  impactScore: number;
  beforeHealthScore?: number;
  afterHealthScore?: number;
  confidence: number;
};

export type OperationalWaterfallStep = {
  id: string;
  label: string;
  kind: "positive" | "negative" | "subtotal" | "neutral";
  value: number;
  currency: string;
  source: "sales" | "refunds" | "discounts" | "inventory" | "incidents" | "costs";
  relatedIds: string[];
  confidence: number;
};

export type TabletCatalogEntityName =
  | "Product"
  | "Brand"
  | "Supplier"
  | "ProductSupplier"
  | "PriceList"
  | "PriceListItem"
  | "TaxRate"
  | "DropdownCatalog"
  | "DropdownOption";

export type TabletCatalogFreshnessStatus = "fresh" | "warning" | "stale" | "unknown" | "error";
export type TabletCatalogRecommendedAction = "none" | "pull_delta" | "bootstrap" | "resync" | "investigate";

export type TabletCatalogEntityFreshness = {
  entityType: TabletCatalogEntityName;
  status: TabletCatalogFreshnessStatus;
  pcRowCount: number;
  exportedCount: number;
  appliedCount: number;
  rejectedCount: number;
  conflictedCount: number;
  duplicatedCount: number;
  lastCursor?: string | null;
  note?: string;
};

export type TabletCatalogFreshnessGridRow = {
  terminalId: string;
  terminalLabel: string;
  storeId?: string | null;
  stream: string;
  lastSuccessfulPullAt: string | null;
  lastAttemptedPullAt: string | null;
  checkpointCursor: string | null;
  checkpointSummary: string;
  freshnessStatus: TabletCatalogFreshnessStatus;
  entityStatuses: TabletCatalogEntityFreshness[];
  counts: {
    applied: number;
    rejected: number;
    conflicted: number;
    duplicated: number;
    pending: number;
    behind: number;
  };
  recommendedAction: TabletCatalogRecommendedAction;
  lastErrorSummary?: string | null;
  evidenceRefs: string[];
};

export type PcSyncCommandType = "catalog_delta" | "bootstrap" | "resync" | "runtime_refresh";
export type PcSyncLifecycleStatus =
  | "created"
  | "queued"
  | "exported"
  | "available"
  | "pulled"
  | "applying"
  | "applied"
  | "rejected"
  | "conflicted"
  | "duplicated"
  | "expired"
  | "failed"
  | "unknown";

export type SyncCommandLifecycleEvent = {
  commandId: string;
  terminalId?: string | null;
  terminalLabel?: string | null;
  commandType: PcSyncCommandType;
  status: PcSyncLifecycleStatus;
  timestamp: string;
  elapsedMs?: number | null;
  actor?: string | null;
  source: "pc.audit_event" | "pc.outbox_event" | "pc.sync_attempt" | "pc.sync_conflict" | "pc.sync_checkpoint";
  stream: string;
  entityCounts: Partial<Record<TabletCatalogEntityName, number>>;
  resultCounts: {
    applied: number;
    rejected: number;
    conflicted: number;
    duplicated: number;
  };
  reason?: string | null;
  recommendedAction: TabletCatalogRecommendedAction;
  evidenceRef: string;
};

export type ShiftPulseBucket = {
  bucketStart: string;
  bucketEnd: string;
  shiftId: string;
  terminalId: string;
  cashierId?: string;
  saleCount: number;
  grossSales: number;
  refundCount: number;
  cancellationCount: number;
  avgTicket: number;
  offlineSaleCount: number;
  pendingSyncCount: number;
  queuePressure: number;
  status: "normal" | "busy" | "risk" | "blocked";
};

export type SyncOutboxMatrixCell = {
  itemType: "event" | "sale" | "refund" | "inventory_adjustment" | "cash_shift" | "ticket" | "customer";
  syncState: "pending" | "sending" | "sent" | "failed" | "retrying";
  count: number;
  oldestAgeMinutes: number;
  lastAttemptAt?: string;
  retryCount: number;
  blocking: boolean;
  confidence: number;
};

export type OwnerPulsePoint = {
  time: string;
  healthScore: number;
  status: PrismaOperationalStatus;
  activeIncidentCount: number;
  openActionCount: number;
  dataConfidence: number;
  freshnessMinutes: number;
  annotation?: string;
};

export type ActionPriorityStackDatum = {
  responsibleId?: string;
  responsibleName: string;
  role: string;
  moduleId: string;
  priority: "low" | "medium" | "high" | "critical";
  openCount: number;
  overdueCount: number;
  blockedCount: number;
  dueSoonCount: number;
  evidenceMissingCount: number;
};

export type HealthRadarAxis = {
  axis: "data_quality" | "sync" | "alerts" | "inventory" | "uptime" | "cashflow";
  label: string;
  value: number;
  status: PrismaOperationalStatus;
  confidence: number;
  staleMinutes: number;
  topReason?: string;
};

export type FreshnessBeacon = {
  moduleId: string;
  moduleName: string;
  lastUpdatedAt: string;
  staleMinutes: number;
  ttlMinutes: number;
  freshnessState: "fresh" | "aging" | "stale" | "offline" | "unknown";
  confidence: number;
  source: "local" | "server" | "public_sanitized" | "cache" | "mock";
};

export type IncidentSparkCard = {
  incidentId: string;
  title: string;
  severity: PrismaSeverity;
  state: "active" | "resolved" | "recurring";
  moduleId: string;
  points: Array<{
    time: string;
    impactScore: number;
    healthScore?: number;
    retryCount?: number;
    latencyMs?: number;
  }>;
  recommendedNextAction: string;
  owner?: string;
  evidenceCount: number;
};

export type ConfidenceBand = {
  dimension: "completeness" | "recency" | "consistency" | "evidence" | "coverage";
  label: string;
  value: number;
  state: PrismaConfidenceLevel;
  reason: string;
  affectedModules: string[];
};

export type PrismaPcChartsViewModel = {
  causalFlowRibbon: CausalFlowRibbonDatum[];
  operationalDensityField: OperationalDensityCell[];
  operationalDensityHeatmap: OperationalDensityCell[];
  serviceDependencyGraph: {
    nodes: ServiceDependencyNode[];
    edges: ServiceDependencyEdge[];
  };
  inventoryRiskTreemap: InventoryRiskNode[];
  decisionLedgerTimeline: DecisionLedgerPoint[];
  financialOperationalWaterfall: OperationalWaterfallStep[];
  tabletCatalogFreshnessGrid: TabletCatalogFreshnessGridRow[];
  syncCommandLifecycleTimeline: SyncCommandLifecycleEvent[];
};

export type PrismaTabletChartsViewModel = {
  shiftPulseStrip: ShiftPulseBucket[];
  syncOutboxStatusMatrix: SyncOutboxMatrixCell[];
};

export type PrismaMobileChartsViewModel = {
  ownerPulseTimeline: OwnerPulsePoint[];
  actionInboxPriorityStack: ActionPriorityStackDatum[];
  healthRadarCompact: HealthRadarAxis[];
  freshnessBeaconGrid: FreshnessBeacon[];
  incidentSparkCards: IncidentSparkCard[];
  confidenceMeterBands: ConfidenceBand[];
};

export type PrismaTripleAppChartsViewModel = {
  schemaVersion: "1.0";
  generatedAt: string;
  pc: PrismaPcChartsViewModel;
  tablet: PrismaTabletChartsViewModel;
  mobile: PrismaMobileChartsViewModel;
  quality: Record<PrismaChartSurface, PrismaChartQuality>;
};

export type PrismaPcChartSource = {
  generatedAt?: string;
  runtime?: {
    generatedAt?: string;
    sourceLabel?: string;
    evidence?: string[];
    warnings?: string[];
    causalFlowRibbon?: CausalFlowRibbonDatum[];
    operationalDensityField?: OperationalDensityCell[];
    operationalDensityHeatmap?: OperationalDensityCell[];
    serviceDependencyGraph?: { nodes?: ServiceDependencyNode[]; edges?: ServiceDependencyEdge[] };
    inventoryRiskTreemap?: InventoryRiskNode[];
    decisionLedgerTimeline?: DecisionLedgerPoint[];
    financialOperationalWaterfall?: OperationalWaterfallStep[];
    tabletCatalogFreshnessGrid?: TabletCatalogFreshnessGridRow[];
    syncCommandLifecycleTimeline?: SyncCommandLifecycleEvent[];
  } | null;
  catalogSync?: {
    generatedAt?: string;
    sourceLabel?: string;
    warnings?: string[];
    tabletCatalogFreshnessGrid?: TabletCatalogFreshnessGridRow[];
    syncCommandLifecycleTimeline?: SyncCommandLifecycleEvent[];
  } | null;
  dashboard?: {
    kpis?: Array<{ key: string; label: string; value: string; note?: string; status?: string; source?: string; tone?: string }>;
    topSkus?: Array<{ sku: string; productName: string; qty: number; totalCents: number }>;
    sync?: {
      pendingEvents?: number;
      failedEvents?: number;
      conflictCount?: number;
      lastIngestAt?: string | null;
      lastOutboxEventAt?: string | null;
      healthLabel?: string;
    };
    meta?: {
      source?: string;
      persistence?: string;
      hasConsolidatedEvents?: boolean;
      generatedAt?: string;
      warnings?: string[];
    };
  } | null;
  triDbStatus?: {
    status?: string;
    latestBridgeStatus?: string;
    bridgeTablesProjected?: number;
    bridgeRowsInsertedOrUpdated?: number;
    bridgeOutboxAcknowledged?: number;
    tablet?: { productCount?: number; saleCount?: number; outboxCount?: number; barcodeCount?: number; lowStockCount?: number; salesTotalCents?: number };
    pc?: { productCount?: number; saleCount?: number; outboxCount?: number; barcodeCount?: number; lowStockCount?: number; salesTotalCents?: number };
    parityOk?: boolean;
    parityTables?: Array<{ table: string; tabletRows: number; pcRows: number; pcCoversTablet: boolean; deltaPcMinusTablet: number }>;
    warnings?: string[];
    sourcePath?: string;
    mode?: string;
  } | null;
  errors?: string[];
};

export type PrismaTabletChartSource = {
  generatedAt?: string;
  runtime?: {
    generatedAt?: string;
    localSalesAllowed?: boolean;
    pcRequiredForBasicSale?: boolean;
    identity?: { businessId?: string; terminalId?: string; operatorName?: string };
    shift?: { state?: string; openedAt?: string | null; cashSessionId?: string | null };
    connection?: { state?: string; pendingEvents?: number; failedEvents?: number; conflictEvents?: number };
    catalog?: { activeProducts?: number; lowStockProducts?: number; inactiveProducts?: number; lastMovementAt?: string | null };
    sales?: { date?: string; ticketsClosed?: number; totalCents?: number; unitsSold?: number; averageTicketCents?: number };
    shiftPulseBuckets?: Array<{
      bucketStart: string;
      bucketEnd?: string;
      shiftId?: string;
      terminalId?: string;
      cashierId?: string;
      saleCount?: number;
      grossSales?: number;
      totalCents?: number;
      refundCount?: number;
      cancellationCount?: number;
      avgTicket?: number;
      averageTicketCents?: number;
      offlineSaleCount?: number;
      pendingSyncCount?: number;
      queuePressure?: number;
      status?: ShiftPulseBucket["status"];
    }>;
    syncOutboxStatusMatrix?: SyncOutboxMatrixCell[];
    warnings?: string[];
  } | null;
  syncPanel?: {
    summary?: { pending?: number; failed?: number; conflict?: number; total?: number };
    items?: Array<{ title?: string; description?: string; status?: string; attempts?: number; createdAt?: string; canRetry?: boolean }>;
  } | null;
  errors?: string[];
};

export type PrismaMobileChartSource = {
  generatedAt?: string;
  snapshot?: {
    meta?: { generatedAt?: string; runtimeMode?: string; confidence?: number; freshnessSeconds?: number | null };
    dataQuality?: {
      runtimeMode?: string;
      confidence?: number;
      completeness?: number;
      generatedAt?: string;
      freshnessSeconds?: number | null;
      missingSources?: string[];
      staleSources?: string[];
      warnings?: string[];
      sources?: Array<{ id: string; label: string; status: string; lastSeenAt: string | null; freshnessSeconds: number | null; latencyMs: number | null; errorCount: number; lastError: string | null; warnings: string[] }>;
    };
    healthRadar?: {
      globalScore?: number | null;
      status?: string;
      confidence?: number;
      dimensions?: Array<{ key: string; label: string; score: number | null; status: string; confidence: number; explanation: string; evidence?: unknown[] }>;
    };
    actionInbox?: {
      items?: Array<{ id: string; title: string; ownerRole: string; priority: number; priorityScore: number; dueAt: string | null; evidence?: unknown[] }>;
    };
    alertCenter?: {
      alerts?: Array<{ id: string; title: string; severity: string; status: string; category: string; source?: string; recommendedAction?: string; evidence?: unknown[]; lastSeenAt?: string; priorityScore?: number }>;
      counts?: { total: number; critical: number; high: number; medium: number; low: number; info: number };
    };
    timeline?: Array<{ id: string; occurredAt: string; title: string; severity: string; source: string; evidence?: unknown[] }>;
    sync?: { status?: string; pendingCount?: number | null; failedCount?: number | null; oldestPendingAt?: string | null; freshnessSeconds?: number | null };
    money?: { expectedCashCents?: number | null; countedCashCents?: number | null; varianceCents?: number | null; varianceStatus?: string };
    inventory?: { criticalCount?: number | null; reorderCount?: number | null; topRiskSku?: string | null; riskStatus?: string };
    chartViewModels?: Array<{ chartKey: string; points: Array<{ x: string; y: number | null; label: string; status?: string; meta?: Record<string, unknown> }>; confidence?: number; source?: string }>;
    ownerPulseTimeline?: OwnerPulsePoint[];
    actionInboxPriorityStack?: ActionPriorityStackDatum[];
    healthRadarCompact?: HealthRadarAxis[];
    freshnessBeaconGrid?: FreshnessBeacon[];
    incidentSparkCards?: IncidentSparkCard[];
    confidenceMeterBands?: ConfidenceBand[];
  } | null;
  errors?: string[];
};

export type PrismaChartAdapterSources = {
  pc?: PrismaPcChartSource;
  tablet?: PrismaTabletChartSource;
  mobile?: PrismaMobileChartSource;
  mockFallback?: PrismaChartMockFallbackPolicy;
};

export type PrismaChartId =
  | "pc.causal-flow-ribbon"
  | "pc.operational-density-field"
  | "ops.operational-density-heatmap"
  | "pc.service-dependency-graph"
  | "pc.inventory-risk-treemap"
  | "pc.decision-ledger-timeline"
  | "pc.financial-operational-waterfall"
  | "pc.tablet-catalog-freshness-grid"
  | "pc.sync-command-lifecycle-timeline"
  | "tablet.shift-pulse-strip"
  | "tablet.sync-outbox-status-matrix"
  | "mobile.owner-pulse-timeline"
  | "mobile.action-inbox-priority-stack"
  | "mobile.health-radar-compact"
  | "mobile.freshness-beacon-grid"
  | "mobile.incident-spark-cards"
  | "mobile.confidence-meter-bands";
