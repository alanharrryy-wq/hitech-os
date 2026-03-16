import {
  applyRuntimeMutationThroughBridge,
  createInMemoryPreviewAdapter,
  createSelectionState,
  reconcileSelectionState,
  type AuthoringMode,
  type MutationFeedback,
  type RuntimeMutationBridgeAdapter,
  type RuntimeMutationCommand,
  type RuntimeMutationResult,
  type RuntimeObservationSnapshot,
  type SceneDocument,
  type SelectionState,
  type SelectionSurface,
  type SelectionTarget,
} from "../../runtime-mutation-bridge/core-v2";

export interface AuthoringWorkbenchDocumentsV2 {
  readonly baseline: SceneDocument;
  readonly draft: SceneDocument;
  readonly preview: SceneDocument;
}

export interface AuthoringWorkbenchStateV2 {
  readonly mode: AuthoringMode;
  readonly documents: AuthoringWorkbenchDocumentsV2;
  readonly selection: SelectionState;
  readonly runtimeObserved: RuntimeObservationSnapshot;
  readonly feedback: readonly MutationFeedback[];
}

export interface MutationClientOutcome {
  readonly state: AuthoringWorkbenchStateV2;
  readonly result: RuntimeMutationResult;
}

export interface ApplyAuthoringMutationOptions {
  readonly adapter?: RuntimeMutationBridgeAdapter;
  readonly maxFeedbackItems?: number;
}

export function createInitialWorkbenchStateV2(initialDocument: SceneDocument, mode: AuthoringMode = "safe"): AuthoringWorkbenchStateV2 {
  const selection = createSelectionState(initialDocument.scene.id, mode);
  const adapter = createInMemoryPreviewAdapter();
  return {
    mode,
    documents: {
      baseline: adapter.snapshot(initialDocument),
      draft: adapter.snapshot(initialDocument),
      preview: adapter.snapshot(initialDocument),
    },
    selection,
    runtimeObserved: adapter.observe(initialDocument, selection.primaryTarget),
    feedback: [],
  };
}

export function setWorkbenchSelection(
  previous: AuthoringWorkbenchStateV2,
  target: SelectionTarget | null,
  sourceSurface: SelectionSurface
): AuthoringWorkbenchStateV2 {
  const nextSelection = {
    ...previous.selection,
    primaryTarget: target,
    sourceSurface,
    mode: previous.mode,
    lastUpdatedAtIso: new Date().toISOString(),
  };
  const adapter = createInMemoryPreviewAdapter();
  return {
    ...previous,
    selection: nextSelection,
    runtimeObserved: adapter.observe(previous.documents.preview, nextSelection.primaryTarget),
  };
}

export function applyAuthoringMutation(
  state: AuthoringWorkbenchStateV2,
  command: RuntimeMutationCommand,
  options: ApplyAuthoringMutationOptions = {}
): MutationClientOutcome {
  const adapter = options.adapter ?? createInMemoryPreviewAdapter();
  const result = applyRuntimeMutationThroughBridge(
    {
      baseline: state.documents.baseline,
      draft: state.documents.draft,
      currentSelection: state.selection.primaryTarget,
    },
    command,
    adapter
  );

  const reconciledSelection = reconcileSelectionState(result.preview, {
    ...state.selection,
    mode: state.mode,
  });

  const nextState: AuthoringWorkbenchStateV2 = {
    ...state,
    documents: {
      baseline: result.baseline,
      draft: result.draft,
      preview: result.preview,
    },
    selection: reconciledSelection,
    runtimeObserved: adapter.observe(result.preview, reconciledSelection.primaryTarget),
    feedback: [result.feedback, ...state.feedback].slice(0, options.maxFeedbackItems ?? 10),
  };

  return {
    state: nextState,
    result,
  };
}
