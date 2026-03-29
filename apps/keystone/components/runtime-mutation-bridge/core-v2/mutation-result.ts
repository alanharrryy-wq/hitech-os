import type { MutationFeedback, SceneDocument } from "./scene-domain";

export type ValidationIssueCode =
  | "invalid-source"
  | "invalid-target"
  | "invalid-scope"
  | "invalid-command"
  | "missing-entity"
  | "safe-mode-rejected"
  | "slot-incompatible"
  | "slot-capacity-exceeded"
  | "locked-target"
  | "out-of-range"
  | "baseline-missing"
  | "draft-target-required"
  | "payload-invalid";

export interface ValidationIssue {
  readonly code: ValidationIssueCode;
  readonly message: string;
}

export interface ValidationResult {
  readonly accepted: boolean;
  readonly issues: readonly ValidationIssue[];
}

export type BridgePhase = "preview" | "draft-update" | "commit" | "discard" | "rejection";

export interface RuntimeMutationResult {
  readonly accepted: boolean;
  readonly commandId: string;
  readonly commandType: string;
  readonly phase: BridgePhase;
  readonly baseline: SceneDocument;
  readonly draft: SceneDocument;
  readonly preview: SceneDocument;
  readonly feedback: MutationFeedback;
  readonly changedTargets: readonly string[];
  readonly validationIssues: readonly ValidationIssue[];
}

export function createMutationFeedback(
  commandType: string,
  accepted: boolean,
  message: string,
  code: string,
  changedTargets: readonly string[]
): MutationFeedback {
  return {
    commandType,
    level: accepted ? "success" : "error",
    message,
    code,
    changedTargets,
    recordedAtIso: new Date().toISOString(),
  };
}

export function createAcceptedMutationResult(args: {
  readonly commandId: string;
  readonly commandType: string;
  readonly phase: Exclude<BridgePhase, "rejection">;
  readonly baseline: SceneDocument;
  readonly draft: SceneDocument;
  readonly preview: SceneDocument;
  readonly changedTargets: readonly string[];
  readonly message: string;
}): RuntimeMutationResult {
  return {
    accepted: true,
    commandId: args.commandId,
    commandType: args.commandType,
    phase: args.phase,
    baseline: args.baseline,
    draft: args.draft,
    preview: args.preview,
    feedback: createMutationFeedback(args.commandType, true, args.message, "accepted", args.changedTargets),
    changedTargets: args.changedTargets,
    validationIssues: [],
  };
}

export function createRejectedMutationResult(args: {
  readonly commandId: string;
  readonly commandType: string;
  readonly baseline: SceneDocument;
  readonly draft: SceneDocument;
  readonly preview: SceneDocument;
  readonly issues: readonly ValidationIssue[];
}): RuntimeMutationResult {
  const message = args.issues.map((issue) => issue.message).join(" ") || "Mutation rejected.";
  const code = args.issues[0]?.code ?? "rejected";
  return {
    accepted: false,
    commandId: args.commandId,
    commandType: args.commandType,
    phase: "rejection",
    baseline: args.baseline,
    draft: args.draft,
    preview: args.preview,
    feedback: createMutationFeedback(args.commandType, false, message, code, []),
    changedTargets: [],
    validationIssues: args.issues,
  };
}
