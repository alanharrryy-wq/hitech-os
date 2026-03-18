import type { MutationEnvelope, MutationScope, MutationTarget, MutationType, PreviewSession, MutationMode } from "../mutation-client/contracts";

export type SurfaceId = "canvas" | "structure-tree" | "inspector" | "toolbar" | "hotkeys";

export type SurfaceActionType =
  | "canvas-drag-layout-node"
  | "canvas-resize-layout-node"
  | "structure-reorder-layout-node"
  | "structure-move-widget"
  | "inspector-update-widget-props"
  | "inspector-update-widget-style"
  | "inspector-update-scene-look"
  | "toolbar-commit-draft"
  | "toolbar-discard-draft"
  | "toolbar-reset-selected-element"
  | "hotkey-commit"
  | "hotkey-discard"
  | "hotkey-reset-selected-element";

export type SelectionKind = "scene" | "layout-node" | "slot" | "widget";

export interface SelectionRef {
  readonly kind: SelectionKind;
  readonly sceneId: string;
  readonly layoutNodeId?: string;
  readonly slotId?: string;
  readonly widgetId?: string;
  readonly selectionId: string;
}

export interface InspectorTargetRef {
  readonly targetPanel: "scene" | "layout" | "slot" | "widget";
  readonly sectionKey: string;
  readonly fieldGroup: readonly string[];
}

export interface SelectionContext {
  readonly selection: SelectionRef;
  readonly inspectorTarget: InspectorTargetRef;
  readonly draftRevision: string;
  readonly baselineRevision: string;
  readonly activeMode: MutationMode;
}

export interface SurfaceActionEnvelope {
  readonly actionId: string;
  readonly surface: SurfaceId;
  readonly type: SurfaceActionType;
  readonly context: SelectionContext;
  readonly target: MutationTarget;
  readonly payload: Readonly<Record<string, unknown>>;
  readonly previewPreferred: boolean;
  readonly requestedAtUtc: string;
  readonly commitIntent?: boolean;
  readonly tags?: readonly string[];
}

export interface RoutedMutationPlan {
  readonly uiAction: SurfaceActionEnvelope;
  readonly mutationType: MutationType;
  readonly mutationScope: MutationScope;
  readonly envelope: MutationEnvelope;
  readonly routeAction: "preview" | "commit" | "discard" | "revert";
}

export interface CompareBadge {
  readonly key: string;
  readonly label: string;
  readonly kind: "dirty" | "warning" | "blocked" | "ready";
}

export interface ApplyBarState {
  readonly visible: boolean;
  readonly commitEnabled: boolean;
  readonly discardEnabled: boolean;
  readonly compareEnabled: boolean;
  readonly badges: readonly CompareBadge[];
  readonly activePreviewSessionId?: string;
}

export interface SurfaceDispatchResult {
  readonly accepted: boolean;
  readonly plan: RoutedMutationPlan;
  readonly previewSession?: PreviewSession;
  readonly diagnostics: readonly string[];
}

export interface UiEvidenceEvent {
  readonly eventId: string;
  readonly actionId: string;
  readonly surface: SurfaceId;
  readonly mutationId?: string;
  readonly stage:
    | "selection-context"
    | "ui-action"
    | "intent-built"
    | "validated"
    | "preview-routed"
    | "commit-routed"
    | "discard-routed"
    | "rejected";
  readonly message: string;
  readonly atUtc: string;
}
