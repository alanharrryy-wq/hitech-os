export type CatalogStatusFilter = "all" | "active" | "inactive";
export type CatalogIssueFilter = "all" | "missing_barcode" | "duplicate_barcode" | "inactive_product" | "stale_price";

export type CatalogFilters = {
  q: string;
  status: CatalogStatusFilter;
  category: string;
  issue: CatalogIssueFilter;
  selectedSku: string;
};

export type CatalogIssueType = Exclude<CatalogIssueFilter, "all">;
export type CatalogIssueSeverity = "BAJO" | "MEDIO" | "ALTO";

export type CatalogIssue = {
  type: CatalogIssueType;
  severity: CatalogIssueSeverity;
  sku: string;
  productName: string;
  label: string;
  detail: string;
  recommendedAction: string;
};

export type CatalogProductRecord = {
  id: string;
  businessId: string;
  sku: string;
  name: string;
  category: string;
  priceCents: number;
  costCents: number;
  stockOnHand: number;
  isActive: boolean;
  updatedAt: string;
  updatedAtLabel: string;
  barcodes: string[];
  daysCover: number | null;
  issues: CatalogIssue[];
};

export type CatalogSummary = {
  totalProducts: number;
  activeProducts: number;
  inactiveProducts: number;
  categories: number;
  barcodeCount: number;
  missingBarcodeCount: number;
  duplicateBarcodeCount: number;
  stalePriceCount: number;
};

export type CatalogWorkspace = {
  filters: CatalogFilters;
  summary: CatalogSummary;
  categories: string[];
  products: CatalogProductRecord[];
  exceptions: CatalogIssue[];
  selectedProduct: CatalogProductRecord | null;
  meta: {
    source: "canonical_prisma" | "fallback_empty";
    confidence: "real" | "empty" | "blocked";
    persistence: "available" | "unavailable";
    generatedAt: string;
    warnings: string[];
  };
};
