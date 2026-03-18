import type { SelectionContext } from "./contracts";

export interface SurfaceFocusModel {
  readonly canvasFocusKey: string;
  readonly structureFocusKey: string;
  readonly inspectorFocusKey: string;
}

export function buildSurfaceFocusModel(context: SelectionContext): SurfaceFocusModel {
  const key = `${context.selection.kind}:${context.selection.selectionId}`;
  return {
    canvasFocusKey: `canvas:${key}`,
    structureFocusKey: `structure:${key}`,
    inspectorFocusKey: `inspector:${context.inspectorTarget.targetPanel}:${context.inspectorTarget.sectionKey}`
  };
}
