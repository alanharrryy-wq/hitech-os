export type InventoryStateFilter = "all" | "critical" | "low" | "ok";
export type InventoryCountStatusFilter = "all" | "open" | "review" | "closed";
export type InventoryAuditSeverityFilter = "all" | "CRÍTICO" | "ALTO" | "MEDIO";
export type InventoryWorkspaceView = "stock" | "counts" | "audit";

export type InventoryFilters = {
  q: string;
  location: string;
  state: InventoryStateFilter;
  countStatus: InventoryCountStatusFilter;
  auditSeverity: InventoryAuditSeverityFilter;
};

export type StockSnapshotView = {
  id: string;
  sku: string;
  productName: string;
  location: string;
  onHand: number;
  reserved: number;
  available: number;
  daysCover: number;
  daysCoverLabel: string;
  state: "critical" | "low" | "ok";
  stateLabel: string;
  snapshotAt: string;
  snapshotAtLabel: string;
};

export type StockLedgerEntry = {
  id: string;
  sku: string;
  productName: string;
  movement: string;
  quantityDelta: number;
  reason: string;
  location: string;
  source: string;
  sourceId: string;
  actor: string;
  beforeQty: number | null;
  afterQty: number | null;
  createdAt: string;
  createdAtLabel: string;
  confidence: "real" | "derived" | "missing";
};

export type AuditCountView = {
  id: string;
  location: string;
  countedBy: string;
  variance: number;
  status: string;
  countedAt: string;
  countedAtLabel: string;
  accuracy: number | null;
  accuracyLabel: string;
};

export type InventoryFindingSeverity = "CRÍTICO" | "ALTO" | "MEDIO";

export type InventoryFinding = {
  id: string;
  severity: InventoryFindingSeverity;
  type: string;
  title: string;
  entityLabel: string;
  detail: string;
  recommendedAction: string;
};

export type InventorySummary = {
  stockedSkuCount: number;
  criticalStockCount: number;
  lowStockCount: number;
  movementCount: number;
  countCount: number;
  openCountCount: number;
  varianceAbsoluteTotal: number;
  inventoryAccuracy: number | null;
};

export type InventoryWorkspace = {
  filters: InventoryFilters;
  locations: string[];
  snapshots: StockSnapshotView[];
  ledger: StockLedgerEntry[];
  counts: AuditCountView[];
  auditFindings: InventoryFinding[];
  countFindings: InventoryFinding[];
  summary: InventorySummary;
  meta: {
    source: "canonical_prisma" | "fallback_empty";
    confidence: "real" | "derived" | "blocked";
    persistence: "available" | "unavailable";
    ledgerMode: "schema_native" | "derived_from_stock_movement" | "unavailable";
    generatedAt: string;
    warnings: string[];
  };
};
