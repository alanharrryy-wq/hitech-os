import type { SelectionContext, SurfaceActionEnvelope } from "./contracts";

function baseAction(context: SelectionContext, type: SurfaceActionEnvelope["type"], payload: Readonly<Record<string, unknown>>): SurfaceActionEnvelope {
  return {
    actionId: `canvas-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "canvas",
    type,
    context,
    target: {
      kind: context.selection.kind,
      sceneId: context.selection.sceneId,
      ...(context.selection.kind === "layout-node" ? { layoutNodeId: context.selection.layoutNodeId ?? context.selection.selectionId } : {}),
      ...(context.selection.kind === "slot" ? { slotId: context.selection.slotId ?? context.selection.selectionId } : {}),
      ...(context.selection.kind === "widget" ? { widgetId: context.selection.widgetId ?? context.selection.selectionId, slotId: context.selection.slotId } : {})
    } as SurfaceActionEnvelope["target"],
    payload,
    previewPreferred: true,
    requestedAtUtc: new Date().toISOString(),
    tags: ["canvas", context.selection.kind]
  };
}

export function createCanvasDragLayoutNodeAction(context: SelectionContext, deltaX: number, deltaY: number): SurfaceActionEnvelope {
  return baseAction(context, "canvas-drag-layout-node", { deltaX, deltaY, axis: "free", fromSurface: "canvas" });
}

export function createCanvasResizeLayoutNodeAction(context: SelectionContext, width: number, height: number): SurfaceActionEnvelope {
  return baseAction(context, "canvas-resize-layout-node", { width, height, strategy: "edge-handle", fromSurface: "canvas" });
}
