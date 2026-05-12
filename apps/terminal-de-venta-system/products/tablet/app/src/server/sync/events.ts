import type { SharedSyncEvent } from "@shared-kernel/sync/events";

export const TABLET_SYNC_EVENTS: ReadonlyArray<SharedSyncEvent> = [
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
  "sync.event.sent",
  "sync.event.failed",
  "sync.conflict.detected"
];
