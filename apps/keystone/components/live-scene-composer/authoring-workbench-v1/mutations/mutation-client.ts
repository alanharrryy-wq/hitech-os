import type { AuthoringWorkbenchState } from "../authoring-workbench-contracts";
import { createRuntimeObservationFromDocument } from "../runtime/runtime-observation";
import { reconcileSelectionAfterMutation } from "../selection/selection-model";
import { createInMemoryPreviewAdapter, type RuntimeMutationBridgeAdapter } from "../../../runtime-mutation-bridge/authoring-workbench-v1/adapters/in-memory-preview-adapter";
import type { RuntimeMutationCommand, RuntimeMutationResult } from "../../../runtime-mutation-bridge/authoring-workbench-v1/contract";
import { applyRuntimeMutationThroughBridge } from "../../../runtime-mutation-bridge/authoring-workbench-v1/applyRuntimeMutationThroughBridge";

export interface MutationClientOutcome {
  readonly state: AuthoringWorkbenchState;
  readonly result: RuntimeMutationResult;
}

export function applyWorkbenchMutation(
  state: AuthoringWorkbenchState,
  command: RuntimeMutationCommand,
  adapter: RuntimeMutationBridgeAdapter = createInMemoryPreviewAdapter()
): MutationClientOutcome {
  const result = applyRuntimeMutationThroughBridge(
    {
      baseline: state.documents.baseline,
      draft: state.documents.draft,
      currentSelection: state.selection.primaryTarget,
    },
    command,
    adapter
  );
  const reconciledSelection = reconcileSelectionAfterMutation(result.preview, state.selection);
  const nextState: AuthoringWorkbenchState = {
    ...state,
    documents: {
      baseline: result.baseline,
      draft: result.draft,
      preview: result.preview,
    },
    selection: reconciledSelection,
    runtimeObserved: createRuntimeObservationFromDocument(result.preview, reconciledSelection.primaryTarget),
    feedback: [result.feedback, ...state.feedback].slice(0, 10),
  };
  return {
    state: nextState,
    result,
  };
}
