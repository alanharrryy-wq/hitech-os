import type { SyncEventEnvelope } from "@/lib/core/types";

export type OutboxSnapshot = SyncEventEnvelope & {
  attempts?: number;
  ageMinutes?: number;
  topicGroup?: "ventas" | "devoluciones" | "turno" | "sincronización";
};

export function summarizeOutbox(events: OutboxSnapshot[]) {
  const pending = events.filter((item) => item.status === "pending");
  const failed = events.filter((item) => item.status === "failed");
  const sent = events.filter((item) => item.status === "sent");
  return {
    total: events.length,
    pending: pending.length,
    failed: failed.length,
    sent: sent.length,
    retryable: events.filter((item) => (item.attempts ?? 0) > 0 && item.status !== "sent").length,
    oldestAgeMinutes: Math.max(0, ...events.map((item) => item.ageMinutes ?? 0))
  };
}

export function pickRetryCandidates(events: OutboxSnapshot[], limit = 5) {
  return events
    .filter((item) => item.status === "failed" || item.status === "pending")
    .sort((a, b) => (b.ageMinutes ?? 0) - (a.ageMinutes ?? 0) || (b.attempts ?? 0) - (a.attempts ?? 0))
    .slice(0, limit);
}
