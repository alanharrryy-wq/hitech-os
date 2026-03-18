import { type BridgeDecision, type MutationEnvelope, type MutationHistoryEntry, targetKey } from "./contracts";

export function toHistoryEntry(envelope: MutationEnvelope, decision: BridgeDecision): MutationHistoryEntry {
  return {
    mutationId: envelope.mutationId,
    sessionId: envelope.previewSessionId,
    type: envelope.type,
    scope: envelope.scope,
    targetKey: targetKey(envelope.target),
    decisionKind: decision.decisionKind,
    atUtc: envelope.requestTimestampUtc,
    notes: [...decision.diagnostics, decision.reason ?? "no explicit reason"]
  };
}

export class MutationHistoryLog {
  private readonly entries: MutationHistoryEntry[] = [];

  public append(entry: MutationHistoryEntry): void {
    this.entries.push(entry);
  }

  public all(): readonly MutationHistoryEntry[] {
    return [...this.entries];
  }

  public forTarget(target: string): readonly MutationHistoryEntry[] {
    return this.entries.filter((entry) => entry.targetKey === target);
  }
}
