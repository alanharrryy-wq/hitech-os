export type PendingSendStatus = "pending" | "failed" | "sent" | "acked" | "conflict";
export type SyncRisk="ok"|"warn"|"danger";

export type SyncOperationProvenance = {
  source: string | null;
  businessId: string;
  storeId: string | null;
  terminalId: string | null;
  deviceId: string | null;
  actorId: string | null;
  aggregateId: string;
  originRecordId: string | null;
  idempotencyKey: string | null;
  correlationId: string | null;
  traceId: string | null;
};

export type SyncDeliveryEvidence = {
  sentAt: string | null;
  syncedAt: string | null;
  ackedAt: string | null;
  failedAt: string | null;
  conflictedAt: string | null;
  lastAttemptAt: string | null;
  nextRetryAt: string | null;
  remoteEventId: string | null;
  remoteLedgerId: string | null;
  remoteLifecycleStatus: string | null;
  remoteConflictCode: string | null;
  remoteRejectedReason: string | null;
};

export type SyncPanelItem = {
  id: string;
  eventId: string;
  title: string;
  description: string;
  status: PendingSendStatus;
  statusLabel: string;
  risk: SyncRisk;
  attempts: number;
  createdAt: string;
  canRetry: boolean;
  provenance: SyncOperationProvenance;
  delivery: SyncDeliveryEvidence;
  resolutionOwner: "pc_backoffice" | null;
  resolutionLabel: string | null;
};

export type SyncPanelSummary = {
  total: number;
  pending: number;
  failed: number;
  sent: number;
  acked: number;
  conflict: number;
  risk: SyncRisk;
  headline: string;
  operatorMessage: string;
  offlineVisible: boolean;
  lastCheckedAt: string;
};

export type SyncPanelResponse = {
  summary: SyncPanelSummary;
  items: SyncPanelItem[];
  diagnostics: string[];
};

export type SyncRetryPreparationResult = {
  scope: "selected" | "all_failed";
  requested: number | null;
  eligible: number;
  updated: number;
  skipped: number | null;
  eligibleIds: string[];
  skippedIds: string[];
  message: string;
};

export const SAFE_SYNC_COPY = {
  ready: "Todo enviado",
  pending: "Hay información guardada localmente esperando envío.",
  failed: "Hay eventos fallidos que necesitan reintento.",
  conflict: "Hay información que requiere revisión antes de enviarse.",
  offline: "Sin conexión visible. La Tablet sigue trabajando en local."
} as const;
