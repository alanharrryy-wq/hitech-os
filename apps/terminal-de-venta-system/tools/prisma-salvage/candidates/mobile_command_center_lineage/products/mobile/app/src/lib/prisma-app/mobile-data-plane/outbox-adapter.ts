import type { CanonicalOutboxState } from "./types";
import { asRecord, pickArray, readDateIso, readNonNegativeInt, readString, unwrapOkData } from "./extractors";

export function normalizeOutboxState(payload: unknown): CanonicalOutboxState {
  const data = unwrapOkData(payload);
  const record = asRecord(data);
  const events = pickArray(data, ["events", "items", "outbox", "rows"]);
  if (events.length === 0) {
    return {
      pending: readNonNegativeInt(record, ["pending", "pendingCount"], 0),
      failed: readNonNegativeInt(record, ["failed", "failedCount"], 0),
      acked: readNonNegativeInt(record, ["acked", "sent", "ackedCount"], 0),
      lastSyncedAt: typeof record.lastSyncedAt === "string" ? readDateIso(record, ["lastSyncedAt"], record.lastSyncedAt) : null,
      oldestPendingAt: typeof record.oldestPendingAt === "string" ? readDateIso(record, ["oldestPendingAt"], record.oldestPendingAt) : null
    };
  }
  let pending = 0;
  let failed = 0;
  let acked = 0;
  let oldestPendingAt: string | null = null;
  let lastSyncedAt: string | null = null;
  for (const raw of events) {
    const event = asRecord(raw);
    const status = readString(event, ["status", "state"], "pending").toLowerCase();
    const createdAt = readDateIso(event, ["createdAt", "occurredAt"], new Date().toISOString());
    const syncedAt = typeof event.syncedAt === "string" ? readDateIso(event, ["syncedAt"], event.syncedAt) : null;
    if (status === "failed" || status === "error") failed += 1;
    else if (status === "acked" || status === "sent" || status === "synced") acked += 1;
    else pending += 1;
    if (status === "pending" && (!oldestPendingAt || Date.parse(createdAt) < Date.parse(oldestPendingAt))) oldestPendingAt = createdAt;
    if (syncedAt && (!lastSyncedAt || Date.parse(syncedAt) > Date.parse(lastSyncedAt))) lastSyncedAt = syncedAt;
  }
  return { pending, failed, acked, lastSyncedAt, oldestPendingAt };
}

export function emptyOutboxState(): CanonicalOutboxState {
  return { pending: 0, failed: 0, acked: 0, lastSyncedAt: null, oldestPendingAt: null };
}
