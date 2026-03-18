import {
  type MutationEnvelope,
  type MutationTarget,
  type ValidationIssue,
  type ValidationResult
} from "./contracts";
import { checkModePolicy } from "./mode-policy";

export interface ValidationContext {
  readonly existingSceneIds?: readonly string[];
  readonly existingLayoutNodeIds?: readonly string[];
  readonly existingSlotIds?: readonly string[];
  readonly existingWidgetIds?: readonly string[];
  readonly activePreviewSessionIds?: readonly string[];
  readonly staleRevisionIds?: readonly string[];
}

function targetExists(target: MutationTarget, context: ValidationContext): boolean {
  switch (target.kind) {
    case "scene":
      return context.existingSceneIds?.includes(target.sceneId) ?? true;
    case "layout-node":
      return context.existingLayoutNodeIds?.includes(target.layoutNodeId) ?? true;
    case "slot":
      return context.existingSlotIds?.includes(target.slotId) ?? true;
    case "widget":
      return context.existingWidgetIds?.includes(target.widgetId) ?? true;
    case "draft":
      return true;
  }
}

export function validateMutationEnvelope(envelope: MutationEnvelope, context: ValidationContext = {}): ValidationResult {
  const issues: ValidationIssue[] = [];

  if (!envelope.target) {
    issues.push({ code: "missing-target", message: "Mutation target is required.", severity: "error" });
  }

  if (envelope.scope === "accepted-state-transition" && !envelope.previewSessionId) {
    issues.push({ code: "preview-lineage-required", message: "Accepted-state transition requires previewSessionId.", severity: "error" });
  }

  if (!envelope.payload && envelope.type !== "draft-discard" && envelope.type !== "draft-commit" && envelope.type !== "selected-element-reset") {
    issues.push({ code: "missing-payload", message: "Mutation payload is required for the selected mutation type.", severity: "error" });
  }

  if (envelope.target && !targetExists(envelope.target, context)) {
    issues.push({ code: "missing-target", message: "Mutation target does not exist in the provided validation context.", severity: "error" });
  }

  if (
    envelope.previewSessionId &&
    context.activePreviewSessionIds &&
    !context.activePreviewSessionIds.includes(envelope.previewSessionId)
  ) {
    issues.push({
      code: "preview-lineage-required",
      message: "Referenced preview session is not active in the validation context.",
      severity: "error"
    });
  }

  if (context.staleRevisionIds?.includes(envelope.requestTimestampUtc.slice(0, 10))) {
    issues.push({
      code: "stale-revision",
      message: "Validation context flagged the request as stale by revision/date bucket.",
      severity: "warning"
    });
  }

  issues.push(...checkModePolicy(envelope));
  return { ok: !issues.some((issue) => issue.severity === "error"), issues };
}
