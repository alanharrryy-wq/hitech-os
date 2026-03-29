
import { type MutationIntent, type SelectionState } from "./contracts";

export interface MutationCapabilitySummary {
  readonly canMoveLayout: boolean;
  readonly canResizeLayout: boolean;
  readonly canInsertWidget: boolean;
  readonly canEditWidgetProps: boolean;
  readonly canEditWidgetStyle: boolean;
  readonly canRemoveWidget: boolean;
  readonly canResetSelected: boolean;
}

export function summarizeMutationCapabilities(selection: SelectionState): MutationCapabilitySummary {
  if (selection.status !== "active" || !selection.ref) {
    return {
      canMoveLayout: false,
      canResizeLayout: false,
      canInsertWidget: false,
      canEditWidgetProps: false,
      canEditWidgetStyle: false,
      canRemoveWidget: false,
      canResetSelected: false
    };
  }

  return {
    canMoveLayout: selection.ref.kind === "layout-node",
    canResizeLayout: selection.ref.kind === "layout-node",
    canInsertWidget: selection.ref.kind === "slot",
    canEditWidgetProps: selection.ref.kind === "widget",
    canEditWidgetStyle: selection.ref.kind === "widget",
    canRemoveWidget: selection.ref.kind === "widget",
    canResetSelected: selection.ref.kind !== "scene"
  };
}

export function buildMutationIntents(selection: SelectionState): readonly MutationIntent[] {
  if (selection.status !== "active" || !selection.ref) {
    return [];
  }
  switch (selection.ref.kind) {
    case "scene":
      return [];
    case "layout-node":
      return [
        { source: "live-scene-composer", type: "layout-move", scope: "commit-capable", target: selection.ref, payload: { axis: "both" } },
        { source: "live-scene-composer", type: "layout-resize", scope: "preview-only", target: selection.ref, payload: { handles: ["n", "e", "s", "w"] } },
        { source: "live-scene-composer", type: "selected-element-reset", scope: "local-reset", target: selection.ref, payload: {} }
      ];
    case "slot":
      return [
        { source: "live-scene-composer", type: "slot-insert-widget", scope: "commit-capable", target: selection.ref, payload: { strategy: "prefab" } },
        { source: "live-scene-composer", type: "selected-element-reset", scope: "local-reset", target: selection.ref, payload: {} }
      ];
    case "widget":
      return [
        { source: "live-scene-composer", type: "widget-props-update", scope: "commit-capable", target: selection.ref, payload: { fields: ["title", "content"] } },
        { source: "live-scene-composer", type: "widget-style-update", scope: "preview-only", target: selection.ref, payload: { fields: ["color", "typography"] } },
        { source: "live-scene-composer", type: "widget-remove", scope: "commit-capable", target: selection.ref, payload: {} },
        { source: "live-scene-composer", type: "selected-element-reset", scope: "local-reset", target: selection.ref, payload: {} }
      ];
  }
}
