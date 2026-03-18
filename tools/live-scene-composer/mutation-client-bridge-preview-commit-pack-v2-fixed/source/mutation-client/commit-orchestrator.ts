import {
  type BridgeDecision,
  type MutationEnvelope,
  type PreviewSession
} from "./contracts";
import { validateMutationEnvelope, type ValidationContext } from "./validation";
import { requestBridgePreview, requestBridgeCommit, requestBridgeDiscard, type BridgeClient } from "./bridge-client";

export interface CommitWorkflowResult {
  readonly session: PreviewSession;
  readonly previewDecision?: BridgeDecision;
  readonly commitDecision?: BridgeDecision;
  readonly discardDecision?: BridgeDecision;
  readonly validationErrors: readonly string[];
}

export async function previewThenCommit(
  client: BridgeClient,
  session: PreviewSession,
  envelope: MutationEnvelope,
  context: ValidationContext = {}
): Promise<CommitWorkflowResult> {
  const validation = validateMutationEnvelope(envelope, context);
  if (!validation.ok) {
    return {
      session,
      validationErrors: validation.issues.map((issue) => issue.message)
    };
  }

  const previewDecision = await requestBridgePreview(client, envelope);
  if (!previewDecision.accepted) {
    return {
      session,
      previewDecision,
      validationErrors: []
    };
  }

  const commitDecision = await requestBridgeCommit(client, {
    ...envelope,
    scope: "accepted-state-transition",
    previewSessionId: session.sessionId
  });

  return {
    session,
    previewDecision,
    commitDecision,
    validationErrors: []
  };
}

export async function discardSession(
  client: BridgeClient,
  session: PreviewSession,
  envelope: MutationEnvelope
): Promise<CommitWorkflowResult> {
  const discardDecision = await requestBridgeDiscard(client, {
    ...envelope,
    type: "draft-discard",
    scope: "full-draft-discard",
    previewSessionId: session.sessionId
  });

  return {
    session,
    discardDecision,
    validationErrors: []
  };
}
