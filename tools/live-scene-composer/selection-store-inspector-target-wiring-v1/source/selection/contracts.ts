export type SelectionStatus = "none" | "active" | "stale";
export type SelectionKind = "scene" | "layout-node" | "slot" | "widget";
export type SelectionOrigin = "canvas" | "structure-tree" | "inspector" | "system";
export type SelectionReason =
  | "initial-select"
  | "surface-select"
  | "clear-selection"
  | "entity-removed"
  | "revision-replaced"
  | "explicit-recovery"
  | "fallback-recovery"
  | "scene-unloaded"
  | "manual-reset";

export interface SceneEntityRef {
  readonly kind: "scene";
  readonly sceneId: string;
}

export interface LayoutNodeEntityRef {
  readonly kind: "layout-node";
  readonly sceneId: string;
  readonly layoutNodeId: string;
}

export interface SlotEntityRef {
  readonly kind: "slot";
  readonly sceneId: string;
  readonly slotId: string;
}

export interface WidgetEntityRef {
  readonly kind: "widget";
  readonly sceneId: string;
  readonly widgetId: string;
  readonly slotId?: string;
}

export type SelectionRef = SceneEntityRef | LayoutNodeEntityRef | SlotEntityRef | WidgetEntityRef;

export interface SelectionContext {
  readonly breadcrumb?: readonly string[];
  readonly parentSlotIdHint?: string;
  readonly lastVisiblePathHint?: readonly string[];
  readonly notes?: readonly string[];
}

export interface SelectionNoneState {
  readonly status: "none";
}

export interface SelectionActiveState {
  readonly status: "active";
  readonly kind: SelectionKind;
  readonly ref: SelectionRef;
  readonly origin: SelectionOrigin;
  readonly revision: string;
  readonly context?: SelectionContext;
}

export interface SelectionStaleState {
  readonly status: "stale";
  readonly kind: SelectionKind;
  readonly ref: SelectionRef;
  readonly origin: SelectionOrigin;
  readonly revision: string;
  readonly staleReason: SelectionReason;
  readonly context?: SelectionContext;
}

export type SelectionState = SelectionNoneState | SelectionActiveState | SelectionStaleState;

export interface SelectionTransition {
  readonly version: number;
  readonly previousStatus: SelectionStatus;
  readonly nextStatus: SelectionStatus;
  readonly reason: SelectionReason;
  readonly origin: SelectionOrigin;
  readonly atUtc: string;
}

export interface SelectionStoreSnapshot {
  readonly selection: SelectionState;
  readonly version: number;
  readonly lastTransition: SelectionTransition | null;
  readonly updatedAtUtc: string;
}

export interface SelectionStoreListener {
  (snapshot: SelectionStoreSnapshot): void;
}

export interface SelectionStoreClock {
  nowUtc(): string;
}

export type ModeKind = "safe" | "advanced";

export type InspectorTargetStatus = "empty" | "ready" | "unavailable";
export type InspectorEditorKind =
  | "empty-editor"
  | "scene-editor"
  | "layout-node-editor"
  | "slot-editor"
  | "widget-editor"
  | "unavailable-editor";

export type InspectorPropertyGroupId =
  | "scene-appearance"
  | "scene-metadata"
  | "layout-structure"
  | "layout-spacing"
  | "layout-style"
  | "slot-policy"
  | "slot-occupancy"
  | "slot-compatibility"
  | "widget-content"
  | "widget-style"
  | "widget-visibility"
  | "widget-binding";

export type InspectorActionId =
  | "reset-scene-look"
  | "reset-selected-element"
  | "remove-widget"
  | "reorder-layout-node"
  | "resize-layout-node"
  | "change-slot-policy"
  | "insert-prefab-into-slot"
  | "toggle-widget-visibility";

export interface InspectorCapabilityContext {
  readonly mode: ModeKind;
  readonly editable: boolean;
  readonly removable: boolean;
  readonly resettable: boolean;
  readonly reorderable: boolean;
  readonly resizable: boolean;
  readonly styleEditable: boolean;
  readonly propsEditable: boolean;
  readonly warnings?: readonly string[];
  readonly propertyGroups?: readonly InspectorPropertyGroupId[];
  readonly actions?: readonly InspectorActionId[];
}

export interface InspectorTarget {
  readonly status: InspectorTargetStatus;
  readonly selectionRef: SelectionRef | null;
  readonly editorKind: InspectorEditorKind;
  readonly propertyGroups: readonly InspectorPropertyGroupId[];
  readonly actions: readonly InspectorActionId[];
  readonly capabilities: Readonly<{
    editable: boolean;
    removable: boolean;
    resettable: boolean;
    reorderable: boolean;
    resizable: boolean;
    styleEditable: boolean;
    propsEditable: boolean;
    mode: ModeKind;
  }>;
  readonly presentation: Readonly<{
    title: string;
    subtitle?: string;
    breadcrumb?: readonly string[];
    warnings: readonly string[];
  }>;
}

export type SurfaceName = "canvas" | "structure-tree" | "inspector";

export interface SurfaceSyncInstruction {
  readonly surface: SurfaceName;
  readonly action:
    | "clear"
    | "highlight-scene"
    | "highlight-layout-node"
    | "highlight-slot"
    | "highlight-widget"
    | "show-empty"
    | "show-ready"
    | "show-unavailable";
  readonly ref: SelectionRef | null;
  readonly notes: readonly string[];
}

export interface SurfaceSyncPlan {
  readonly selection: SelectionState;
  readonly instructions: readonly SurfaceSyncInstruction[];
}

export interface SelectionStoreOptions {
  readonly initialSelection?: SelectionState;
  readonly clock?: SelectionStoreClock;
}

export interface SelectionInput {
  readonly ref: SelectionRef;
  readonly origin: SelectionOrigin;
  readonly revision: string;
  readonly context?: SelectionContext;
  readonly reason?: SelectionReason;
}

export interface SelectionRecoveryInput extends SelectionInput {
  readonly recoveryReason: Extract<SelectionReason, "explicit-recovery" | "fallback-recovery">;
}

export function createSceneRef(sceneId: string): SceneEntityRef {
  return { kind: "scene", sceneId };
}

export function createLayoutNodeRef(sceneId: string, layoutNodeId: string): LayoutNodeEntityRef {
  return { kind: "layout-node", sceneId, layoutNodeId };
}

export function createSlotRef(sceneId: string, slotId: string): SlotEntityRef {
  return { kind: "slot", sceneId, slotId };
}

export function createWidgetRef(sceneId: string, widgetId: string, slotId?: string): WidgetEntityRef {
  return { kind: "widget", sceneId, widgetId, slotId };
}

export function createNoSelection(): SelectionNoneState {
  return { status: "none" };
}

export function createActiveSelection(input: SelectionInput): SelectionActiveState {
  return {
    status: "active",
    kind: input.ref.kind,
    ref: input.ref,
    origin: input.origin,
    revision: input.revision,
    context: input.context
  };
}

export function createStaleSelection(
  active: SelectionActiveState | SelectionStaleState,
  staleReason: SelectionReason,
  revision = active.revision
): SelectionStaleState {
  return {
    status: "stale",
    kind: active.kind,
    ref: active.ref,
    origin: active.origin,
    revision,
    staleReason,
    context: active.context
  };
}

export function isActiveSelection(selection: SelectionState): selection is SelectionActiveState {
  return selection.status === "active";
}

export function isStaleSelection(selection: SelectionState): selection is SelectionStaleState {
  return selection.status === "stale";
}

export function assertValidSelectionState(selection: SelectionState): void {
  if (selection.status === "none") {
    return;
  }
  if (selection.kind !== selection.ref.kind) {
    throw new Error(`Selection kind mismatch. state=${selection.kind} ref=${selection.ref.kind}`);
  }
  if (!selection.revision || !selection.origin) {
    throw new Error("Active or stale selection must include revision and origin.");
  }
}

export function selectionRefToKey(ref: SelectionRef): string {
  switch (ref.kind) {
    case "scene":
      return `scene:${ref.sceneId}`;
    case "layout-node":
      return `layout-node:${ref.sceneId}:${ref.layoutNodeId}`;
    case "slot":
      return `slot:${ref.sceneId}:${ref.slotId}`;
    case "widget":
      return `widget:${ref.sceneId}:${ref.widgetId}`;
  }
}
