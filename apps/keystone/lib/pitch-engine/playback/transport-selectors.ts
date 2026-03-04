import type { TransportState } from "./transport-reducer.js";

export function selectTransportProgress(state: TransportState): number {
  if (state.durationMs <= 0) {
    return 0;
  }

  return Math.min(Math.max(state.positionMs / state.durationMs, 0), 1);
}

export function selectTransportRemainingMs(state: TransportState): number {
  return Math.max(0, state.durationMs - state.positionMs);
}

export function selectTransportIsPlaying(state: TransportState): boolean {
  return state.status === "playing";
}

export function selectCurrentStepIndex(state: TransportState): number {
  return state.currentStepIndex;
}

export function selectCurrentStepLabel(state: TransportState): string {
  return `step-${state.currentStepIndex + 1}`;
}

export function selectCanPlay(state: TransportState): boolean {
  return state.durationMs > 0 && state.status !== "playing";
}

export function selectCanPause(state: TransportState): boolean {
  return state.status === "playing";
}
