import { type VerificationCheck } from "./contracts";

export function buildVerificationPlan(): readonly VerificationCheck[] {
  return [
    {
      id: "docs-root",
      title: "Canonical docs root exists",
      status: "skipped",
      severity: "info",
      details: "Evaluated by PowerShell verifier at install time."
    },
    {
      id: "staging-root",
      title: "Staging root exists",
      status: "skipped",
      severity: "info",
      details: "Evaluated by PowerShell verifier at install time."
    },
    {
      id: "mutation-entrypoints",
      title: "Mutation entrypoints present",
      status: "skipped",
      severity: "info",
      details: "Evaluated by structural smoke checks."
    }
  ];
}
