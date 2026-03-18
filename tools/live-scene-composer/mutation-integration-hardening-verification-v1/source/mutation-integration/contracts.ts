export type VerificationSeverity = "info" | "warn" | "error";

export interface VerificationCheck {
  readonly id: string;
  readonly title: string;
  readonly status: "passed" | "failed" | "skipped";
  readonly severity: VerificationSeverity;
  readonly details: string;
}

export interface VerificationReport {
  readonly packageName: string;
  readonly repoRoot: string;
  readonly downloadsRoot: string;
  readonly docsRoot: string;
  readonly stagingRoot: string;
  readonly mirrorStatus: "mirrored" | "staged-only" | "ambiguous" | "missing" | "not-requested";
  readonly verificationStatus: "passed" | "failed" | "partial";
  readonly smokeStatus: "passed" | "failed" | "skipped";
  readonly guardStatus: "passed" | "failed" | "skipped";
  readonly copiedDocsCount: number;
  readonly stagedFilesCount: number;
  readonly mirroredFilesCount: number;
  readonly checks: readonly VerificationCheck[];
  readonly nextCommands: readonly string[];
}
