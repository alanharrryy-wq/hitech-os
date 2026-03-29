import type { SelectionContext, SurfaceActionEnvelope } from "./contracts";

function targetFromContext(context: SelectionContext): SurfaceActionEnvelope["target"] {
  switch (context.selection.kind) {
    case "widget":
      return { kind: "widget", sceneId: context.selection.sceneId, widgetId: context.selection.widgetId ?? context.selection.selectionId, slotId: context.selection.slotId };
    case "layout-node":
      return { kind: "layout-node", sceneId: context.selection.sceneId, layoutNodeId: context.selection.layoutNodeId ?? context.selection.selectionId };
    default:
      return { kind: "scene", sceneId: context.selection.sceneId };
  }
}

export function createInspectorWidgetPropsAction(context: SelectionContext, propsPatch: Readonly<Record<string, unknown>>): SurfaceActionEnvelope {
  return {
    actionId: `inspector-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "inspector",
    type: "inspector-update-widget-props",
    context,
    target: targetFromContext(context),
    payload: { propsPatch, section: context.inspectorTarget.sectionKey },
    previewPreferred: true,
    requestedAtUtc: new Date().toISOString(),
    tags: ["inspector", "props"]
  };
}

export function createInspectorWidgetStyleAction(context: SelectionContext, stylePatch: Readonly<Record<string, unknown>>): SurfaceActionEnvelope {
  return {
    actionId: `inspector-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "inspector",
    type: "inspector-update-widget-style",
    context,
    target: targetFromContext(context),
    payload: { stylePatch, section: context.inspectorTarget.sectionKey },
    previewPreferred: true,
    requestedAtUtc: new Date().toISOString(),
    tags: ["inspector", "style"]
  };
}

export function createInspectorSceneLookAction(context: SelectionContext, scenePatch: Readonly<Record<string, unknown>>): SurfaceActionEnvelope {
  return {
    actionId: `inspector-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "inspector",
    type: "inspector-update-scene-look",
    context,
    target: { kind: "scene", sceneId: context.selection.sceneId },
    payload: { scenePatch, section: "scene-look" },
    previewPreferred: true,
    requestedAtUtc: new Date().toISOString(),
    tags: ["inspector", "scene-look"]
  };
}
