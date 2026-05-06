import { z } from "zod";

export const PRISMA_MOBILE_API_VERSION = "2026-05-02.mobile.17";
export const PRISMA_MOBILE_DATA_SOURCE = "connected-data-plane";

export const prismaMobileEndpointIds = [
  "summary",
  "sales_today",
  "cash_current",
  "inventory_watchlist",
  "alerts",
  "reports_daily",
  "branches",
  "health"
] as const;

export type PrismaMobileEndpointId = (typeof prismaMobileEndpointIds)[number];

export const PrismaMobileSeveritySchema = z.enum(["critica", "alta", "media", "info"]);
export const PrismaMobileHealthSchema = z.enum(["sano", "revisar", "urgente", "offline"]);
export const PrismaMobileInventoryStateSchema = z.enum(["critico", "reponer", "normal", "sobrestock"]);
export const PrismaMobilePrioritySchema = z.enum(["alta", "media", "baja"]);
export const PrismaMobileRuntimeModeSchema = z.enum(["connected", "partial", "offline"]);
export const PrismaMobileSourceSchema = z.enum(["connected-data-plane", "tablet-pos", "pc-backoffice", "local-cache", "unavailable"]);

export const PrismaMobileApiMetaSchema = z.object({
  apiVersion: z.literal(PRISMA_MOBILE_API_VERSION),
  endpoint: z.string().min(1),
  generatedAt: z.string().datetime(),
  source: PrismaMobileSourceSchema.default(PRISMA_MOBILE_DATA_SOURCE),
  runtimeMode: PrismaMobileRuntimeModeSchema,
  contractId: z.literal("PRISMA_APP_MOBILE_17_DATA_PLANE"),
  upstreams: z.array(z.object({
    id: z.string().min(1),
    ok: z.boolean(),
    url: z.string().min(1),
    status: z.number().int().optional(),
    latencyMs: z.number().int().nonnegative().optional(),
    error: z.string().optional()
  })).default([])
});

export type PrismaMobileApiMeta = z.infer<typeof PrismaMobileApiMetaSchema>;

export const PrismaMobileKpiSchema = z.object({
  key: z.string().min(1),
  label: z.string().min(1),
  value: z.string().min(1),
  note: z.string(),
  tone: z.enum(["gold", "green", "blue", "red", "neutral"]),
  numericValue: z.number().optional(),
  unit: z.string().optional()
});

export const PrismaMobileActionSchema = z.object({
  title: z.string().min(1),
  detail: z.string().min(1),
  owner: z.string().min(1),
  priority: PrismaMobilePrioritySchema
});

export const PrismaMobileDataReadinessLevelSchema = z.enum(["ready", "partial", "empty", "offline", "blocked"]);
export const PrismaMobileDataReadinessActionSchema = z.object({
  title: z.string().min(1),
  detail: z.string().min(1),
  owner: z.string().min(1),
  priority: PrismaMobilePrioritySchema
});
export const PrismaMobileDataReadinessSchema = z.object({
  level: PrismaMobileDataReadinessLevelSchema,
  label: z.string().min(1),
  headline: z.string().min(1),
  detail: z.string().min(1),
  sourceSummary: z.string().min(1),
  salesState: z.enum(["with_sales", "empty", "unavailable"]),
  inventoryState: z.enum(["with_items", "empty", "unavailable"]),
  pcState: z.enum(["connected", "unavailable"]),
  syncState: z.enum(["clean", "pending", "failed", "unknown"]),
  facts: z.array(z.string().min(1)).default([]),
  actions: z.array(PrismaMobileDataReadinessActionSchema).default([])
});

export const PrismaMobileSalesPointSchema = z.object({
  hour: z.string().min(1),
  label: z.string().min(1),
  amount: z.string().min(1),
  amountCents: z.number().int().nonnegative(),
  height: z.string().min(1)
});

export const PrismaMobileCashMovementSchema = z.object({
  label: z.string().min(1),
  value: z.string().min(1),
  amountCents: z.number().int(),
  detail: z.string().min(1)
});

export const PrismaMobileInventoryItemSchema = z.object({
  sku: z.string().min(1),
  name: z.string().min(1),
  category: z.string().min(1),
  stock: z.string().min(1),
  stockQty: z.number().int().nonnegative(),
  movement: z.string().min(1),
  weeklyUnitsSold: z.number().int().nonnegative(),
  state: PrismaMobileInventoryStateSchema
});

export const PrismaMobileAlertSchema = z.object({
  id: z.string().min(1),
  severity: PrismaMobileSeveritySchema,
  area: z.string().min(1),
  title: z.string().min(1),
  detail: z.string().min(1),
  time: z.string().min(1),
  action: z.string().min(1)
});

export const PrismaMobileReportCardSchema = z.object({
  title: z.string().min(1),
  value: z.string().min(1),
  detail: z.string().min(1),
  footnote: z.string().min(1)
});

export const PrismaMobileBranchSchema = z.object({
  name: z.string().min(1),
  status: PrismaMobileHealthSchema,
  salesToday: z.string().min(1),
  salesTodayCents: z.number().int().nonnegative(),
  salesDelta: z.string().min(1),
  cashState: z.string().min(1),
  alerts: z.number().int().nonnegative(),
  syncLag: z.string().min(1),
  tickets: z.number().int().nonnegative()
});

export const PrismaMobileSummaryPayloadSchema = z.object({
  businessName: z.string().min(1),
  screen: z.literal("hoy"),
  mode: z.literal("owner_mobile"),
  generatedLabel: z.string().min(1),
  health: PrismaMobileHealthSchema,
  urgentAlerts: z.number().int().nonnegative(),
  branchesToReview: z.number().int().nonnegative(),
  dataReadiness: PrismaMobileDataReadinessSchema.default({
    level: "partial",
    label: "Lectura pendiente",
    headline: "La app está esperando datos operativos.",
    detail: "El contrato anterior no incluía readiness; refresca la app para reconstruirlo desde fuentes reales.",
    sourceSummary: "fuente no clasificada",
    salesState: "unavailable",
    inventoryState: "unavailable",
    pcState: "unavailable",
    syncState: "unknown",
    facts: [],
    actions: []
  }),
  kpis: z.array(PrismaMobileKpiSchema).min(1),
  quickActions: z.array(PrismaMobileActionSchema)
});

export const PrismaMobileSalesTodayPayloadSchema = z.object({
  totalSalesCents: z.number().int().nonnegative(),
  totalSalesLabel: z.string().min(1),
  tickets: z.number().int().nonnegative(),
  averageTicketCents: z.number().int().nonnegative(),
  averageTicketLabel: z.string().min(1),
  deltaAgainstYesterday: z.string().min(1),
  strongCategory: z.string().min(1),
  timeline: z.array(PrismaMobileSalesPointSchema)
});

export const PrismaMobileCashCurrentPayloadSchema = z.object({
  status: z.string().min(1),
  expectedCents: z.number().int().nonnegative(),
  expectedLabel: z.string().min(1),
  countedCents: z.number().int().nonnegative(),
  countedLabel: z.string().min(1),
  differenceCents: z.number().int(),
  lastCut: z.string().min(1),
  movements: z.array(PrismaMobileCashMovementSchema)
});

export const PrismaMobileInventoryWatchlistPayloadSchema = z.object({
  items: z.array(PrismaMobileInventoryItemSchema),
  counts: z.object({
    critical: z.number().int().nonnegative(),
    reorder: z.number().int().nonnegative(),
    normal: z.number().int().nonnegative(),
    overstock: z.number().int().nonnegative()
  })
});

export const PrismaMobileAlertsPayloadSchema = z.object({
  alerts: z.array(PrismaMobileAlertSchema),
  counts: z.object({
    total: z.number().int().nonnegative(),
    critical: z.number().int().nonnegative(),
    high: z.number().int().nonnegative(),
    medium: z.number().int().nonnegative(),
    info: z.number().int().nonnegative()
  })
});

export const PrismaMobileReportsDailyPayloadSchema = z.object({
  reportDate: z.string().min(1),
  nextReportAt: z.string().min(1),
  cards: z.array(PrismaMobileReportCardSchema)
});

export const PrismaMobileBranchesPayloadSchema = z.object({
  branches: z.array(PrismaMobileBranchSchema),
  counts: z.object({
    total: z.number().int().nonnegative(),
    healthy: z.number().int().nonnegative(),
    review: z.number().int().nonnegative(),
    urgent: z.number().int().nonnegative(),
    offline: z.number().int().nonnegative()
  })
});

export const PrismaMobileHealthPayloadSchema = z.object({
  ok: z.literal(true),
  product: z.literal("PRISMA App Mobile"),
  surface: z.literal("prisma.mobile.app"),
  contract: z.literal("PRISMA_APP_MOBILE_17_DATA_PLANE"),
  endpoints: z.array(z.enum(prismaMobileEndpointIds)).min(1),
  upstreams: z.array(z.object({ id: z.string(), ok: z.boolean(), latencyMs: z.number().optional(), error: z.string().optional() })).default([])
});

export type PrismaMobileKpi = z.infer<typeof PrismaMobileKpiSchema>;
export type PrismaMobileAction = z.infer<typeof PrismaMobileActionSchema>;
export type PrismaMobileDataReadiness = z.infer<typeof PrismaMobileDataReadinessSchema>;
export type PrismaMobileDataReadinessAction = z.infer<typeof PrismaMobileDataReadinessActionSchema>;
export type PrismaMobileSalesPoint = z.infer<typeof PrismaMobileSalesPointSchema>;
export type PrismaMobileCashMovement = z.infer<typeof PrismaMobileCashMovementSchema>;
export type PrismaMobileInventoryItem = z.infer<typeof PrismaMobileInventoryItemSchema>;
export type PrismaMobileAlert = z.infer<typeof PrismaMobileAlertSchema>;
export type PrismaMobileReportCard = z.infer<typeof PrismaMobileReportCardSchema>;
export type PrismaMobileBranch = z.infer<typeof PrismaMobileBranchSchema>;
export type PrismaMobileSummaryPayload = z.infer<typeof PrismaMobileSummaryPayloadSchema>;
export type PrismaMobileSalesTodayPayload = z.infer<typeof PrismaMobileSalesTodayPayloadSchema>;
export type PrismaMobileCashCurrentPayload = z.infer<typeof PrismaMobileCashCurrentPayloadSchema>;
export type PrismaMobileInventoryWatchlistPayload = z.infer<typeof PrismaMobileInventoryWatchlistPayloadSchema>;
export type PrismaMobileAlertsPayload = z.infer<typeof PrismaMobileAlertsPayloadSchema>;
export type PrismaMobileReportsDailyPayload = z.infer<typeof PrismaMobileReportsDailyPayloadSchema>;
export type PrismaMobileBranchesPayload = z.infer<typeof PrismaMobileBranchesPayloadSchema>;
export type PrismaMobileHealthPayload = z.infer<typeof PrismaMobileHealthPayloadSchema>;

export type PrismaMobileApiEnvelope<TData> = {
  ok: true;
  data: TData;
  meta: PrismaMobileApiMeta;
};

export function buildMobileApiMeta(
  endpoint: PrismaMobileEndpointId,
  options: Partial<Pick<PrismaMobileApiMeta, "source" | "runtimeMode" | "upstreams">> = {}
): PrismaMobileApiMeta {
  return PrismaMobileApiMetaSchema.parse({
    apiVersion: PRISMA_MOBILE_API_VERSION,
    endpoint,
    generatedAt: new Date().toISOString(),
    source: options.source ?? PRISMA_MOBILE_DATA_SOURCE,
    runtimeMode: options.runtimeMode ?? "connected",
    upstreams: options.upstreams ?? [],
    contractId: "PRISMA_APP_MOBILE_17_DATA_PLANE"
  });
}

export function okMobileResponse<TData>(endpoint: PrismaMobileEndpointId, data: TData, metaOptions: Partial<Pick<PrismaMobileApiMeta, "source" | "runtimeMode" | "upstreams">> = {}): PrismaMobileApiEnvelope<TData> {
  return { ok: true, data, meta: buildMobileApiMeta(endpoint, metaOptions) };
}

export function noStoreJsonInit(): ResponseInit {
  return { headers: { "Cache-Control": "no-store, max-age=0", "Content-Type": "application/json; charset=utf-8" } };
}
