import type { AuthoringMode, AuthoringWorkbenchModuleDescriptor, AuthoringWorkbenchState, RuntimeObservationSnapshot, SceneDocument, SelectionTarget } from "../authoring-workbench-contracts";
import { createSampleSceneDocument } from "../model/sample-scene";
import { isDraftDirty } from "../model/scene-graph";
import { applyWorkbenchMutation } from "../mutations/mutation-client";
import { createRuntimeObservationFromDocument } from "../runtime/runtime-observation";
import { createSelectionState, setSelection } from "../selection/selection-model";
import type { RuntimeMutationCommand } from "../mutations/mutation-client";

export type WorkbenchAction =
  | { readonly type: "selection.set"; readonly target: SelectionTarget | null; readonly sourceSurface: "canvas" | "structure" | "inspector" | "system" }
  | { readonly type: "mode.set"; readonly mode: AuthoringMode }
  | { readonly type: "mutation.apply"; readonly command: RuntimeMutationCommand }
  | { readonly type: "runtime.observation.replace"; readonly snapshot: RuntimeObservationSnapshot }
  | { readonly type: "feedback.clear" };

export function createInitialWorkbenchState(
  initialDocument: SceneDocument = createSampleSceneDocument(),
  mode: AuthoringMode = "safe",
  modules: readonly AuthoringWorkbenchModuleDescriptor[] = []
): AuthoringWorkbenchState {
  const selection = createSelectionState(initialDocument.scene.id, mode);
  return {
    mode,
    documents: {
      baseline: initialDocument,
      draft: JSON.parse(JSON.stringify(initialDocument)) as SceneDocument,
      preview: JSON.parse(JSON.stringify(initialDocument)) as SceneDocument,
    },
    selection,
    runtimeObserved: createRuntimeObservationFromDocument(initialDocument, selection.primaryTarget),
    feedback: [],
    enabledModules: modules.filter((module) => module.enabledByDefault).map((module) => module.id),
  };
}

export function workbenchReducer(state: AuthoringWorkbenchState, action: WorkbenchAction): AuthoringWorkbenchState {
  switch (action.type) {
    case "selection.set":
      return {
        ...state,
        selection: setSelection(state.selection, action.target, action.sourceSurface, state.mode),
      };
    case "mode.set":
      return {
        ...state,
        mode: action.mode,
        selection: {
          ...state.selection,
          mode: action.mode,
        },
      };
    case "mutation.apply":
      return applyWorkbenchMutation(state, action.command).state;
    case "runtime.observation.replace":
      return {
        ...state,
        runtimeObserved: action.snapshot,
      };
    case "feedback.clear":
      return {
        ...state,
        feedback: [],
      };
    default:
      return state;
  }
}

export function deriveDirtyState(state: AuthoringWorkbenchState): boolean {
  return isDraftDirty(state);
}
