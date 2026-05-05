export type OperationMode = "purchasing" | "receiving" | "replenishment" | "dashboard";
export type DataConfidence = "real" | "partial" | "proxy" | "missing" | "blocked";
export type Severity = "BAJO" | "MEDIO" | "ALTO" | "CRITICO";

export type PurchaseRow = {
  folio: string;
  supplier: string;
  status: string;
  createdAt: string;
  expectedAt: string;
  totalCents: number;
  linesCount: number;
  orderedQty: number;
  receivedQty: number;
  pendingQty: number;
  risk: "OK" | "VENCIDA" | "PARCIAL" | "SIN_LINEAS";
};

export type ReceiptRow = {
  folio: string;
  purchaseFolio: string;
  supplier: string;
  status: string;
  receivedAt: string;
  totalCents: number;
  linesCount: number;
  expectedQty: number;
  receivedQty: number;
  discrepancyQty: number;
  discrepancyCount: number;
  discrepancyLabel: string;
};

export type ReplenishmentRow = {
  sku: string;
  name: string;
  location: string;
  priority: string;
  currentStock: number;
  suggestedQty: number;
  minStock: number;
  maxStock: number;
  reason: string;
};

export type KpiRow = {
  key: string;
  label: string;
  value: string;
  formula: string;
  source: string;
  confidence: DataConfidence;
  range: string;
  href: string;
  note: string;
  status: "ok" | "warning" | "critical" | "empty";
};

export type OperationAlert = {
  severity: Severity;
  module: string;
  title: string;
  detail: string;
  href: string;
};

export type OperationSummary = {
  openOrders: number;
  overdueOrders: number;
  receiptsWithDiscrepancy: number;
  replenishmentSignals: number;
  highPrioritySignals: number;
  netSalesCents: number;
  tickets: number;
  fillRate: number | null;
};

export type OperationWorkspace = {
  mode: OperationMode;
  title: string;
  kicker: string;
  description: string;
  summary: OperationSummary;
  purchases: PurchaseRow[];
  receipts: ReceiptRow[];
  replenishment: ReplenishmentRow[];
  kpis: KpiRow[];
  alerts: OperationAlert[];
  meta: {
    source: "canonical_prisma" | "fallback_empty";
    persistence: "available" | "unavailable";
    confidence: DataConfidence;
    generatedAt: string;
    warnings: string[];
  };
};
