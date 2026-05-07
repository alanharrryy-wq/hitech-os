export type TriDbHealthStatus = "READY" | "READY_WITH_CAVEATS" | "BLOCKED" | "UNKNOWN";

export type TriDbSurfaceMetrics = {
  productCount: number;
  saleCount: number;
  outboxCount: number;
  barcodeCount: number;
  lowStockCount: number;
  salesTotalCents: number;
};

export type TriDbStatusTableParity = {
  table: string;
  tabletRows: number;
  pcRows: number;
  pcCoversTablet: boolean;
  deltaPcMinusTablet: number;
};

export type TriDbStatusCardModel = {
  status: TriDbHealthStatus;
  latestBridgeStatus: string;
  generatedAtLabel: string;
  lastSyncLabel: string;
  bridgeTablesProjected: number;
  bridgeRowsInsertedOrUpdated: number;
  bridgeOutboxAcknowledged: number;
  tablet: TriDbSurfaceMetrics;
  pc: TriDbSurfaceMetrics;
  parityOk: boolean;
  parityTables: TriDbStatusTableParity[];
  warnings: string[];
  sourcePath: string;
  evidencePath: string | null;
  mode: "real" | "missing" | "invalid";
};
