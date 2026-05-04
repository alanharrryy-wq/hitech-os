export type ReturnAuditAction = "selected" | "reason_set" | "submitted" | "completed" | "failed";
export type ReturnAuditEntry = { action: ReturnAuditAction; at: string; actorId: string; saleId: string; detail: string; amountCents?: number };

export function createReturnAuditEntry(input: Omit<ReturnAuditEntry, "at">): ReturnAuditEntry {
  return { ...input, at: new Date().toISOString() };
}

export function summarizeReturnAuditTrail(entries: ReturnAuditEntry[]) {
  const ordered = [...entries].sort((a, b) => a.at.localeCompare(b.at));
  return {
    count: ordered.length,
    firstActionAt: ordered[0]?.at ?? null,
    lastActionAt: ordered.at(-1)?.at ?? null,
    completed: ordered.some(entry => entry.action === "completed"),
    failed: ordered.some(entry => entry.action === "failed"),
    amountCents: ordered.reduce((sum, entry) => sum + (entry.amountCents ?? 0), 0),
  };
}
