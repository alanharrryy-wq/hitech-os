import type { SelectionContext } from "./contracts";

export interface OverlayRenderState {
  readonly showBounds: boolean;
  readonly showHandles: boolean;
  readonly highlightStructureRow: boolean;
  readonly activePanel: string;
}

export function buildOverlayRenderState(context: SelectionContext): OverlayRenderState {
  return {
    showBounds: context.selection.kind !== "scene",
    showHandles: context.selection.kind === "layout-node" || context.selection.kind === "widget",
    highlightStructureRow: context.selection.kind !== "scene",
    activePanel: context.inspectorTarget.targetPanel
  };
}
