import type { LiveSceneComposerModule } from "../contracts";
import type { SceneLookModel, SceneLookModelPatch } from "../scene-look-model";

export type AuthoringMode = "safe" | "advanced";
export type SelectionSurface = "canvas" | "structure" | "inspector" | "system";
export type TargetKind = "scene" | "layout-node" | "slot" | "widget" | "draft";
export type LayoutNodeKind = "root" | "stack" | "grid" | "container" | "slot-reference";
export type SlotKind = "content" | "metric" | "chart" | "media" | "container" | "custom";
export type WidgetType = "text" | "kpi" | "chart" | "image" | "container";
export type WidgetCapability = "textual" | "metric" | "chart" | "media" | "layout-container";
export type FeedbackLevel = "info" | "success" | "warning" | "error";

export type SceneId = string;
export type LayoutNodeId = string;
export type SlotId = string;
export type WidgetId = string;
export type PrefabId = string;

export interface FrameBox {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface WidgetStyle {
  readonly background: string;
  readonly foreground: string;
  readonly borderStyle: "none" | "solid" | "glass";
  readonly radius: number;
  readonly emphasis: "subtle" | "default" | "strong";
}

export type WidgetStylePatch = Partial<WidgetStyle>;
export type WidgetPropsPatch = Readonly<Record<string, unknown>>;

export interface SceneEntity {
  readonly id: SceneId;
  readonly title: string;
  readonly description: string;
  readonly look: SceneLookModel;
}

export interface LayoutNode {
  readonly id: LayoutNodeId;
  readonly title: string;
  readonly kind: LayoutNodeKind;
  readonly parentId: LayoutNodeId | null;
  readonly childIds: readonly LayoutNodeId[];
  readonly orderIndex: number;
  readonly slotId: SlotId | null;
  readonly frame: FrameBox;
  readonly locked: boolean;
}

export interface SlotEntity {
  readonly id: SlotId;
  readonly title: string;
  readonly kind: SlotKind;
  readonly acceptedWidgetTypes: readonly WidgetType[];
  readonly acceptedCapabilities: readonly WidgetCapability[];
  readonly widgetIds: readonly WidgetId[];
  readonly maxWidgets: number;
  readonly locked: boolean;
}

export interface WidgetEntity {
  readonly id: WidgetId;
  readonly title: string;
  readonly type: WidgetType;
  readonly slotId: SlotId;
  readonly prefabId: PrefabId | null;
  readonly capabilities: readonly WidgetCapability[];
  readonly props: Readonly<Record<string, unknown>>;
  readonly style: WidgetStyle;
  readonly visible: boolean;
  readonly locked: boolean;
}

export interface PrefabDefinition {
  readonly id: PrefabId;
  readonly title: string;
  readonly widgetType: WidgetType;
  readonly acceptedSlotKinds: readonly SlotKind[];
  readonly acceptedCapabilities: readonly WidgetCapability[];
  readonly defaultProps: Readonly<Record<string, unknown>>;
  readonly defaultStyle: WidgetStyle;
  readonly description: string;
  readonly tags: readonly string[];
}

export interface DocumentMeta {
  readonly revision: number;
  readonly nextId: number;
  readonly lastCommittedAtIso: string | null;
}

export interface SceneDocument {
  readonly scene: SceneEntity;
  readonly rootLayoutId: LayoutNodeId;
  readonly layoutNodes: Readonly<Record<LayoutNodeId, LayoutNode>>;
  readonly slots: Readonly<Record<SlotId, SlotEntity>>;
  readonly widgets: Readonly<Record<WidgetId, WidgetEntity>>;
  readonly meta: DocumentMeta;
}

export interface SelectionTarget {
  readonly kind: Exclude<TargetKind, "draft">;
  readonly id: string;
  readonly sceneId: SceneId;
}

export interface SelectionState {
  readonly primaryTarget: SelectionTarget | null;
  readonly sourceSurface: SelectionSurface;
  readonly mode: AuthoringMode;
  readonly lastUpdatedAtIso: string;
}

export interface RuntimeObservedBounds {
  readonly targetKind: Exclude<TargetKind, "draft">;
  readonly targetId: string;
  readonly frame: FrameBox;
}

export interface RuntimeObservationSnapshot {
  readonly sceneId: SceneId;
  readonly bounds: readonly RuntimeObservedBounds[];
  readonly measuredAtIso: string;
}

export interface MutationFeedback {
  readonly commandType: string;
  readonly level: FeedbackLevel;
  readonly message: string;
  readonly code: string;
  readonly changedTargets: readonly string[];
  readonly recordedAtIso: string;
}

export interface AuthoringWorkbenchState {
  readonly mode: AuthoringMode;
  readonly documents: {
    readonly baseline: SceneDocument;
    readonly draft: SceneDocument;
    readonly preview: SceneDocument;
  };
  readonly selection: SelectionState;
  readonly runtimeObserved: RuntimeObservationSnapshot;
  readonly feedback: readonly MutationFeedback[];
  readonly enabledModules: readonly string[];
}

export type AuthoringOperation =
  | "scene-look.update"
  | "layout.move"
  | "layout.resize"
  | "layout.reorder"
  | "widget.insert-from-prefab"
  | "widget.update-props"
  | "widget.update-style"
  | "widget.remove"
  | "selection.reset"
  | "draft.discard"
  | "draft.commit";

export interface AuthoringWorkbenchModuleDescriptor extends LiveSceneComposerModule {
  readonly capabilities: readonly AuthoringOperation[];
  readonly supportedTargets: readonly SelectionTarget["kind"][];
  readonly safeModeCompatible: boolean;
  readonly advancedModeCompatible: boolean;
}

export interface StructureTreeEntry {
  readonly id: string;
  readonly kind: "scene" | "layout-node" | "slot" | "widget";
  readonly title: string;
  readonly depth: number;
  readonly parentId: string | null;
  readonly selectionTarget: SelectionTarget;
  readonly childIds: readonly string[];
}

export interface CanvasBox {
  readonly id: string;
  readonly kind: "layout-node" | "slot" | "widget";
  readonly title: string;
  readonly frame: FrameBox;
  readonly selected: boolean;
  readonly slotId: string | null;
  readonly widgetIds: readonly string[];
}

export interface ResolvedInspectorTarget {
  readonly surface: "scene-look" | "layout-node" | "slot" | "widget" | "none";
  readonly title: string;
  readonly description: string;
  readonly selection: SelectionTarget | null;
  readonly sections: readonly string[];
}

export type { SceneLookModel, SceneLookModelPatch };
