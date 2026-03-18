import type { ApplyBarState } from "./contracts";

export interface CommitControlModel {
  readonly canApply: boolean;
  readonly canDiscard: boolean;
  readonly reason?: string;
}

export function deriveCommitControlModel(state: ApplyBarState): CommitControlModel {
  if (!state.visible) {
    return { canApply: false, canDiscard: false, reason: "No active preview session." };
  }
  if (!state.commitEnabled) {
    return { canApply: false, canDiscard: state.discardEnabled, reason: "Preview session is not commit-ready." };
  }
  return { canApply: true, canDiscard: state.discardEnabled };
}
