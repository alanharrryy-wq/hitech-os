export const SHARED_SYNC_EVENTS = [
  "sale.created",
  "ticket.closed",
  "return.created",
  "shift.opened",
  "shift.closed",
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
] as const;

export type SharedSyncEvent = (typeof SHARED_SYNC_EVENTS)[number];
