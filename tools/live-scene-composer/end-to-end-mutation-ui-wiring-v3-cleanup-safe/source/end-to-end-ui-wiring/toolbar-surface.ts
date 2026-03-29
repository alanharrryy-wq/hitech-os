import type { SelectionContext, SurfaceActionEnvelope } from "./contracts";

function toolbarTarget(context: SelectionContext): SurfaceActionEnvelope["target"] {
  return { kind: "draft", sceneId: context.selection.sceneId, draftRevision: context.draftRevision };
}

export function createToolbarCommitAction(context: SelectionContext): SurfaceActionEnvelope {
  return {
    actionId: `toolbar-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "toolbar",
    type: "toolbar-commit-draft",
    context,
    target: toolbarTarget(context),
    payload: { requestedBy: "toolbar", baselineRevision: context.baselineRevision },
    previewPreferred: false,
    commitIntent: true,
    requestedAtUtc: new Date().toISOString(),
    tags: ["toolbar", "commit"]
  };
}

export function createToolbarDiscardAction(context: SelectionContext): SurfaceActionEnvelope {
  return {
    actionId: `toolbar-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "toolbar",
    type: "toolbar-discard-draft",
    context,
    target: toolbarTarget(context),
    payload: { requestedBy: "toolbar" },
    previewPreferred: false,
    requestedAtUtc: new Date().toISOString(),
    tags: ["toolbar", "discard"]
  };
}

export function createToolbarResetSelectedElementAction(context: SelectionContext): SurfaceActionEnvelope {
  return {
    actionId: `toolbar-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "toolbar",
    type: "toolbar-reset-selected-element",
    context,
    target: toolbarTarget(context),
    payload: { selectedKind: context.selection.kind, selectionId: context.selection.selectionId },
    previewPreferred: false,
    requestedAtUtc: new Date().toISOString(),
    tags: ["toolbar", "reset"]
  };
}
