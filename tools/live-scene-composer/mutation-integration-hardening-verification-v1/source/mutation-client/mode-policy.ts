import { type MutationEnvelope, type MutationType, type ValidationIssue } from "./contracts";

const SAFE_MODE_ALLOWLIST: readonly MutationType[] = [
  "scene-look-update",
  "layout-move",
  "layout-resize",
  "slot-insert-widget",
  "widget-props-update",
  "widget-style-update",
  "widget-remove",
  "draft-discard",
  "draft-commit",
  "selected-element-reset"
];

const ADVANCED_ONLY_TAGS = new Set(["requires-advanced-capability", "cross-scene", "unsafe-bulk"]);

export function checkModePolicy(envelope: MutationEnvelope): readonly ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  if (envelope.mode === "safe" && !SAFE_MODE_ALLOWLIST.includes(envelope.type)) {
    issues.push({
      code: "safe-mode-policy",
      message: `Mutation type ${envelope.type} is not allowed in safe mode.`,
      severity: "error"
    });
  }

  if (envelope.mode === "safe" && envelope.tags?.some((tag) => ADVANCED_ONLY_TAGS.has(tag))) {
    issues.push({
      code: "safe-mode-policy",
      message: "Envelope carries advanced-only tags while requesting safe mode.",
      severity: "error"
    });
  }

  if (envelope.scope === "accepted-state-transition" && envelope.previewSessionId === undefined) {
    issues.push({
      code: "preview-lineage-required",
      message: "Accepted-state transitions require explicit preview lineage.",
      severity: "error"
    });
  }

  return issues;
}

export function summarizeModeAllowance(envelope: MutationEnvelope): string {
  const issues = checkModePolicy(envelope);
  if (issues.length === 0) {
    return `${envelope.mode} mode allows ${envelope.type} for ${envelope.scope}.`;
  }
  return issues.map((issue) => issue.message).join(" ");
}
