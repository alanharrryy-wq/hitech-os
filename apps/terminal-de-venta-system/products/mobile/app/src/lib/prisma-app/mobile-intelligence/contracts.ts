import { z } from "zod";

export const PRISMA_MOBILE_INTELLIGENCE_CONTRACT_ID = "PRISMA_MOBILE_INTELLIGENCE_LAYER_40";

export const MobileRuntimeModeSchema = z.enum(["live", "partial", "offline", "stale", "unknown", "demo-disabled"]);
export const OperationalValueStatusSchema = z.enum(["ok", "null", "unknown", "unavailable", "partial", "stale", "offline"]);
export const SourceStatusSchema = z.enum(["ok", "stale", "offline", "error", "unknown"]);
export const EvidenceSensitivitySchema = z.enum(["public", "safe", "redacted"]);
export const AlertSeveritySchema = z.enum(["critical", "high", "medium", "low", "info"]);
export const AlertStatusSchema = z.enum(["new", "seen", "acknowledged", "in_progress", "resolved", "dismissed", "snoozed"]);
export const AlertCategorySchema = z.enum(["MONEY", "SALES", "INVENTORY", "SYNC", "DEVICE", "HEALTH", "SECURITY", "AUDIT", "REPORT"]);
export const ChartRangeSchema = z.enum(["today", "yesterday", "seven-days", "thirty-days"]);
export const ChartUnitSchema = z.enum(["currency", "count", "percent", "milliseconds", "minutes"]);

export const PrismaMobileApiResponseMetaSchema = z.object({
  generatedAt: z.string().datetime(),
  runtimeMode: MobileRuntimeModeSchema.optional(),
  confidence: z.number().min(0).max(1).optional(),
  freshnessSeconds: z.number().int().nonnegative().nullable().optional()
});

export const PrismaMobileApiErrorSchema = z.object({
  code: z.string().min(1),
  message: z.string().min(1),
  details: z.unknown().optional()
});

export const PrismaMobileApiResponseSchema = z.object({
  ok: z.boolean(),
  data: z.unknown().optional(),
  error: PrismaMobileApiErrorSchema.optional(),
  meta: PrismaMobileApiResponseMetaSchema.optional()
});

export const EvidenceLinkSchema = z.object({
  id: z.string().min(1),
  label: z.string().min(1),
  source: z.string().min(1),
  summary: z.string().min(1),
  sensitivity: EvidenceSensitivitySchema.default("safe"),
  href: z.string().optional()
});

export const SourceQualitySchema = z.object({
  id: z.string().min(1),
  label: z.string().min(1),
  status: SourceStatusSchema,
  lastSeenAt: z.string().datetime().nullable(),
  freshnessSeconds: z.number().int().nonnegative().nullable(),
  latencyMs: z.number().int().nonnegative().nullable(),
  errorCount: z.number().int().nonnegative(),
  lastError: z.string().nullable(),
  warnings: z.array(z.string())
});

export const DataQualityReportSchema = z.object({
  runtimeMode: MobileRuntimeModeSchema,
  confidence: z.number().min(0).max(1),
  completeness: z.number().min(0).max(1),
  generatedAt: z.string().datetime(),
  freshnessSeconds: z.number().int().nonnegative().nullable(),
  missingSources: z.array(z.string()),
  staleSources: z.array(z.string()),
  warnings: z.array(z.string()),
  sources: z.array(SourceQualitySchema)
});

export const MobileSnapshotMetaV2Schema = z.object({
  contractId: z.literal(PRISMA_MOBILE_INTELLIGENCE_CONTRACT_ID),
  generatedAt: z.string().datetime(),
  runtimeMode: MobileRuntimeModeSchema,
  confidence: z.number().min(0).max(1),
  freshnessSeconds: z.number().int().nonnegative().nullable()
});

export const NullableMetricSchema = z.object({
  value: z.number().nullable(),
  label: z.string().min(1),
  status: OperationalValueStatusSchema,
  source: z.string().min(1),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export const TodaySummarySchema = z.object({
  businessName: z.string().min(1),
  generatedAt: z.string().datetime(),
  openingLine: z.string().min(1),
  healthLabel: z.string().min(1),
  recommendedAction: z.string().min(1),
  status: OperationalValueStatusSchema
});

export const MoneySummarySchema = z.object({
  expectedCashCents: z.number().nullable(),
  countedCashCents: z.number().nullable(),
  varianceCents: z.number().nullable(),
  varianceStatus: OperationalValueStatusSchema,
  label: z.string().min(1),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export const SalesIntelligenceSchema = z.object({
  totalSalesCents: z.number().nullable(),
  tickets: z.number().nullable(),
  averageTicketCents: z.number().nullable(),
  paceStatus: OperationalValueStatusSchema,
  summary: z.string().min(1),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export const InventoryIntelligenceSchema = z.object({
  criticalCount: z.number().int().nonnegative().nullable(),
  reorderCount: z.number().int().nonnegative().nullable(),
  topRiskSku: z.string().nullable(),
  riskStatus: OperationalValueStatusSchema,
  summary: z.string().min(1),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export const MobileAlertSchema = z.object({
  id: z.string().min(1),
  dedupeKey: z.string().min(1),
  category: AlertCategorySchema,
  severity: AlertSeveritySchema,
  status: AlertStatusSchema,
  title: z.string().min(1),
  summary: z.string().min(1),
  whyItMatters: z.string().min(1),
  recommendedAction: z.string().min(1),
  source: z.string().min(1),
  sourceRef: z.string().min(1),
  confidence: z.number().min(0).max(1),
  priorityScore: z.number().int().nonnegative(),
  evidence: z.array(EvidenceLinkSchema).default([]),
  lastSeenAt: z.string().datetime()
});

export const AlertCenterSchema = z.object({
  alerts: z.array(MobileAlertSchema),
  counts: z.object({
    total: z.number().int().nonnegative(),
    critical: z.number().int().nonnegative(),
    high: z.number().int().nonnegative(),
    medium: z.number().int().nonnegative(),
    low: z.number().int().nonnegative(),
    info: z.number().int().nonnegative()
  }),
  primaryRecommendedAction: z.string().min(1)
});

export const ActionItemSchema = z.object({
  id: z.string().min(1),
  alertId: z.string().min(1).optional(),
  title: z.string().min(1),
  reason: z.string().min(1),
  impact: z.string().min(1),
  recommendedAction: z.string().min(1),
  ownerRole: z.string().min(1),
  priority: z.number().int().min(1).max(5),
  priorityScore: z.number().int().nonnegative(),
  dueAt: z.string().datetime().nullable(),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export const ActionInboxSchema = z.object({
  items: z.array(ActionItemSchema),
  primaryAction: ActionItemSchema.nullable()
});

export const TimelineEventSchema = z.object({
  id: z.string().min(1),
  type: z.string().min(1),
  occurredAt: z.string().datetime(),
  title: z.string().min(1),
  detail: z.string().min(1),
  whyItMatters: z.string().min(1),
  recommendedAction: z.string().min(1),
  severity: AlertSeveritySchema,
  source: z.string().min(1),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export const HealthRadarDimensionSchema = z.object({
  key: z.string().min(1),
  label: z.string().min(1),
  score: z.number().int().min(0).max(100).nullable(),
  status: z.enum(["healthy", "watch", "degraded", "blocked", "unknown"]),
  confidence: z.number().min(0).max(1),
  explanation: z.string().min(1),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export const HealthRadarSchema = z.object({
  globalScore: z.number().int().min(0).max(100).nullable(),
  status: z.enum(["healthy", "watch", "degraded", "blocked", "unknown"]),
  confidence: z.number().min(0).max(1),
  dimensions: z.array(HealthRadarDimensionSchema)
});

export const SyncStatusSchema = z.object({
  status: z.enum(["ok", "delayed", "blocked", "offline", "unknown"]),
  pendingCount: z.number().int().nonnegative().nullable(),
  failedCount: z.number().int().nonnegative().nullable(),
  oldestPendingAt: z.string().datetime().nullable(),
  freshnessSeconds: z.number().int().nonnegative().nullable(),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export const ReportSummarySchema = z.object({
  dailyStatus: OperationalValueStatusSchema,
  generatedAt: z.string().datetime(),
  highlights: z.array(z.string()),
  risks: z.array(z.string()),
  opportunities: z.array(z.string()),
  recommendedActions: z.array(z.string()),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export const ChartPointSchema = z.object({
  x: z.string().min(1),
  y: z.number().nullable(),
  label: z.string().min(1),
  status: OperationalValueStatusSchema.default("ok"),
  meta: z.record(z.union([z.string(), z.number(), z.boolean(), z.null()])).default({})
});

export const ChartViewModelSchema = z.object({
  chartKey: z.string().min(1),
  title: z.string().min(1),
  rangeKey: ChartRangeSchema,
  points: z.array(ChartPointSchema),
  unit: ChartUnitSchema,
  summary: z.string().min(1),
  emptyState: z.string().optional(),
  source: z.string().optional(),
  confidence: z.number().min(0).max(1).optional(),
  evidence: z.array(EvidenceLinkSchema).default([])
});

export type MobileRuntimeMode = z.infer<typeof MobileRuntimeModeSchema>;
export type PrismaMobileApiResponseMeta = z.infer<typeof PrismaMobileApiResponseMetaSchema>;
export type PrismaMobileApiError = z.infer<typeof PrismaMobileApiErrorSchema>;
export type PrismaMobileApiResponse<T = unknown> = Omit<z.infer<typeof PrismaMobileApiResponseSchema>, "data"> & { data?: T };
export type OperationalValueStatus = z.infer<typeof OperationalValueStatusSchema>;
export type EvidenceLink = z.infer<typeof EvidenceLinkSchema>;
export type SourceQuality = z.infer<typeof SourceQualitySchema>;
export type DataQualityReport = z.infer<typeof DataQualityReportSchema>;
export type MobileSnapshotMetaV2 = z.infer<typeof MobileSnapshotMetaV2Schema>;
export type TodaySummary = z.infer<typeof TodaySummarySchema>;
export type MoneySummary = z.infer<typeof MoneySummarySchema>;
export type SalesIntelligence = z.infer<typeof SalesIntelligenceSchema>;
export type InventoryIntelligence = z.infer<typeof InventoryIntelligenceSchema>;
export type MobileAlert = z.infer<typeof MobileAlertSchema>;
export type AlertCenter = z.infer<typeof AlertCenterSchema>;
export type ActionItem = z.infer<typeof ActionItemSchema>;
export type ActionInbox = z.infer<typeof ActionInboxSchema>;
export type TimelineEvent = z.infer<typeof TimelineEventSchema>;
export type HealthRadarDimension = z.infer<typeof HealthRadarDimensionSchema>;
export type HealthRadar = z.infer<typeof HealthRadarSchema>;
export type SyncStatus = z.infer<typeof SyncStatusSchema>;
export type ReportSummary = z.infer<typeof ReportSummarySchema>;
export type ChartPoint = z.infer<typeof ChartPointSchema>;
export type ChartViewModel = z.infer<typeof ChartViewModelSchema>;

export const PrismaMobileIntelligenceSnapshotSchema = z.object({
  meta: MobileSnapshotMetaV2Schema,
  today: TodaySummarySchema,
  money: MoneySummarySchema,
  sales: SalesIntelligenceSchema,
  inventory: InventoryIntelligenceSchema,
  alertCenter: AlertCenterSchema,
  actionInbox: ActionInboxSchema,
  timeline: z.array(TimelineEventSchema),
  healthRadar: HealthRadarSchema,
  sync: SyncStatusSchema,
  reports: ReportSummarySchema,
  dataQuality: DataQualityReportSchema,
  chartViewModels: z.array(ChartViewModelSchema)
});

export type PrismaMobileIntelligenceSnapshot = z.infer<typeof PrismaMobileIntelligenceSnapshotSchema>;
