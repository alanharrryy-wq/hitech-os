export type MutationSource =
  | "canvas"
  | "structure-tree"
  | "inspector"
  | "module"
  | "system";

export type MutationMode = "safe" | "advanced";
export type MutationScope =
  | "preview-only"
  | "commit-capable"
  | "accepted-state-transition"
  | "local-reset"
  | "full-draft-discard";

export type MutationType =
  | "scene-look-update"
  | "layout-move"
  | "layout-resize"
  | "slot-insert-widget"
  | "widget-props-update"
  | "widget-style-update"
  | "widget-remove"
  | "draft-discard"
  | "draft-commit"
  | "selected-element-reset";

export type TargetKind = "scene" | "layout-node" | "slot" | "widget" | "draft";

export interface SceneTarget {
  readonly kind: "scene";
  readonly sceneId: string;
}

export interface LayoutNodeTarget {
  readonly kind: "layout-node";
  readonly sceneId: string;
  readonly layoutNodeId: string;
}

export interface SlotTarget {
  readonly kind: "slot";
  readonly sceneId: string;
  readonly slotId: string;
}

export interface WidgetTarget {
  readonly kind: "widget";
  readonly sceneId: string;
  readonly widgetId: string;
  readonly slotId?: string;
}

export interface DraftTarget {
  readonly kind: "draft";
  readonly sceneId: string;
  readonly draftRevision: string;
}

export type MutationTarget =
  | SceneTarget
  | LayoutNodeTarget
  | SlotTarget
  | WidgetTarget
  | DraftTarget;

export interface ReversibilityMetadata {
  readonly reversible: boolean;
  readonly inverseStrategy?: "patch-inverse" | "snapshot-restore" | "reset-target" | "discard-session";
  readonly notes?: readonly string[];
}

export interface MutationEnvelope {
  readonly mutationId: string;
  readonly source: MutationSource;
  readonly type: MutationType;
  readonly mode: MutationMode;
  readonly scope: MutationScope;
  readonly target: MutationTarget;
  readonly payload: Readonly<Record<string, unknown>>;
  readonly previewSessionId?: string;
  readonly requestTimestampUtc: string;
  readonly reversibility: ReversibilityMetadata;
  readonly tags?: readonly string[];
}

export interface ValidationIssue {
  readonly code:
    | "missing-target"
    | "invalid-scope"
    | "missing-payload"
    | "safe-mode-policy"
    | "stale-revision"
    | "unsupported-target"
    | "unsupported-type"
    | "adapter-unavailable"
    | "preview-lineage-required";
  readonly message: string;
  readonly severity: "warning" | "error";
}

export interface ValidationResult {
  readonly ok: boolean;
  readonly issues: readonly ValidationIssue[];
}

export interface PreviewPatchSummary {
  readonly changedFields: readonly string[];
  readonly changeCount: number;
  readonly addedEntityIds: readonly string[];
  readonly removedEntityIds: readonly string[];
  readonly movedEntityIds: readonly string[];
}

export interface PreviewSession {
  readonly sessionId: string;
  readonly sceneId: string;
  readonly baselineRevision: string;
  readonly draftRevision: string;
  readonly openedAtUtc: string;
  readonly updatedAtUtc: string;
  readonly mutationIds: readonly string[];
  readonly pendingEnvelopes: readonly MutationEnvelope[];
  readonly diffSummary: PreviewPatchSummary;
  readonly warnings: readonly string[];
  readonly commitReady: boolean;
}

export interface BridgeDecision {
  readonly accepted: boolean;
  readonly decisionKind: "preview-approved" | "preview-rejected" | "commit-approved" | "commit-rejected" | "discard-approved" | "revert-approved";
  readonly mutationId: string;
  readonly reason?: string;
  readonly adapterKey?: string;
  readonly diagnostics: readonly string[];
}

export interface BridgeAdapterRequest {
  readonly envelope: MutationEnvelope;
  readonly action: "preview" | "commit" | "discard" | "revert";
}

export interface BridgeAdapterResult {
  readonly accepted: boolean;
  readonly adapterKey: string;
  readonly diagnostics: readonly string[];
  readonly appliedRevision?: string;
}

export interface MutationHistoryEntry {
  readonly mutationId: string;
  readonly sessionId?: string;
  readonly type: MutationType;
  readonly scope: MutationScope;
  readonly targetKey: string;
  readonly decisionKind: BridgeDecision["decisionKind"];
  readonly atUtc: string;
  readonly notes: readonly string[];
}

export interface DiagnosticsEvent {
  readonly eventId: string;
  readonly level: "info" | "warn" | "error";
  readonly category:
    | "intent-built"
    | "validation"
    | "preview-session"
    | "bridge-preview"
    | "bridge-commit"
    | "discard"
    | "revert"
    | "history";
  readonly mutationId?: string;
  readonly sessionId?: string;
  readonly message: string;
  readonly details?: Readonly<Record<string, unknown>>;
  readonly atUtc: string;
}

export interface MutationClientClock {
  nowUtc(): string;
  nextId(prefix: string): string;
}

export interface PreviewDiffInput {
  readonly baseline: Readonly<Record<string, unknown>>;
  readonly draft: Readonly<Record<string, unknown>>;
  readonly staged: Readonly<Record<string, unknown>>;
}

export function targetKey(target: MutationTarget): string {
  switch (target.kind) {
    case "scene":
      return `scene:${target.sceneId}`;
    case "layout-node":
      return `layout-node:${target.sceneId}:${target.layoutNodeId}`;
    case "slot":
      return `slot:${target.sceneId}:${target.slotId}`;
    case "widget":
      return `widget:${target.sceneId}:${target.widgetId}`;
    case "draft":
      return `draft:${target.sceneId}:${target.draftRevision}`;
  }
}

export function createDefaultClock(seed = Date.now()): MutationClientClock {
  let counter = seed % 1000000;
  return {
    nowUtc: () => new Date().toISOString(),
    nextId(prefix: string) {
      counter += 1;
      return `${prefix}-${counter}`;
    }
  };
}
