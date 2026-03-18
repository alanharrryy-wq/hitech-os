
export type SurfaceName = "canvas" | "structure-tree" | "inspector" | "system";
export type EntityKind = "scene" | "layout-node" | "slot" | "widget";
export type SelectionStatus = "none" | "active" | "stale";
export type SelectionOrigin = "canvas" | "structure-tree" | "inspector" | "system";
export type SurfaceEventKind =
  | "canvas-hit"
  | "canvas-clear"
  | "tree-select"
  | "tree-focus-move"
  | "tree-toggle-expand"
  | "revision-replaced"
  | "entity-removed"
  | "explicit-recovery"
  | "sync-refresh";

export interface SceneRef { readonly kind: "scene"; readonly sceneId: string; }
export interface LayoutNodeRef { readonly kind: "layout-node"; readonly sceneId: string; readonly layoutNodeId: string; }
export interface SlotRef { readonly kind: "slot"; readonly sceneId: string; readonly slotId: string; }
export interface WidgetRef { readonly kind: "widget"; readonly sceneId: string; readonly widgetId: string; readonly slotId?: string; }
export type EntityRef = SceneRef | LayoutNodeRef | SlotRef | WidgetRef;

export interface SelectionState {
  readonly status: SelectionStatus;
  readonly ref: EntityRef | null;
  readonly revision: string | null;
  readonly origin: SelectionOrigin | null;
  readonly staleReason?: string;
}

export interface LayoutNodeRecord {
  readonly id: string;
  readonly kind: "root" | "stack" | "grid" | "container" | "slot-ref";
  readonly title: string;
  readonly childLayoutNodeIds: readonly string[];
  readonly slotId?: string;
}

export interface SlotRecord {
  readonly id: string;
  readonly title: string;
  readonly kind: "content" | "chart" | "media" | "container" | "metric" | "custom";
  readonly widgetIds: readonly string[];
  readonly acceptsMultiple: boolean;
}

export interface WidgetRecord {
  readonly id: string;
  readonly title: string;
  readonly widgetType: string;
  readonly slotId: string;
  readonly visible: boolean;
  readonly locked?: boolean;
}

export interface SceneGraphInput {
  readonly sceneId: string;
  readonly sceneTitle: string;
  readonly revision: string;
  readonly rootLayoutNodeId: string;
  readonly layoutNodes: Readonly<Record<string, LayoutNodeRecord>>;
  readonly slots: Readonly<Record<string, SlotRecord>>;
  readonly widgets: Readonly<Record<string, WidgetRecord>>;
}

export interface TreeNodeBadge {
  readonly kind: "selection" | "stale" | "hidden" | "locked" | "kind";
  readonly label: string;
}

export interface StructureTreeNode {
  readonly nodeId: string;
  readonly ref: EntityRef;
  readonly kind: EntityKind | "diagnostic-ghost";
  readonly title: string;
  readonly subtitle?: string;
  readonly badges: readonly TreeNodeBadge[];
  readonly expandedByDefault: boolean;
  readonly children: readonly StructureTreeNode[];
}

export interface StructureTreeProjection {
  readonly sceneId: string;
  readonly revision: string;
  readonly root: StructureTreeNode;
  readonly flatOrder: readonly EntityRef[];
}

export interface BoundsRect {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface ObservedBoundsEntry {
  readonly refKey: string;
  readonly rect: BoundsRect;
  readonly visible: boolean;
}

export interface CanvasOverlay {
  readonly overlayId: string;
  readonly kind: "scene-frame" | "layout-frame" | "slot-frame" | "widget-frame" | "stale-ghost" | "guide";
  readonly label: string;
  readonly rect?: BoundsRect;
  readonly editable: boolean;
  readonly notes: readonly string[];
}

export interface CanvasViewModel {
  readonly selection: SelectionState;
  readonly overlays: readonly CanvasOverlay[];
  readonly emptyState: boolean;
  readonly diagnostics: readonly string[];
}

export interface SurfaceInstruction {
  readonly surface: SurfaceName;
  readonly action: string;
  readonly ref: EntityRef | null;
  readonly notes: readonly string[];
}

export interface MutationIntent {
  readonly source: "live-scene-composer";
  readonly type:
    | "layout-move"
    | "layout-resize"
    | "slot-insert-widget"
    | "widget-style-update"
    | "widget-props-update"
    | "widget-remove"
    | "selected-element-reset";
  readonly scope: "preview-only" | "commit-capable" | "local-reset";
  readonly target: EntityRef;
  readonly payload: Readonly<Record<string, unknown>>;
}

export interface SurfaceEvent {
  readonly kind: SurfaceEventKind;
  readonly origin: SurfaceName;
  readonly ref?: EntityRef;
  readonly revision?: string;
  readonly reason?: string;
  readonly payload?: Readonly<Record<string, unknown>>;
}

export interface CoordinationSnapshot {
  readonly selection: SelectionState;
  readonly tree: StructureTreeProjection;
  readonly canvas: CanvasViewModel;
  readonly instructions: readonly SurfaceInstruction[];
  readonly diagnostics: readonly string[];
}

export interface CoordinationEventRecord {
  readonly kind: SurfaceEventKind;
  readonly origin: SurfaceName;
  readonly beforeStatus: SelectionStatus;
  readonly afterStatus: SelectionStatus;
  readonly atUtc: string;
  readonly notes: readonly string[];
}

export interface SelectionStoreCompat {
  getSnapshot(): { selection: SelectionState };
  select(input: { ref: EntityRef; origin: SelectionOrigin; revision: string; reason?: string }): unknown;
  clear(reason?: string, origin?: SelectionOrigin): unknown;
  markStale(reason: string, revision?: string): unknown;
}

export function refKey(ref: EntityRef): string {
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

export function sceneRef(sceneId: string): SceneRef {
  return { kind: "scene", sceneId };
}

export function layoutNodeRef(sceneId: string, layoutNodeId: string): LayoutNodeRef {
  return { kind: "layout-node", sceneId, layoutNodeId };
}

export function slotRef(sceneId: string, slotId: string): SlotRef {
  return { kind: "slot", sceneId, slotId };
}

export function widgetRef(sceneId: string, widgetId: string, slotId?: string): WidgetRef {
  return { kind: "widget", sceneId, widgetId, slotId };
}
