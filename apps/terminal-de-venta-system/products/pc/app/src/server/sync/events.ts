import type { SharedSyncEvent } from "@shared-kernel/sync/events";

export const PC_SYNC_EVENTS: ReadonlyArray<SharedSyncEvent> = [
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
];
