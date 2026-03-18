import type { PreviewSession } from "../mutation-client/contracts";
import type { ValidationContext } from "../mutation-client/validation";
import { validateMutationEnvelope } from "../mutation-client/validation";
import { DefaultBridgeClient, requestBridgeCommit, requestBridgeDiscard, requestBridgePreview, requestBridgeRevert } from "../mutation-client/bridge-client";
import { openPreviewSession, stageEnvelope, commitPreviewSession, discardPreviewSession } from "../mutation-client/preview-session";
import type { SelectionContext, SurfaceActionEnvelope, SurfaceDispatchResult, UiEvidenceEvent } from "./contracts";
import { buildRoutedMutationPlan } from "./intent-builders";
import { assertPlanRoute } from "./bridge-route-gate";

export interface EndToEndPipelineState {
  readonly selectionContext: SelectionContext;
  readonly previewSession?: PreviewSession;
  readonly evidence: readonly UiEvidenceEvent[];
}

export class EndToEndMutationPipeline {
  private readonly client: DefaultBridgeClient;
  private state: EndToEndPipelineState;

  public constructor(selectionContext: SelectionContext, state?: EndToEndPipelineState) {
    this.client = new DefaultBridgeClient();
    this.state = state ?? { selectionContext, evidence: [] };
  }

  public getState(): EndToEndPipelineState {
    return this.state;
  }

  public async dispatch(action: SurfaceActionEnvelope, validationContext: ValidationContext = {}): Promise<SurfaceDispatchResult> {
    const plan = buildRoutedMutationPlan(action);
    const diagnostics = [...assertPlanRoute(plan)];
    const validation = validateMutationEnvelope(plan.envelope, validationContext);
    diagnostics.push(...validation.issues.map((issue) => `${issue.severity}:${issue.code}`));

    if (!validation.ok) {
      this.pushEvidence(action, undefined, "rejected", "Validation rejected UI action.");
      return { accepted: false, plan, diagnostics };
    }

    let previewSession = this.state.previewSession;
    if (!previewSession) {
      previewSession = openPreviewSession({
        sceneId: action.context.selection.sceneId,
        baselineRevision: action.context.baselineRevision,
        draftRevision: action.context.draftRevision
      });
    }

    let accepted = false;
    if (plan.routeAction === "preview") {
      const decision = await requestBridgePreview(this.client, plan.envelope);
      accepted = decision.accepted;
      diagnostics.push(...decision.diagnostics);
      if (accepted) {
        previewSession = stageEnvelope(previewSession, plan.envelope, plan.envelope.payload);
        this.pushEvidence(action, plan.envelope.mutationId, "preview-routed", "Preview routed through bridge client.");
      }
    } else if (plan.routeAction === "commit") {
      const commitBase = previewSession ? commitPreviewSession(previewSession) : previewSession;
      const decision = await requestBridgeCommit(this.client, plan.envelope);
      accepted = decision.accepted;
      diagnostics.push(...decision.diagnostics);
      if (accepted && commitBase) {
        previewSession = commitBase;
        this.pushEvidence(action, plan.envelope.mutationId, "commit-routed", "Commit routed through bridge client.");
      }
    } else if (plan.routeAction === "discard") {
      const decision = await requestBridgeDiscard(this.client, plan.envelope);
      accepted = decision.accepted;
      diagnostics.push(...decision.diagnostics);
      if (accepted && previewSession) {
        previewSession = discardPreviewSession(previewSession);
        this.pushEvidence(action, plan.envelope.mutationId, "discard-routed", "Discard routed through bridge client.");
      }
    } else {
      const decision = await requestBridgeRevert(this.client, plan.envelope);
      accepted = decision.accepted;
      diagnostics.push(...decision.diagnostics);
      this.pushEvidence(action, plan.envelope.mutationId, accepted ? "validated" : "rejected", accepted ? "Reset / revert action routed." : "Reset / revert action rejected.");
    }

    this.state = { ...this.state, previewSession };
    return { accepted, plan, previewSession, diagnostics };
  }

  private pushEvidence(action: SurfaceActionEnvelope, mutationId: string | undefined, stage: UiEvidenceEvent["stage"], message: string): void {
    this.state = {
      ...this.state,
      evidence: [
        ...this.state.evidence,
        {
          eventId: `evidence-${Date.now()}-${this.state.evidence.length + 1}`,
          actionId: action.actionId,
          surface: action.surface,
          mutationId,
          stage,
          message,
          atUtc: new Date().toISOString()
        }
      ]
    };
  }
}
