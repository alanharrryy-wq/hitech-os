import type {
  AuthoringMode,
  PrefabDefinition,
  SceneId,
  SceneLookModelPatch,
  SelectionTarget,
  WidgetPropsPatch,
  WidgetStylePatch,
} from "./scene-domain";

export const AUTHORING_WORKBENCH_V2_MUTATION_SOURCE = "live-scene-composer.authoring-workbench-v2" as const;

export type MutationSource = typeof AUTHORING_WORKBENCH_V2_MUTATION_SOURCE;
export type MutationScope =
  | "preview-only"
  | "commit-capable"
  | "accepted-state-transition"
  | "local-reset"
  | "full-draft-discard";

export interface DraftMutationTarget {
  readonly kind: "draft";
  readonly id: "draft";
  readonly sceneId: SceneId;
}

export type RuntimeMutationTarget = SelectionTarget | DraftMutationTarget;

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

export type RuntimeMutationType = RuntimeMutationCommand["type"];

export function createCommandId(prefix: string): string {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`;
}

export function createDraftMutationTarget(sceneId: SceneId): DraftMutationTarget {
  return {
    kind: "draft",
    id: "draft",
    sceneId,
  };
}

function createCommand<TypeName extends RuntimeMutationType, Payload>(args: {
  readonly prefix: string;
  readonly type: TypeName;
  readonly mode: AuthoringMode;
  readonly scope: MutationScope;
  readonly target: RuntimeMutationTarget;
  readonly payload: Payload;
}): RuntimeMutationCommandBase<TypeName, Payload> {
  return {
    commandId: createCommandId(args.prefix),
    type: args.type,
    source: AUTHORING_WORKBENCH_V2_MUTATION_SOURCE,
    mode: args.mode,
    scope: args.scope,
    target: args.target,
    payload: args.payload,
    requestedAtIso: new Date().toISOString(),
  };
}

export function createSceneLookUpdateCommand(
  target: RuntimeMutationTarget,
  patch: SceneLookModelPatch,
  mode: AuthoringMode,
  scope: MutationScope = "preview-only"
): SceneLookUpdateCommand {
  return createCommand({
    prefix: "scene-look",
    type: "scene.look.update",
    mode,
    scope,
    target,
    payload: { patch },
  });
}

export function createLayoutMoveCommand(target: RuntimeMutationTarget, deltaX: number, deltaY: number, mode: AuthoringMode): LayoutMoveCommand {
  return createCommand({
    prefix: "layout-move",
    type: "layout.node.move",
    mode,
    scope: "preview-only",
    target,
    payload: { deltaX, deltaY },
  });
}

export function createLayoutResizeCommand(
  target: RuntimeMutationTarget,
  widthDelta: number,
  heightDelta: number,
  mode: AuthoringMode
): LayoutResizeCommand {
  return createCommand({
    prefix: "layout-resize",
    type: "layout.node.resize",
    mode,
    scope: "preview-only",
    target,
    payload: { widthDelta, heightDelta },
  });
}

export function createLayoutReorderCommand(target: RuntimeMutationTarget, toIndex: number, mode: AuthoringMode): LayoutReorderCommand {
  return createCommand({
    prefix: "layout-reorder",
    type: "layout.node.reorder",
    mode,
    scope: "commit-capable",
    target,
    payload: { toIndex },
  });
}

export function createInsertWidgetCommand(
  target: RuntimeMutationTarget,
  slotId: string,
  prefab: PrefabDefinition,
  mode: AuthoringMode
): InsertWidgetFromPrefabCommand {
  return createCommand({
    prefix: "widget-insert",
    type: "widget.insert-from-prefab",
    mode,
    scope: "commit-capable",
    target,
    payload: { slotId, prefab },
  });
}

export function createUpdateWidgetPropsCommand(
  target: RuntimeMutationTarget,
  patch: WidgetPropsPatch,
  mode: AuthoringMode
): UpdateWidgetPropsCommand {
  return createCommand({
    prefix: "widget-props",
    type: "widget.update-props",
    mode,
    scope: "preview-only",
    target,
    payload: { patch },
  });
}

export function createUpdateWidgetStyleCommand(
  target: RuntimeMutationTarget,
  patch: WidgetStylePatch,
  mode: AuthoringMode
): UpdateWidgetStyleCommand {
  return createCommand({
    prefix: "widget-style",
    type: "widget.update-style",
    mode,
    scope: "preview-only",
    target,
    payload: { patch },
  });
}

export function createRemoveWidgetCommand(target: RuntimeMutationTarget, widgetId: string, mode: AuthoringMode): RemoveWidgetCommand {
  return createCommand({
    prefix: "widget-remove",
    type: "widget.remove",
    mode,
    scope: "commit-capable",
    target,
    payload: { widgetId },
  });
}

export function createResetSelectionCommand(
  target: RuntimeMutationTarget,
  baselineSceneId: SceneId,
  mode: AuthoringMode
): ResetSelectedElementCommand {
  return createCommand({
    prefix: "selection-reset",
    type: "selection.reset",
    mode,
    scope: "local-reset",
    target,
    payload: { baselineSceneId },
  });
}

export function createCommitDraftCommand(sceneId: SceneId, mode: AuthoringMode, note: string | null = null): CommitDraftCommand {
  return createCommand({
    prefix: "draft-commit",
    type: "draft.commit",
    mode,
    scope: "accepted-state-transition",
    target: createDraftMutationTarget(sceneId),
    payload: { note },
  });
}

export function createDiscardDraftCommand(sceneId: SceneId, mode: AuthoringMode, reason: string | null = null): DiscardDraftCommand {
  return createCommand({
    prefix: "draft-discard",
    type: "draft.discard",
    mode,
    scope: "full-draft-discard",
    target: createDraftMutationTarget(sceneId),
    payload: { reason },
  });
}
