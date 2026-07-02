import type {
  PrismaMobileAlert,
  PrismaMobileBranch,
  PrismaMobileCashCurrentPayload,
  PrismaMobileHealthPayload,
  PrismaMobileInventoryItem,
  PrismaMobileReportsDailyPayload,
  PrismaMobileSalesTodayPayload,
  PrismaMobileSummaryPayload
} from "../prisma-app-api-contracts";
import type { PrismaMobileSnapshotPayload } from "../prisma-mobile-snapshot-contract";

export type UpstreamId = "tablet" | "pc" | "control" | "blackbox" | "local";
export type EndpointRole = "health" | "sales" | "inventory" | "events" | "cash" | "dashboard" | "branch" | "incidents" | "snapshot";
export type DataPlaneRuntimeMode = "live" | "partial" | "offline" | "stale" | "unknown" | "demo-disabled";
export type FetchStatus = "ok" | "http_error" | "timeout" | "parse_error" | "network_error" | "disabled";
export type SourceStatusValue = "ok" | "stale" | "offline" | "error" | "unknown";

export type MobileDataPlaneConfig = {
  businessId: string;
  terminalId: string;
  businessName: string;
  customerId: string;
  tenantId: string;
  licenseId: string;
  planLabel: string;
  activationMode: string;
  activationModeLabel: string;
  licenseStateLabel: string;
  authorizationLabel: string;
  pcDeviceId: string;
  tabletDeviceId: string;
  mobileDeviceId: string;
  tabletOrigin: string | null;
  pcOrigin: string | null;
  controlOrigin: string | null;
  blackBoxOrigin: string | null;
  requestTimeoutMs: number;
  tabletTimeoutMs: number;
  pcTimeoutMs: number;
  controlTimeoutMs: number;
  blackBoxTimeoutMs: number;
  retryCount: number;
  staleAfterMs: number;
  lowStockDefaultThreshold: number;
  overstockDefaultThreshold: number;
  cashDifferenceWarningCents: number;
  cashDifferenceCriticalCents: number;
};

export type UpstreamProbe = {
  id: UpstreamId | "mobile";
  ok: boolean;
  url: string;
  status?: number;
  latencyMs?: number;
  error?: string;
};

export type MobileSourceStatus = {
  id: UpstreamId;
  label: string;
  status: SourceStatusValue;
  lastSeenAt: string | null;
  freshnessSeconds: number | null;
  latencyMs: number | null;
  errorCount: number;
  lastError: string | null;
  warnings: string[];
};

export type FetchResult<T> = {
  status: FetchStatus;
  url: string;
  upstream: UpstreamId;
  role: EndpointRole;
  data: T | null;
  httpStatus?: number;
  latencyMs: number;
  error?: string;
};

export type CanonicalSaleLine = {
  productId: string;
  sku: string;
  name: string;
  qty: number;
  unitPriceCents: number;
  totalCents: number;
  category: string;
};

export type CanonicalSale = {
  id: string;
  ticketNumber: string;
  createdAt: string;
  completedAt: string;
  totalCents: number;
  subtotalCents: number;
  discountCents: number;
  paymentMethod: string;
  operatorId: string;
  terminalId: string;
  lines: CanonicalSaleLine[];
};

export type CanonicalSalesToday = {
  sales: CanonicalSale[];
  totalSalesCents: number;
  tickets: number;
  averageTicketCents: number;
  hourlyBuckets: Array<{ hour: string; amountCents: number; tickets: number }>;
  topCategory: string;
  sourceLabel: string;
};

export type CanonicalInventoryItem = {
  productId: string;
  sku: string;
  name: string;
  category: string;
  stockQty: number;
  lowStockThreshold: number;
  overstockThreshold: number;
  weeklyUnitsSold: number;
  lastMovementLabel: string;
};

export type CanonicalInventoryWatchlist = {
  items: CanonicalInventoryItem[];
  critical: number;
  reorder: number;
  normal: number;
  overstock: number;
};

export type CanonicalOutboxState = {
  pending: number;
  failed: number;
  acked: number;
  lastSyncedAt: string | null;
  oldestPendingAt: string | null;
};

export type CanonicalCashState = {
  expectedCents: number;
  countedCents: number | null;
  differenceCents: number;
  openedAt: string | null;
  lastCutAt: string | null;
  cashInCents: number;
  cashOutCents: number;
  cardCents: number;
  transferCents: number;
};

export type CanonicalPcDashboard = {
  ok: boolean;
  branchName: string;
  branchStatus: "sano" | "revisar" | "urgente" | "offline";
  consolidatedSalesCents: number | null;
  consolidatedTickets: number | null;
  syncLagMs: number | null;
  activeAlerts: number;
};

export type MobileDataPlaneState = {
  config: MobileDataPlaneConfig;
  probes: UpstreamProbe[];
  sourceStatuses: MobileSourceStatus[];
  salesToday: CanonicalSalesToday;
  inventory: CanonicalInventoryWatchlist;
  outbox: CanonicalOutboxState;
  cash: CanonicalCashState;
  pc: CanonicalPcDashboard;
  warnings: string[];
  runtimeMode: DataPlaneRuntimeMode;
};

export type MobileEndpointPayloads = {
  summary: PrismaMobileSummaryPayload;
  sales_today: PrismaMobileSalesTodayPayload;
  cash_current: PrismaMobileCashCurrentPayload;
  inventory_watchlist: { items: PrismaMobileInventoryItem[]; counts: { critical: number; reorder: number; normal: number; overstock: number } };
  alerts: { alerts: PrismaMobileAlert[]; counts: { total: number; critical: number; high: number; medium: number; info: number } };
  reports_daily: PrismaMobileReportsDailyPayload;
  branches: { branches: PrismaMobileBranch[]; counts: { total: number; healthy: number; review: number; urgent: number; offline: number } };
  health: PrismaMobileHealthPayload;
  snapshot: PrismaMobileSnapshotPayload;
};
