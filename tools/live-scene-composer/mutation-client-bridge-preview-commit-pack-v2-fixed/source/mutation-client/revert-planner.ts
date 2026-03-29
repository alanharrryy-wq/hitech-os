import { type MutationEnvelope, type MutationTarget } from "./contracts";

export interface RevertPlan {
  readonly target: MutationTarget;
  readonly mutationIds: readonly string[];
  readonly strategy: "patch-inverse" | "snapshot-restore" | "reset-target" | "discard-session";
  readonly notes: readonly string[];
}

export function buildRevertPlan(envelopes: readonly MutationEnvelope[], target: MutationTarget): RevertPlan {
  const relevant = envelopes.filter((envelope) => sameTarget(envelope.target, target));
  const strategy = relevant.some((entry) => entry.reversibility.inverseStrategy === "snapshot-restore")
    ? "snapshot-restore"
    : relevant.some((entry) => entry.reversibility.inverseStrategy === "reset-target")
      ? "reset-target"
      : relevant.some((entry) => entry.reversibility.inverseStrategy === "discard-session")
        ? "discard-session"
        : "patch-inverse";

  return {
    target,
    mutationIds: relevant.map((entry) => entry.mutationId),
    strategy,
    notes: [
      `relevant mutation count: ${relevant.length}`,
      `strategy chosen: ${strategy}`
    ]
  };
}

function sameTarget(left: MutationTarget, right: MutationTarget): boolean {
  if (left.kind !== right.kind || left.sceneId !== right.sceneId) {
    return false;
  }
  switch (left.kind) {
    case "scene":
      return true;
    case "layout-node":
      return left.layoutNodeId === (right as typeof left).layoutNodeId;
    case "slot":
      return left.slotId === (right as typeof left).slotId;
    case "widget":
      return left.widgetId === (right as typeof left).widgetId;
    case "draft":
      return left.draftRevision === (right as typeof left).draftRevision;
  }
}
