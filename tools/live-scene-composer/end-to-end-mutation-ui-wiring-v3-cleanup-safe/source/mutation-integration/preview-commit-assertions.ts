export interface PreviewCommitAssertion {
  readonly id: string;
  readonly statement: string;
}

export const previewCommitAssertions: readonly PreviewCommitAssertion[] = [
  { id: "preview-not-accepted", statement: "Preview must not imply accepted state." },
  { id: "commit-advances-accepted", statement: "Commit advances accepted semantics for the relevant workflow." },
  { id: "discard-preserves-baseline", statement: "Discard preserves baseline integrity." },
  { id: "reset-narrower-than-discard", statement: "Reset remains narrower than full discard when possible." }
];
