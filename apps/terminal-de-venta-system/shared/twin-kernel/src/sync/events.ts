export const SHARED_SYNC_EVENTS = [
  "sale.created",
  "sale.completed",
  "ticket.closed",
  "stock.decremented",
  "inventory.low_stock_detected",
  "sale.cancelled",
  "sale.refunded",
  "shift.opened",
  "shift.closed",
  "stock.adjusted",
  "catalog.product.created",
  "catalog.product.updated",
  "sync.event.sent",
  "sync.event.failed",
  "sync.conflict.detected",
  "sync.conflict.resolved"
] as const;

export type SharedSyncEvent = (typeof SHARED_SYNC_EVENTS)[number];

export const SHARED_OUTBOX_STATES = ["pending", "sent", "failed", "acked", "conflict"] as const;
export type SharedOutboxState = (typeof SHARED_OUTBOX_STATES)[number];

export const SHARED_CONFLICT_CODES = [
  "product_discontinued",
  "old_local_price",
  "negative_stock",
  "duplicate_event",
  "terminal_not_registered",
  "sale_outside_shift",
  "inconsistent_sequence",
  "invalid_schema",
  "unknown_topic"
] as const;
export type SharedConflictCode = (typeof SHARED_CONFLICT_CODES)[number];

export const SHARED_EVENT_ENVELOPE_FIELDS = [
  "eventId",
  "topic",
  "businessId",
  "terminalId",
  "actorId",
  "source",
  "occurredAt",
  "payload",
  "schemaVersion"
] as const;
export type SharedEventEnvelopeField = (typeof SHARED_EVENT_ENVELOPE_FIELDS)[number];
