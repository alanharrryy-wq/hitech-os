import type { SelectionContext, SurfaceActionEnvelope } from "./contracts";

function targetFromContext(context: SelectionContext): SurfaceActionEnvelope["target"] {
  switch (context.selection.kind) {
    case "layout-node":
      return { kind: "layout-node", sceneId: context.selection.sceneId, layoutNodeId: context.selection.layoutNodeId ?? context.selection.selectionId };
    case "slot":
      return { kind: "slot", sceneId: context.selection.sceneId, slotId: context.selection.slotId ?? context.selection.selectionId };
    case "widget":
      return { kind: "widget", sceneId: context.selection.sceneId, widgetId: context.selection.widgetId ?? context.selection.selectionId, slotId: context.selection.slotId };
    default:
      return { kind: "scene", sceneId: context.selection.sceneId };
  }
}

export function createStructureReorderLayoutNodeAction(context: SelectionContext, beforeNodeId: string | null): SurfaceActionEnvelope {
  return {
    actionId: `structure-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "structure-tree",
    type: "structure-reorder-layout-node",
    context,
    target: targetFromContext(context),
    payload: { beforeNodeId, fromSurface: "structure-tree", operation: "reorder" },
    previewPreferred: true,
    requestedAtUtc: new Date().toISOString(),
    tags: ["structure-tree", context.selection.kind]
  };
}

export function createStructureMoveWidgetAction(context: SelectionContext, destinationSlotId: string): SurfaceActionEnvelope {
  return {
    actionId: `structure-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "structure-tree",
    type: "structure-move-widget",
    context,
    target: targetFromContext(context),
    payload: { destinationSlotId, operation: "move-widget", fromSurface: "structure-tree" },
    previewPreferred: true,
    requestedAtUtc: new Date().toISOString(),
    tags: ["structure-tree", "widget-move"]
  };
}
