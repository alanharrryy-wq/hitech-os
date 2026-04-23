import type { SharedSyncEvent } from "@shared-kernel/sync/events";

export const TABLET_SYNC_EVENTS: ReadonlyArray<SharedSyncEvent> = [
  "sale.created",
  "ticket.closed",
  "return.created",
  "shift.opened",
  "shift.closed",
  "sync.started",
  "sync.succeeded",
  "sync.failed",
  "sync.conflict_detected",
  "outbox.enqueued",
  "outbox.dispatched"
];
