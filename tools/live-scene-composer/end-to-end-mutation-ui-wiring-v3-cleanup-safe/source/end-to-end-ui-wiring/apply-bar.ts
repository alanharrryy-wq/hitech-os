import type { PreviewSession } from "../mutation-client/contracts";
import type { ApplyBarState } from "./contracts";
import { buildCompareBadges } from "./preview-compare";

export function buildApplyBarState(session: PreviewSession | undefined): ApplyBarState {
  const badges = buildCompareBadges(session);
  return {
    visible: Boolean(session),
    commitEnabled: Boolean(session?.commitReady),
    discardEnabled: Boolean(session),
    compareEnabled: Boolean(session && session.diffSummary.changeCount >= 0),
    badges,
    activePreviewSessionId: session?.sessionId
  };
}
