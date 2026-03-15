import { createContext, useContext, useMemo, useReducer } from "react";
import type { AuthoringMode, PrefabDefinition, SelectionTarget, WidgetPropsPatch, WidgetStylePatch } from "./authoring-workbench-contracts";
import { deriveInspectorTarget } from "./selection/inspector-target";
import { deriveLegalOperations } from "./selection/selection-model";
import { createComposerModuleRegistry } from "./composer-module-registry";
import { createInitialWorkbenchState, deriveDirtyState, workbenchReducer } from "./state/workbench-store";
import {
  createCommitDraftCommand,
  createDiscardDraftCommand,
  createInsertWidgetCommand,
  createLayoutMoveCommand,
  createLayoutReorderCommand,
  createLayoutResizeCommand,
  createRemoveWidgetCommand,
  createResetSelectionCommand,
  createSceneLookUpdateCommand,
  createUpdateWidgetPropsCommand,
  createUpdateWidgetStyleCommand,
} from "../../runtime-mutation-bridge/authoring-workbench-v1/contract";
import type { SceneDocument, SceneLookModelPatch } from "./authoring-workbench-contracts";

export interface LiveSceneComposerContextValue {
  readonly state: ReturnType<typeof createInitialWorkbenchState>;
  readonly dirty: boolean;
  readonly inspectorTarget: ReturnType<typeof deriveInspectorTarget>;
  readonly legalOperations: readonly string[];
  readonly modules: ReturnType<typeof createComposerModuleRegistry>["descriptors"];
  setMode(mode: AuthoringMode): void;
  select(target: SelectionTarget | null, sourceSurface: "canvas" | "structure" | "inspector" | "system"): void;
  previewSceneLook(patch: SceneLookModelPatch): void;
  moveLayoutNode(target: SelectionTarget, deltaX: number, deltaY: number): void;
  resizeLayoutNode(target: SelectionTarget, widthDelta: number, heightDelta: number): void;
  reorderLayoutNode(target: SelectionTarget, toIndex: number): void;
  insertWidgetFromPrefab(slotTarget: SelectionTarget, prefab: PrefabDefinition): void;
  updateWidgetProps(target: SelectionTarget, patch: WidgetPropsPatch): void;
  updateWidgetStyle(target: SelectionTarget, patch: WidgetStylePatch): void;
  removeWidget(target: SelectionTarget): void;
  resetSelectedElement(): void;
  commitDraft(): void;
  discardDraft(): void;
  clearFeedback(): void;
}

const LiveSceneComposerContext = createContext<LiveSceneComposerContextValue | null>(null);

export interface LiveSceneComposerProviderProps {
  readonly initialDocument?: SceneDocument;
  readonly children: any;
}

export function LiveSceneComposerProvider({ initialDocument, children }: LiveSceneComposerProviderProps): any {
  const registry = useMemo(() => createComposerModuleRegistry(), []);
  const [state, dispatch] = useReducer(workbenchReducer, createInitialWorkbenchState(initialDocument, "safe", registry.descriptors));
  const inspectorTarget = useMemo(
    () => deriveInspectorTarget(state.documents.preview, state.selection.primaryTarget),
    [state.documents.preview, state.selection.primaryTarget]
  );
  const legalOperations = useMemo(
    () => deriveLegalOperations(state.selection.primaryTarget, state.documents.preview, state.mode),
    [state.selection.primaryTarget, state.documents.preview, state.mode]
  );

  const value: LiveSceneComposerContextValue = {
    state,
    dirty: deriveDirtyState(state),
    inspectorTarget,
    legalOperations,
    modules: registry.descriptors,
    setMode(mode) {
      dispatch({ type: "mode.set", mode });
    },
    select(target, sourceSurface) {
      dispatch({ type: "selection.set", target, sourceSurface });
    },
    previewSceneLook(patch) {
      dispatch({
        type: "mutation.apply",
        command: createSceneLookUpdateCommand({ kind: "scene", id: state.documents.preview.scene.id, sceneId: state.documents.preview.scene.id }, patch, "preview-only", state.mode),
      });
    },
    moveLayoutNode(target, deltaX, deltaY) {
      dispatch({ type: "mutation.apply", command: createLayoutMoveCommand(target, deltaX, deltaY, state.mode) });
    },
    resizeLayoutNode(target, widthDelta, heightDelta) {
      dispatch({ type: "mutation.apply", command: createLayoutResizeCommand(target, widthDelta, heightDelta, state.mode) });
    },
    reorderLayoutNode(target, toIndex) {
      dispatch({ type: "mutation.apply", command: createLayoutReorderCommand(target, toIndex, state.mode) });
    },
    insertWidgetFromPrefab(slotTarget, prefab) {
      dispatch({ type: "mutation.apply", command: createInsertWidgetCommand(slotTarget, slotTarget.id, prefab, state.mode) });
    },
    updateWidgetProps(target, patch) {
      dispatch({ type: "mutation.apply", command: createUpdateWidgetPropsCommand(target, patch, state.mode) });
    },
    updateWidgetStyle(target, patch) {
      dispatch({ type: "mutation.apply", command: createUpdateWidgetStyleCommand(target, patch, state.mode) });
    },
    removeWidget(target) {
      dispatch({ type: "mutation.apply", command: createRemoveWidgetCommand(target, target.id, state.mode) });
    },
    resetSelectedElement() {
      const currentTarget = state.selection.primaryTarget;
      if (!currentTarget) {
        return;
      }
      dispatch({
        type: "mutation.apply",
        command: createResetSelectionCommand(currentTarget, state.documents.baseline.scene.id, state.mode),
      });
    },
    commitDraft() {
      dispatch({ type: "mutation.apply", command: createCommitDraftCommand(state.documents.preview.scene.id, state.mode) });
    },
    discardDraft() {
      dispatch({ type: "mutation.apply", command: createDiscardDraftCommand(state.documents.preview.scene.id, state.mode) });
    },
    clearFeedback() {
      dispatch({ type: "feedback.clear" });
    },
  };

  return <LiveSceneComposerContext.Provider value={value}>{children}</LiveSceneComposerContext.Provider>;
}

export function useLiveSceneComposer(): LiveSceneComposerContextValue {
  const context = useContext(LiveSceneComposerContext);
  if (!context) {
    throw new Error("LiveSceneComposerProvider is required before using workbench context.");
  }
  return context;
}
