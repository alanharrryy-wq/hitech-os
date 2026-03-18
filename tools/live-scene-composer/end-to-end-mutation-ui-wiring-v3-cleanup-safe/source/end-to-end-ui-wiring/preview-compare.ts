import type { PreviewSession } from "../mutation-client/contracts";
import type { CompareBadge } from "./contracts";

export function buildCompareBadges(session: PreviewSession | undefined): readonly CompareBadge[] {
  if (!session) {
    return [{ key: "no-session", label: "No preview session", kind: "blocked" }];
  }
  const badges: CompareBadge[] = [];
  badges.push({ key: "diff-count", label: `Diffs: ${session.diffSummary.changeCount}`, kind: session.diffSummary.changeCount > 0 ? "dirty" : "ready" });
  if (session.warnings.length > 0) {
    badges.push({ key: "warnings", label: `Warnings: ${session.warnings.length}`, kind: "warning" });
  }
  badges.push({ key: "commit-ready", label: session.commitReady ? "Commit ready" : "Commit blocked", kind: session.commitReady ? "ready" : "blocked" });
  return badges;
}
