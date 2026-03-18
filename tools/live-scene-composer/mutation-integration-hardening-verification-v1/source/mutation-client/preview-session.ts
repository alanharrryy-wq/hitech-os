import {
  type MutationEnvelope,
  type MutationClientClock,
  type PreviewPatchSummary,
  type PreviewSession,
  createDefaultClock
} from "./contracts";
import { summarizePreviewDiff } from "./preview-diff";

export interface OpenPreviewSessionArgs {
  readonly sceneId: string;
  readonly baselineRevision: string;
  readonly draftRevision: string;
  readonly clock?: MutationClientClock;
}

export function openPreviewSession(args: OpenPreviewSessionArgs): PreviewSession {
  const clock = args.clock ?? createDefaultClock();
  return {
    sessionId: clock.nextId("preview-session"),
    sceneId: args.sceneId,
    baselineRevision: args.baselineRevision,
    draftRevision: args.draftRevision,
    openedAtUtc: clock.nowUtc(),
    updatedAtUtc: clock.nowUtc(),
    mutationIds: [],
    pendingEnvelopes: [],
    diffSummary: emptyDiffSummary(),
    warnings: [],
    commitReady: false
  };
}

export function stageEnvelope(session: PreviewSession, envelope: MutationEnvelope, stagedShape: Readonly<Record<string, unknown>> = {}): PreviewSession {
  const clock = createDefaultClock();
  const nextDiff = summarizePreviewDiff({ baseline: {}, draft: {}, staged: stagedShape });
  const nextWarnings = [...session.warnings];
  if (envelope.scope === "preview-only" && Object.keys(envelope.payload).length === 0) {
    nextWarnings.push(`Preview envelope ${envelope.mutationId} carries an empty payload.`);
  }
  return {
    ...session,
    updatedAtUtc: clock.nowUtc(),
    mutationIds: [...session.mutationIds, envelope.mutationId],
    pendingEnvelopes: [...session.pendingEnvelopes, envelope],
    diffSummary: nextDiff,
    warnings: nextWarnings,
    commitReady: session.pendingEnvelopes.length + 1 > 0
  };
}

export function discardPreviewSession(session: PreviewSession): PreviewSession {
  const clock = createDefaultClock();
  return {
    ...session,
    updatedAtUtc: clock.nowUtc(),
    mutationIds: [],
    pendingEnvelopes: [],
    diffSummary: emptyDiffSummary(),
    warnings: [],
    commitReady: false
  };
}

export function commitPreviewSession(session: PreviewSession): PreviewSession {
  const clock = createDefaultClock();
  return {
    ...session,
    updatedAtUtc: clock.nowUtc(),
    warnings: [...session.warnings, "commit requested"],
    commitReady: true
  };
}

function emptyDiffSummary(): PreviewPatchSummary {
  return {
    changedFields: [],
    changeCount: 0,
    addedEntityIds: [],
    removedEntityIds: [],
    movedEntityIds: []
  };
}
