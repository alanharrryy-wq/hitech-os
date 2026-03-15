import type {
  AuthoringMode,
  AuthoringOperation,
  SceneDocument,
  SelectionState,
  SelectionSurface,
  SelectionTarget,
} from "../authoring-workbench-contracts";

export function createSelectionState(sceneId: string, mode: AuthoringMode = "safe"): SelectionState {
  return {
    primaryTarget: {
      kind: "scene",
      id: sceneId,
      sceneId,
    },
    sourceSurface: "system",
    mode,
    lastUpdatedAtIso: new Date().toISOString(),
  };
}

export function setSelection(
  previous: SelectionState,
  target: SelectionTarget | null,
  sourceSurface: SelectionSurface,
  mode: AuthoringMode = previous.mode
): SelectionState {
  return {
    primaryTarget: target,
    sourceSurface,
    mode,
    lastUpdatedAtIso: new Date().toISOString(),
  };
}

export function isSelectionTargetEqual(left: SelectionTarget | null, right: SelectionTarget | null): boolean {
  if (left === right) {
    return true;
  }
  if (!left || !right) {
    return false;
  }
  return left.kind === right.kind && left.id === right.id && left.sceneId === right.sceneId;
}

export function deriveLegalOperations(target: SelectionTarget | null, document: SceneDocument, mode: AuthoringMode): readonly AuthoringOperation[] {
  const always: AuthoringOperation[] = ["draft.commit", "draft.discard"];
  if (!target) {
    return always;
  }
  if (target.kind === "scene") {
    return ["scene-look.update", ...always];
  }
  if (target.kind === "layout-node") {
    const node = document.layoutNodes[target.id];
    if (!node || node.locked || node.kind === "root") {
      return ["selection.reset", ...always];
    }
    return ["layout.move", "layout.resize", "layout.reorder", "selection.reset", ...always];
  }
  if (target.kind === "slot") {
    const slot = document.slots[target.id];
    if (!slot || slot.locked) {
      return ["selection.reset", ...always];
    }
    return ["widget.insert-from-prefab", "selection.reset", ...always];
  }
  const widget = document.widgets[target.id];
  if (!widget || widget.locked) {
    return ["selection.reset", ...always];
  }
  const base: AuthoringOperation[] = ["widget.update-props", "widget.update-style", "widget.remove", "selection.reset", ...always];
  if (mode === "advanced" && widget.type === "container") {
    return ["layout.move", ...base];
  }
  return base;
}

export function selectionExistsInDocument(document: SceneDocument, selection: SelectionTarget | null): boolean {
  if (!selection) {
    return false;
  }
  if (selection.kind === "scene") {
    return selection.id === document.scene.id;
  }
  if (selection.kind === "layout-node") {
    return Boolean(document.layoutNodes[selection.id]);
  }
  if (selection.kind === "slot") {
    return Boolean(document.slots[selection.id]);
  }
  return Boolean(document.widgets[selection.id]);
}

export function reconcileSelectionAfterMutation(document: SceneDocument, selection: SelectionState): SelectionState {
  if (selectionExistsInDocument(document, selection.primaryTarget)) {
    return selection;
  }
  return createSelectionState(document.scene.id, selection.mode);
}
