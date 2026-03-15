import type {
  AuthoringMode,
  MutationFeedback,
  PrefabDefinition,
  SceneDocument,
  SceneId,
  SceneLookModelPatch,
  SelectionTarget,
  WidgetPropsPatch,
  WidgetStylePatch,
} from "../../live-scene-composer/authoring-workbench-v1/authoring-workbench-contracts";

export const AUTHORING_WORKBENCH_MUTATION_SOURCE = "live-scene-composer.authoring-workbench-v1" as const;
export type MutationSource = typeof AUTHORING_WORKBENCH_MUTATION_SOURCE;
export type MutationScope = "preview-only" | "commit-capable" | "accepted-state-transition" | "local-reset" | "full-draft-discard";
export type RuntimeMutationTarget = SelectionTarget | { readonly kind: "draft"; readonly id: "draft"; readonly sceneId: SceneId };

export type RuntimeMutationCommand =
  | SceneLookUpdateCommand
  | LayoutMoveCommand
  | LayoutResizeCommand
  | LayoutReorderCommand
  | InsertWidgetFromPrefabCommand
  | UpdateWidgetPropsCommand
  | UpdateWidgetStyleCommand
  | RemoveWidgetCommand
  | ResetSelectedElementCommand
  | CommitDraftCommand
  | DiscardDraftCommand;

export interface RuntimeMutationCommandBase<TypeName extends string, Payload> {
  readonly commandId: string;
  readonly type: TypeName;
  readonly source: MutationSource;
  readonly mode: AuthoringMode;
  readonly scope: MutationScope;
  readonly target: RuntimeMutationTarget;
  readonly payload: Payload;
  readonly requestedAtIso: string;
}

export type SceneLookUpdateCommand = RuntimeMutationCommandBase<"scene.look.update", { readonly patch: SceneLookModelPatch }>;
export type LayoutMoveCommand = RuntimeMutationCommandBase<"layout.node.move", { readonly deltaX: number; readonly deltaY: number }>;
export type LayoutResizeCommand = RuntimeMutationCommandBase<"layout.node.resize", { readonly widthDelta: number; readonly heightDelta: number }>;
export type LayoutReorderCommand = RuntimeMutationCommandBase<"layout.node.reorder", { readonly toIndex: number }>;
export type InsertWidgetFromPrefabCommand = RuntimeMutationCommandBase<"widget.insert-from-prefab", { readonly slotId: string; readonly prefab: PrefabDefinition }>;
export type UpdateWidgetPropsCommand = RuntimeMutationCommandBase<"widget.update-props", { readonly patch: WidgetPropsPatch }>;
export type UpdateWidgetStyleCommand = RuntimeMutationCommandBase<"widget.update-style", { readonly patch: WidgetStylePatch }>;
export type RemoveWidgetCommand = RuntimeMutationCommandBase<"widget.remove", { readonly widgetId: string }>;
export type ResetSelectedElementCommand = RuntimeMutationCommandBase<"selection.reset", { readonly baselineSceneId: SceneId }>;
export type CommitDraftCommand = RuntimeMutationCommandBase<"draft.commit", { readonly note: string | null }>;
export type DiscardDraftCommand = RuntimeMutationCommandBase<"draft.discard", { readonly reason: string | null }>;

export interface RuntimeMutationValidationError {
  readonly code:
    | "invalid-source"
    | "invalid-target"
    | "invalid-scope"
    | "missing-entity"
    | "safe-mode-rejected"
    | "slot-incompatible"
    | "slot-capacity-exceeded"
    | "locked-target"
    | "out-of-range"
    | "baseline-missing";
  readonly message: string;
}

export interface RuntimeMutationValidationResult {
  readonly accepted: boolean;
  readonly errors: readonly RuntimeMutationValidationError[];
}

export interface RuntimeMutationExecutionContext {
  readonly baseline: SceneDocument;
  readonly draft: SceneDocument;
  readonly currentSelection: SelectionTarget | null;
}

export interface RuntimeMutationResult {
  readonly accepted: boolean;
  readonly baseline: SceneDocument;
  readonly draft: SceneDocument;
  readonly preview: SceneDocument;
  readonly feedback: MutationFeedback;
  readonly changedTargets: readonly string[];
  readonly validationErrors: readonly RuntimeMutationValidationError[];
}

export function createCommandId(prefix: string): string {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`;
}

export function createSceneLookUpdateCommand(
  target: RuntimeMutationTarget,
  patch: SceneLookModelPatch,
  scope: MutationScope,
  mode: AuthoringMode
): SceneLookUpdateCommand {
  return {
    commandId: createCommandId("scene-look"),
    type: "scene.look.update",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope,
    target,
    payload: { patch },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createLayoutMoveCommand(target: RuntimeMutationTarget, deltaX: number, deltaY: number, mode: AuthoringMode): LayoutMoveCommand {
  return {
    commandId: createCommandId("layout-move"),
    type: "layout.node.move",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "preview-only",
    target,
    payload: { deltaX, deltaY },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createLayoutResizeCommand(target: RuntimeMutationTarget, widthDelta: number, heightDelta: number, mode: AuthoringMode): LayoutResizeCommand {
  return {
    commandId: createCommandId("layout-resize"),
    type: "layout.node.resize",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "preview-only",
    target,
    payload: { widthDelta, heightDelta },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createLayoutReorderCommand(target: RuntimeMutationTarget, toIndex: number, mode: AuthoringMode): LayoutReorderCommand {
  return {
    commandId: createCommandId("layout-reorder"),
    type: "layout.node.reorder",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "commit-capable",
    target,
    payload: { toIndex },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createInsertWidgetCommand(target: RuntimeMutationTarget, slotId: string, prefab: PrefabDefinition, mode: AuthoringMode): InsertWidgetFromPrefabCommand {
  return {
    commandId: createCommandId("widget-insert"),
    type: "widget.insert-from-prefab",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "commit-capable",
    target,
    payload: { slotId, prefab },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createUpdateWidgetPropsCommand(target: RuntimeMutationTarget, patch: WidgetPropsPatch, mode: AuthoringMode): UpdateWidgetPropsCommand {
  return {
    commandId: createCommandId("widget-props"),
    type: "widget.update-props",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "preview-only",
    target,
    payload: { patch },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createUpdateWidgetStyleCommand(target: RuntimeMutationTarget, patch: WidgetStylePatch, mode: AuthoringMode): UpdateWidgetStyleCommand {
  return {
    commandId: createCommandId("widget-style"),
    type: "widget.update-style",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "preview-only",
    target,
    payload: { patch },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createRemoveWidgetCommand(target: RuntimeMutationTarget, widgetId: string, mode: AuthoringMode): RemoveWidgetCommand {
  return {
    commandId: createCommandId("widget-remove"),
    type: "widget.remove",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "commit-capable",
    target,
    payload: { widgetId },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createResetSelectionCommand(target: RuntimeMutationTarget, baselineSceneId: SceneId, mode: AuthoringMode): ResetSelectedElementCommand {
  return {
    commandId: createCommandId("selection-reset"),
    type: "selection.reset",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "local-reset",
    target,
    payload: { baselineSceneId },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createCommitDraftCommand(sceneId: SceneId, mode: AuthoringMode): CommitDraftCommand {
  return {
    commandId: createCommandId("draft-commit"),
    type: "draft.commit",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "accepted-state-transition",
    target: { kind: "draft", id: "draft", sceneId },
    payload: { note: null },
    requestedAtIso: new Date().toISOString(),
  };
}

export function createDiscardDraftCommand(sceneId: SceneId, mode: AuthoringMode): DiscardDraftCommand {
  return {
    commandId: createCommandId("draft-discard"),
    type: "draft.discard",
    source: AUTHORING_WORKBENCH_MUTATION_SOURCE,
    mode,
    scope: "full-draft-discard",
    target: { kind: "draft", id: "draft", sceneId },
    payload: { reason: null },
    requestedAtIso: new Date().toISOString(),
  };
}
