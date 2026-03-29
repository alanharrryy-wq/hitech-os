import { type SelectionRef } from "./contracts";

export type MutationSource = "canvas" | "structure-tree" | "inspector" | "system";
export type MutationMode = "safe" | "advanced";
export type MutationScope = "preview" | "commit" | "reset" | "discard";

export type MutationIntent =
  | {
      readonly type: "update-scene-look";
      readonly source: MutationSource;
      readonly mode: MutationMode;
      readonly scope: MutationScope;
      readonly target: Extract<SelectionRef, { kind: "scene" }>;
      readonly patch: Readonly<Record<string, unknown>>;
    }
  | {
      readonly type: "move-layout-node";
      readonly source: MutationSource;
      readonly mode: MutationMode;
      readonly scope: MutationScope;
      readonly target: Extract<SelectionRef, { kind: "layout-node" }>;
      readonly destination: Readonly<{ parentLayoutNodeId: string; index: number }>;
    }
  | {
      readonly type: "change-slot-policy";
      readonly source: MutationSource;
      readonly mode: MutationMode;
      readonly scope: MutationScope;
      readonly target: Extract<SelectionRef, { kind: "slot" }>;
      readonly patch: Readonly<Record<string, unknown>>;
    }
  | {
      readonly type: "update-widget-style";
      readonly source: MutationSource;
      readonly mode: MutationMode;
      readonly scope: MutationScope;
      readonly target: Extract<SelectionRef, { kind: "widget" }>;
      readonly patch: Readonly<Record<string, unknown>>;
    };

export function buildUpdateWidgetStyleIntent(args: {
  readonly target: Extract<SelectionRef, { kind: "widget" }>;
  readonly patch: Readonly<Record<string, unknown>>;
  readonly source?: MutationSource;
  readonly mode?: MutationMode;
  readonly scope?: MutationScope;
}): MutationIntent {
  return {
    type: "update-widget-style",
    source: args.source ?? "inspector",
    mode: args.mode ?? "safe",
    scope: args.scope ?? "preview",
    target: args.target,
    patch: args.patch
  };
}

export function buildUpdateSceneLookIntent(args: {
  readonly target: Extract<SelectionRef, { kind: "scene" }>;
  readonly patch: Readonly<Record<string, unknown>>;
  readonly source?: MutationSource;
  readonly mode?: MutationMode;
  readonly scope?: MutationScope;
}): MutationIntent {
  return {
    type: "update-scene-look",
    source: args.source ?? "inspector",
    mode: args.mode ?? "safe",
    scope: args.scope ?? "preview",
    target: args.target,
    patch: args.patch
  };
}
