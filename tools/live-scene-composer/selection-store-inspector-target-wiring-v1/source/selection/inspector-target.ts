import {
  type InspectorActionId,
  type InspectorCapabilityContext,
  type InspectorEditorKind,
  type InspectorPropertyGroupId,
  type InspectorTarget,
  type ModeKind,
  type SelectionRef,
  type SelectionState,
  createNoSelection
} from "./contracts";

const EMPTY_CAPABILITIES = Object.freeze({
  editable: false,
  removable: false,
  resettable: false,
  reorderable: false,
  resizable: false,
  styleEditable: false,
  propsEditable: false,
  mode: "safe" as ModeKind
});

function makePresentation(selectionRef: SelectionRef | null, title: string, warnings: readonly string[], subtitle?: string): InspectorTarget["presentation"] {
  const breadcrumb = !selectionRef
    ? undefined
    : selectionRef.kind === "scene"
      ? [selectionRef.sceneId]
      : selectionRef.kind === "layout-node"
        ? [selectionRef.sceneId, "layout", selectionRef.layoutNodeId]
        : selectionRef.kind === "slot"
          ? [selectionRef.sceneId, "slot", selectionRef.slotId]
          : [selectionRef.sceneId, "widget", selectionRef.widgetId];

  return {
    title,
    subtitle,
    breadcrumb,
    warnings
  };
}

function buildReadyTarget(
  selection: Exclude<SelectionState, { status: "none" }>,
  editorKind: InspectorEditorKind,
  propertyGroups: readonly InspectorPropertyGroupId[],
  actions: readonly InspectorActionId[],
  context: InspectorCapabilityContext,
  title: string,
  subtitle?: string
): InspectorTarget {
  return {
    status: "ready",
    selectionRef: selection.ref,
    editorKind,
    propertyGroups,
    actions,
    capabilities: {
      editable: context.editable,
      removable: context.removable,
      resettable: context.resettable,
      reorderable: context.reorderable,
      resizable: context.resizable,
      styleEditable: context.styleEditable,
      propsEditable: context.propsEditable,
      mode: context.mode
    },
    presentation: makePresentation(selection.ref, title, context.warnings ?? [], subtitle)
  };
}

function groupsForKind(kind: SelectionRef["kind"], context: InspectorCapabilityContext): readonly InspectorPropertyGroupId[] {
  if (context.propertyGroups && context.propertyGroups.length > 0) {
    return context.propertyGroups;
  }

  switch (kind) {
    case "scene":
      return ["scene-appearance", "scene-metadata"];
    case "layout-node":
      return ["layout-structure", "layout-spacing", "layout-style"];
    case "slot":
      return ["slot-policy", "slot-occupancy", "slot-compatibility"];
    case "widget":
      return ["widget-content", "widget-style", "widget-visibility", "widget-binding"];
  }
}

function actionsForKind(kind: SelectionRef["kind"], context: InspectorCapabilityContext): readonly InspectorActionId[] {
  if (context.actions && context.actions.length > 0) {
    return context.actions;
  }

  switch (kind) {
    case "scene":
      return context.resettable ? ["reset-scene-look"] : [];
    case "layout-node":
      return [
        ...(context.reorderable ? ["reorder-layout-node" as const] : []),
        ...(context.resizable ? ["resize-layout-node" as const] : []),
        ...(context.resettable ? ["reset-selected-element" as const] : [])
      ];
    case "slot":
      return [
        ...(context.editable ? ["change-slot-policy" as const] : []),
        ...(context.propsEditable ? ["insert-prefab-into-slot" as const] : [])
      ];
    case "widget":
      return [
        ...(context.removable ? ["remove-widget" as const] : []),
        ...(context.resettable ? ["reset-selected-element" as const] : []),
        ...(context.editable ? ["toggle-widget-visibility" as const] : [])
      ];
  }
}

export function createDefaultCapabilityContext(overrides: Partial<InspectorCapabilityContext> = {}): InspectorCapabilityContext {
  return {
    mode: overrides.mode ?? "safe",
    editable: overrides.editable ?? true,
    removable: overrides.removable ?? false,
    resettable: overrides.resettable ?? false,
    reorderable: overrides.reorderable ?? false,
    resizable: overrides.resizable ?? false,
    styleEditable: overrides.styleEditable ?? false,
    propsEditable: overrides.propsEditable ?? false,
    warnings: overrides.warnings ?? [],
    propertyGroups: overrides.propertyGroups,
    actions: overrides.actions
  };
}

export function deriveInspectorTarget(selection: SelectionState, context: InspectorCapabilityContext = createDefaultCapabilityContext()): InspectorTarget {
  if (selection.status === "none") {
    return {
      status: "empty",
      selectionRef: null,
      editorKind: "empty-editor",
      propertyGroups: [],
      actions: [],
      capabilities: EMPTY_CAPABILITIES,
      presentation: makePresentation(null, "Nothing selected", [])
    };
  }

  if (selection.status === "stale") {
    return {
      status: "unavailable",
      selectionRef: selection.ref,
      editorKind: "unavailable-editor",
      propertyGroups: [],
      actions: [],
      capabilities: {
        ...EMPTY_CAPABILITIES,
        mode: context.mode
      },
      presentation: makePresentation(
        selection.ref,
        "Selected target unavailable",
        [
          ...(context.warnings ?? []),
          `Selection became stale because: ${selection.staleReason}`
        ],
        "Choose a new target or apply an explicit recovery rule."
      )
    };
  }

  const propertyGroups = groupsForKind(selection.ref.kind, context);
  const actions = actionsForKind(selection.ref.kind, context);

  switch (selection.ref.kind) {
    case "scene":
      return buildReadyTarget(selection, "scene-editor", propertyGroups, actions, context, "Scene", "Scene-level appearance and metadata.");
    case "layout-node":
      return buildReadyTarget(selection, "layout-node-editor", propertyGroups, actions, context, "Layout Node", "Structural layout controls.");
    case "slot":
      return buildReadyTarget(selection, "slot-editor", propertyGroups, actions, context, "Slot", "Host policy and insertion context.");
    case "widget":
      return buildReadyTarget(selection, "widget-editor", propertyGroups, actions, context, "Widget", "Widget content, style, and behavior.");
  }
}

export function deriveEmptyInspectorTarget(): InspectorTarget {
  return deriveInspectorTarget(createNoSelection());
}
