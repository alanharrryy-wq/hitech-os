import { type BridgeDecision, type DiagnosticsEvent, type MutationClientClock, type MutationEnvelope, createDefaultClock } from "./contracts";

export function createDiagnosticsEvent(args: {
  readonly category: DiagnosticsEvent["category"];
  readonly level: DiagnosticsEvent["level"];
  readonly message: string;
  readonly envelope?: MutationEnvelope;
  readonly sessionId?: string;
  readonly details?: Readonly<Record<string, unknown>>;
  readonly clock?: MutationClientClock;
}): DiagnosticsEvent {
  const clock = args.clock ?? createDefaultClock();
  return {
    eventId: clock.nextId("diagnostic"),
    level: args.level,
    category: args.category,
    mutationId: args.envelope?.mutationId,
    sessionId: args.sessionId,
    message: args.message,
    details: args.details,
    atUtc: clock.nowUtc()
  };
}

export function diagnosticsFromDecision(decision: BridgeDecision): readonly DiagnosticsEvent[] {
  const clock = createDefaultClock();
  return [
    {
      eventId: clock.nextId("diagnostic"),
      level: decision.accepted ? "info" : "error",
      category: decision.decisionKind.includes("commit") ? "bridge-commit" : "bridge-preview",
      mutationId: decision.mutationId,
      message: decision.reason ?? decision.decisionKind,
      details: { adapterKey: decision.adapterKey, diagnostics: decision.diagnostics },
      atUtc: clock.nowUtc()
    }
  ];
}
