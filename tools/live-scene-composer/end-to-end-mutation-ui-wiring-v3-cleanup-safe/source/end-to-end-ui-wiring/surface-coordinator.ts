import type { SelectionContext, SurfaceActionEnvelope } from "./contracts";
import { buildApplyBarState } from "./apply-bar";
import { buildSurfaceFocusModel } from "./focus-sync";
import { buildOverlayRenderState } from "./render-state";
import { deriveCommitControlModel } from "./commit-controls";
import { EndToEndMutationPipeline } from "./mutation-pipeline";

export interface CoordinatedSurfaceState {
  readonly focus: ReturnType<typeof buildSurfaceFocusModel>;
  readonly overlay: ReturnType<typeof buildOverlayRenderState>;
  readonly applyBar: ReturnType<typeof buildApplyBarState>;
  readonly commitControls: ReturnType<typeof deriveCommitControlModel>;
}

export class SurfaceCoordinator {
  private readonly pipeline: EndToEndMutationPipeline;

  public constructor(private readonly context: SelectionContext) {
    this.pipeline = new EndToEndMutationPipeline(context);
  }

  public readState(): CoordinatedSurfaceState {
    const pipelineState = this.pipeline.getState();
    const applyBar = buildApplyBarState(pipelineState.previewSession);
    return {
      focus: buildSurfaceFocusModel(this.context),
      overlay: buildOverlayRenderState(this.context),
      applyBar,
      commitControls: deriveCommitControlModel(applyBar)
    };
  }

  public async dispatch(action: SurfaceActionEnvelope) {
    return this.pipeline.dispatch(action);
  }
}
