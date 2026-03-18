export interface UiWiringEvidenceBundle {
  readonly packageName: string;
  readonly generatedAtUtc: string;
  readonly checks: readonly { readonly name: string; readonly status: "passed" | "warning" | "failed"; readonly detail: string }[];
  readonly mirroredPaths: readonly string[];
  readonly typecheckAttempted: boolean;
  readonly typecheckStatus: "passed" | "warning" | "failed";
}
