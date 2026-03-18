import type { MutationMode, MutationTarget } from "../mutation-client/contracts";
import type { SelectionContext, SelectionRef, InspectorTargetRef } from "./contracts";

export interface BuildSelectionContextArgs {
  readonly selection: SelectionRef;
  readonly draftRevision: string;
  readonly baselineRevision: string;
  readonly activeMode: MutationMode;
}

export function deriveInspectorTarget(selection: SelectionRef): InspectorTargetRef {
  switch (selection.kind) {
    case "scene":
      return { targetPanel: "scene", sectionKey: "scene-look", fieldGroup: ["theme", "background", "metadata"] };
    case "layout-node":
      return { targetPanel: "layout", sectionKey: "layout-constraints", fieldGroup: ["position", "size", "order"] };
    case "slot":
      return { targetPanel: "slot", sectionKey: "slot-policy", fieldGroup: ["acceptance", "capacity", "appearance"] };
    case "widget":
      return { targetPanel: "widget", sectionKey: "widget-style", fieldGroup: ["props", "style", "visibility"] };
  }
}

export function selectionToTarget(selection: SelectionRef): MutationTarget {
  switch (selection.kind) {
    case "scene":
      return { kind: "scene", sceneId: selection.sceneId };
    case "layout-node":
      return { kind: "layout-node", sceneId: selection.sceneId, layoutNodeId: selection.layoutNodeId ?? selection.selectionId };
    case "slot":
      return { kind: "slot", sceneId: selection.sceneId, slotId: selection.slotId ?? selection.selectionId };
    case "widget":
      return { kind: "widget", sceneId: selection.sceneId, widgetId: selection.widgetId ?? selection.selectionId, slotId: selection.slotId };
  }
}

export function buildSelectionContext(args: BuildSelectionContextArgs): SelectionContext {
  return {
    selection: args.selection,
    inspectorTarget: deriveInspectorTarget(args.selection),
    draftRevision: args.draftRevision,
    baselineRevision: args.baselineRevision,
    activeMode: args.activeMode
  };
}
