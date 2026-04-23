import type { SharedSyncEvent } from "@shared-kernel/sync/events";

export const PC_SYNC_EVENTS: ReadonlyArray<SharedSyncEvent> = [
  "catalog.updated",
  "stock.adjusted",
  "stock.received",
  "purchase_order.created",
  "replenishment.requested",
  "audit.completed",
  "sync.started",
  "sync.succeeded",
  "sync.failed",
  "sync.conflict_detected",
  "outbox.enqueued",
  "outbox.dispatched"
];
