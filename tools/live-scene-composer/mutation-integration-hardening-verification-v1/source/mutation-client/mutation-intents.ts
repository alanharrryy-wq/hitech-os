import {
  type MutationEnvelope,
  type MutationMode,
  type MutationScope,
  type MutationSource,
  type MutationTarget,
  type MutationType,
  type MutationClientClock,
  createDefaultClock
} from "./contracts";

export interface BuildMutationArgs {
  readonly source: MutationSource;
  readonly type: MutationType;
  readonly mode: MutationMode;
  readonly scope: MutationScope;
  readonly target: MutationTarget;
  readonly payload?: Readonly<Record<string, unknown>>;
  readonly previewSessionId?: string;
  readonly tags?: readonly string[];
  readonly clock?: MutationClientClock;
}

export function buildMutationEnvelope(args: BuildMutationArgs): MutationEnvelope {
  const clock = args.clock ?? createDefaultClock();
  return {
    mutationId: clock.nextId("mutation"),
    source: args.source,
    type: args.type,
    mode: args.mode,
    scope: args.scope,
    target: args.target,
    payload: args.payload ?? {},
    previewSessionId: args.previewSessionId,
    requestTimestampUtc: clock.nowUtc(),
    reversibility: deriveReversibility(args.type, args.scope),
    tags: args.tags ?? []
  };
}

export function buildPreviewEnvelope(args: Omit<BuildMutationArgs, "scope">): MutationEnvelope {
  return buildMutationEnvelope({ ...args, scope: "preview-only" });
}

export function buildCommitEnvelope(args: Omit<BuildMutationArgs, "scope">): MutationEnvelope {
  return buildMutationEnvelope({ ...args, scope: "commit-capable" });
}

export function deriveReversibility(type: MutationType, scope: MutationScope) {
  if (scope === "full-draft-discard") {
    return { reversible: false, inverseStrategy: "discard-session" as const, notes: ["full draft discard is terminal for the active preview session"] };
  }
  if (scope === "local-reset") {
    return { reversible: true, inverseStrategy: "reset-target" as const, notes: ["reset stays target-scoped"] };
  }
  switch (type) {
    case "layout-move":
    case "layout-resize":
    case "widget-style-update":
    case "widget-props-update":
      return { reversible: true, inverseStrategy: "patch-inverse" as const, notes: ["patch fields can be inverted when lineage is available"] };
    case "widget-remove":
    case "slot-insert-widget":
      return { reversible: true, inverseStrategy: "snapshot-restore" as const, notes: ["structural changes want snapshot restore fallback"] };
    case "draft-discard":
      return { reversible: false, inverseStrategy: "discard-session" as const, notes: ["discard clears the active preview chain"] };
    case "draft-commit":
      return { reversible: true, inverseStrategy: "snapshot-restore" as const, notes: ["commit should retain enough lineage for compare and explicit rollback"] };
    default:
      return { reversible: true, inverseStrategy: "patch-inverse" as const, notes: [] };
  }
}
