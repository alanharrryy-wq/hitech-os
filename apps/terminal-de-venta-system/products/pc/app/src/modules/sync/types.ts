export type SyncConflictSeverity = "warning" | "conflict" | "rejected";

export type SyncConflictCatalogItem = {
  code: string;
  label: string;
  severity: SyncConflictSeverity;
  detail: string;
};

export type SyncRecentEvent = {
  id: string;
  topic: string;
  status: string;
  aggregateId: string;
  createdAt: string;
  createdAtLabel: string;
};

export type SyncReleaseWorkspace = {
  summary: {
    totalEvents: number | null;
    ackedEvents: number | null;
    conflictEvents: number | null;
    failedEvents: number | null;
  };
  requiredFields: string[];
  statusModel: Array<{ status: string; description: string }>;
  conflictCatalog: SyncConflictCatalogItem[];
  recentEvents: SyncRecentEvent[];
  sampleDryRunPayload: unknown;
  meta: {
    persistence: "available" | "unavailable";
    confidence: "real" | "blocked";
    generatedAt: string;
    warnings: string[];
  };
};
