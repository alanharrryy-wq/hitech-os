import type { SharedSyncEvent } from "@shared-kernel/sync/events";

export const PC_SYNC_EVENTS: ReadonlyArray<SharedSyncEvent> = [
  "sale.created",
  "sale.completed",
  "ticket.closed",
  "stock.decremented",
  "inventory.low_stock_detected",
  "sale.cancelled",
  "sale.refunded",
  "cash.session.opened",
  "cash.movement.recorded",
  "shift.opened",
  "shift.closed",
  "stock.adjusted",
  "catalog.product.created",
  "catalog.product.updated",
  "sync.event.sent",
  "sync.event.failed",
  "sync.conflict.detected",
  "sync.conflict.resolved",
  "supplier.created",
  "supplier.updated",
  "supplier.disabled",
  "product.supplier.linked",
  "product.supplier.unlinked",
  "product.supplier.updated"
];
