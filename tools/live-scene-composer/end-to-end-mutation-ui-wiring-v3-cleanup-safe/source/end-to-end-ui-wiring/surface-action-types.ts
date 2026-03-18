import type { SurfaceActionType } from "./contracts";

export const previewFirstActions: readonly SurfaceActionType[] = [
  "canvas-drag-layout-node",
  "canvas-resize-layout-node",
  "structure-reorder-layout-node",
  "structure-move-widget",
  "inspector-update-widget-props",
  "inspector-update-widget-style",
  "inspector-update-scene-look"
];

export const commitActions: readonly SurfaceActionType[] = ["toolbar-commit-draft", "hotkey-commit"];
export const discardActions: readonly SurfaceActionType[] = ["toolbar-discard-draft", "hotkey-discard"];
export const resetActions: readonly SurfaceActionType[] = ["toolbar-reset-selected-element", "hotkey-reset-selected-element"];

export function isPreviewFirstAction(type: SurfaceActionType): boolean {
  return previewFirstActions.includes(type);
}

export function isCommitAction(type: SurfaceActionType): boolean {
  return commitActions.includes(type);
}

export function isDiscardAction(type: SurfaceActionType): boolean {
  return discardActions.includes(type);
}

export function isResetAction(type: SurfaceActionType): boolean {
  return resetActions.includes(type);
}
