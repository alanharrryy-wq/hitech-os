import type { MutationType, MutationSource, MutationScope } from "../mutation-client/contracts";
import { buildMutationEnvelope } from "../mutation-client/mutation-intents";
import type { RoutedMutationPlan, SurfaceActionEnvelope } from "./contracts";
import { isCommitAction, isDiscardAction, isResetAction } from "./surface-action-types";

function mapMutationType(action: SurfaceActionEnvelope): MutationType {
  switch (action.type) {
    case "canvas-drag-layout-node":
      return "layout-move";
    case "canvas-resize-layout-node":
      return "layout-resize";
    case "structure-reorder-layout-node":
      return "layout-move";
    case "structure-move-widget":
      return "slot-insert-widget";
    case "inspector-update-widget-props":
      return "widget-props-update";
    case "inspector-update-widget-style":
      return "widget-style-update";
    case "inspector-update-scene-look":
      return "scene-look-update";
    case "toolbar-commit-draft":
    case "hotkey-commit":
      return "draft-commit";
    case "toolbar-discard-draft":
    case "hotkey-discard":
      return "draft-discard";
    case "toolbar-reset-selected-element":
    case "hotkey-reset-selected-element":
      return "selected-element-reset";
  }
}

function mapSource(action: SurfaceActionEnvelope): MutationSource {
  switch (action.surface) {
    case "canvas":
      return "canvas";
    case "structure-tree":
      return "structure-tree";
    case "inspector":
      return "inspector";
    default:
      return "system";
  }
}

function mapScope(action: SurfaceActionEnvelope): MutationScope {
  if (isCommitAction(action.type)) {
    return "accepted-state-transition";
  }
  if (isDiscardAction(action.type)) {
    return "full-draft-discard";
  }
  if (isResetAction(action.type)) {
    return "local-reset";
  }
  return action.previewPreferred ? "preview-only" : "commit-capable";
}

function mapRouteAction(action: SurfaceActionEnvelope): RoutedMutationPlan["routeAction"] {
  if (isCommitAction(action.type)) { return "commit"; }
  if (isDiscardAction(action.type)) { return "discard"; }
  if (isResetAction(action.type)) { return "revert"; }
  return action.commitIntent ? "commit" : "preview";
}

export function buildRoutedMutationPlan(action: SurfaceActionEnvelope): RoutedMutationPlan {
  const mutationType = mapMutationType(action);
  const mutationScope = mapScope(action);
  const routeAction = mapRouteAction(action);
  const envelope = buildMutationEnvelope({
    source: mapSource(action),
    type: mutationType,
    mode: action.context.activeMode,
    scope: mutationScope,
    target: action.target,
    payload: action.payload,
    previewSessionId: mutationScope === "accepted-state-transition" ? action.context.draftRevision : undefined,
    tags: action.tags ?? [action.surface, action.type]
  });
  return { uiAction: action, mutationType, mutationScope, envelope, routeAction };
}
