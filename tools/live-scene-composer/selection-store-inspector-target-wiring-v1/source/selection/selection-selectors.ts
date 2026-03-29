import {
  type SelectionActiveState,
  type SelectionRef,
  type SelectionState,
  type SelectionStoreSnapshot,
  isActiveSelection,
  selectionRefToKey
} from "./contracts";

export function getActiveSelection(snapshot: SelectionStoreSnapshot): SelectionActiveState | null {
  return isActiveSelection(snapshot.selection) ? snapshot.selection : null;
}

export function getSelectionRef(snapshot: SelectionStoreSnapshot): SelectionRef | null {
  return snapshot.selection.status === "none" ? null : snapshot.selection.ref;
}

export function getSelectionKey(snapshot: SelectionStoreSnapshot): string | null {
  const ref = getSelectionRef(snapshot);
  return ref ? selectionRefToKey(ref) : null;
}

export function matchesSelectionRef(selection: SelectionState, ref: SelectionRef): boolean {
  if (selection.status === "none") {
    return false;
  }
  return selectionRefToKey(selection.ref) === selectionRefToKey(ref);
}

export function selectionBelongsToScene(selection: SelectionState, sceneId: string): boolean {
  if (selection.status === "none") {
    return false;
  }
  return selection.ref.sceneId === sceneId;
}

export function canShowTargetLocalUi(snapshot: SelectionStoreSnapshot, ref: SelectionRef): boolean {
  return snapshot.selection.status === "active" && matchesSelectionRef(snapshot.selection, ref);
}
