import {
  applyRuntimeMutationThroughBridge,
  createCommitDraftCommand as createCommitDraftCommandV2,
  createDiscardDraftCommand as createDiscardDraftCommandV2,
  createInMemoryPreviewAdapter,
  createInsertWidgetCommand as createInsertWidgetCommandV2,
  createLayoutMoveCommand as createLayoutMoveCommandV2,
  createLayoutReorderCommand as createLayoutReorderCommandV2,
  createLayoutResizeCommand as createLayoutResizeCommandV2,
  createRemoveWidgetCommand as createRemoveWidgetCommandV2,
  createResetSelectionCommand as createResetSelectionCommandV2,
  createSceneLookUpdateCommand as createSceneLookUpdateCommandV2,
  createUpdateWidgetPropsCommand as createUpdateWidgetPropsCommandV2,
  createUpdateWidgetStyleCommand as createUpdateWidgetStyleCommandV2,
  type CommitDraftCommand,
  type DiscardDraftCommand,
  type InsertWidgetFromPrefabCommand,
  type LayoutMoveCommand,
  type LayoutReorderCommand,
  type LayoutResizeCommand,
  type RemoveWidgetCommand,
  type ResetSelectedElementCommand,
  type RuntimeMutationBridgeAdapter,
  type RuntimeMutationCommand,
  type RuntimeMutationResult,
  type RuntimeMutationTarget,
  type SceneLookUpdateCommand,
  type UpdateWidgetPropsCommand,
  type UpdateWidgetStyleCommand,
} from "../../../runtime-mutation-bridge/core-v2";
import type {
  AuthoringMode,
  AuthoringWorkbenchState,
  PrefabDefinition,
  SceneId,
  SceneLookModelPatch,
  WidgetPropsPatch,
  WidgetStylePatch,
} from "../authoring-workbench-contracts";
import { createRuntimeObservationFromDocument } from "../runtime/runtime-observation";
import { reconcileSelectionAfterMutation } from "../selection/selection-model";

export type {
  CommitDraftCommand,
  DiscardDraftCommand,
  InsertWidgetFromPrefabCommand,
  LayoutMoveCommand,
  LayoutReorderCommand,
  LayoutResizeCommand,
  RemoveWidgetCommand,
  ResetSelectedElementCommand,
  RuntimeMutationBridgeAdapter,
  RuntimeMutationCommand,
  RuntimeMutationResult,
  RuntimeMutationTarget,
  SceneLookUpdateCommand,
  UpdateWidgetPropsCommand,
  UpdateWidgetStyleCommand,
};

export interface MutationClientOutcome {
  readonly state: AuthoringWorkbenchState;
  readonly result: RuntimeMutationResult;
}

export function createSceneLookUpdateCommand(
  target: RuntimeMutationTarget,
  patch: SceneLookModelPatch,
  scope: "preview-only" | "commit-capable" | "accepted-state-transition" | "local-reset" | "full-draft-discard",
  mode: AuthoringMode
): SceneLookUpdateCommand {
  return createSceneLookUpdateCommandV2(target, patch, mode, scope);
}

export function createLayoutMoveCommand(target: RuntimeMutationTarget, deltaX: number, deltaY: number, mode: AuthoringMode): LayoutMoveCommand {
  return createLayoutMoveCommandV2(target, deltaX, deltaY, mode);
}

export function createLayoutResizeCommand(
  target: RuntimeMutationTarget,
  widthDelta: number,
  heightDelta: number,
  mode: AuthoringMode
): LayoutResizeCommand {
  return createLayoutResizeCommandV2(target, widthDelta, heightDelta, mode);
}

export function createLayoutReorderCommand(target: RuntimeMutationTarget, toIndex: number, mode: AuthoringMode): LayoutReorderCommand {
  return createLayoutReorderCommandV2(target, toIndex, mode);
}

export function createInsertWidgetCommand(
  target: RuntimeMutationTarget,
  slotId: string,
  prefab: PrefabDefinition,
  mode: AuthoringMode
): InsertWidgetFromPrefabCommand {
  return createInsertWidgetCommandV2(target, slotId, prefab, mode);
}

export function createUpdateWidgetPropsCommand(
  target: RuntimeMutationTarget,
  patch: WidgetPropsPatch,
  mode: AuthoringMode
): UpdateWidgetPropsCommand {
  return createUpdateWidgetPropsCommandV2(target, patch, mode);
}

export function createUpdateWidgetStyleCommand(
  target: RuntimeMutationTarget,
  patch: WidgetStylePatch,
  mode: AuthoringMode
): UpdateWidgetStyleCommand {
  return createUpdateWidgetStyleCommandV2(target, patch, mode);
}

export function createRemoveWidgetCommand(target: RuntimeMutationTarget, widgetId: string, mode: AuthoringMode): RemoveWidgetCommand {
  return createRemoveWidgetCommandV2(target, widgetId, mode);
}

export function createResetSelectionCommand(
  target: RuntimeMutationTarget,
  baselineSceneId: SceneId,
  mode: AuthoringMode
): ResetSelectedElementCommand {
  return createResetSelectionCommandV2(target, baselineSceneId, mode);
}

export function createCommitDraftCommand(sceneId: SceneId, mode: AuthoringMode): CommitDraftCommand {
  return createCommitDraftCommandV2(sceneId, mode);
}

export function createDiscardDraftCommand(sceneId: SceneId, mode: AuthoringMode): DiscardDraftCommand {
  return createDiscardDraftCommandV2(sceneId, mode);
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

  const reconciledSelection = reconcileSelectionAfterMutation(result.preview, {
    ...state.selection,
    mode: state.mode,
  });

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
