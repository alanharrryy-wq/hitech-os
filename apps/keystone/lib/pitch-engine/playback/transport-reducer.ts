import type { TransportAction } from "./transport-actions.js";

export type TransportStatus = "idle" | "ready" | "playing" | "paused" | "ended";

export interface TransportState {
  readonly status: TransportStatus;
  readonly durationMs: number;
  readonly positionMs: number;
  readonly stepCount: number;
  readonly currentStepIndex: number;
  readonly playbackRate: number;
  readonly loop: boolean;
}

export const TRANSPORT_INITIAL_STATE: TransportState = {
  status: "idle",
  durationMs: 0,
  positionMs: 0,
  stepCount: 1,
  currentStepIndex: 0,
  playbackRate: 1,
  loop: false
};

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

function safeDuration(durationMs: number): number {
  return clamp(Math.floor(durationMs), 0, 120_000);
}

function safeStepCount(stepCount: number): number {
  return clamp(Math.floor(stepCount), 1, 10_000);
}

function safeRate(rate: number): number {
  if (!Number.isFinite(rate)) {
    return 1;
  }

  return clamp(rate, 0.1, 4);
}

function resolveStepIndex(positionMs: number, durationMs: number, stepCount: number): number {
  if (stepCount <= 1 || durationMs <= 0) {
    return 0;
  }

  const segmentMs = durationMs / stepCount;
  if (segmentMs <= 0) {
    return 0;
  }

  return clamp(Math.floor(positionMs / segmentMs), 0, stepCount - 1);
}

function deriveState(
  previous: TransportState,
  updates: Partial<Omit<TransportState, "currentStepIndex">>
): TransportState {
  const durationMs = updates.durationMs ?? previous.durationMs;
  const positionMs = updates.positionMs ?? previous.positionMs;
  const stepCount = updates.stepCount ?? previous.stepCount;
  const status = updates.status ?? previous.status;
  const playbackRate = updates.playbackRate ?? previous.playbackRate;
  const loop = updates.loop ?? previous.loop;

  return {
    status,
    durationMs,
    positionMs,
    stepCount,
    currentStepIndex: resolveStepIndex(positionMs, durationMs, stepCount),
    playbackRate,
    loop
  };
}

export function transportReducer(
  state: TransportState = TRANSPORT_INITIAL_STATE,
  action: TransportAction
): TransportState {
  switch (action.type) {
    case "transport/load": {
      const durationMs = safeDuration(action.payload.durationMs);
      const stepCount = safeStepCount(action.payload.stepCount);
      return deriveState(state, {
        status: "ready",
        durationMs,
        positionMs: 0,
        stepCount
      });
    }

    case "transport/play": {
      if (state.durationMs <= 0) {
        return deriveState(state, {
          status: "ready",
          positionMs: 0
        });
      }

      const status = state.positionMs >= state.durationMs ? "ended" : "playing";
      return deriveState(state, {
        status
      });
    }

    case "transport/pause": {
      if (state.status !== "playing") {
        return state;
      }

      return deriveState(state, {
        status: "paused"
      });
    }

    case "transport/stop": {
      const status: TransportStatus = state.durationMs > 0 ? "ready" : "idle";
      return deriveState(state, {
        status,
        positionMs: 0
      });
    }

    case "transport/seek": {
      const nextPositionMs = clamp(Math.floor(action.payload.positionMs), 0, state.durationMs);
      const nextStatus: TransportStatus =
        nextPositionMs >= state.durationMs && state.durationMs > 0 ? "ended" : state.status;

      return deriveState(state, {
        positionMs: nextPositionMs,
        status: nextStatus
      });
    }

    case "transport/tick": {
      if (state.status !== "playing") {
        return state;
      }

      const deltaMs = Math.max(0, action.payload.deltaMs);
      const nextPosition = state.positionMs + Math.floor(deltaMs * state.playbackRate);

      if (state.durationMs <= 0) {
        return deriveState(state, {
          positionMs: 0,
          status: "ended"
        });
      }

      if (nextPosition < state.durationMs) {
        return deriveState(state, {
          positionMs: nextPosition
        });
      }

      if (state.loop) {
        const wrapped = nextPosition % state.durationMs;
        return deriveState(state, {
          positionMs: wrapped,
          status: "playing"
        });
      }

      return deriveState(state, {
        positionMs: state.durationMs,
        status: "ended"
      });
    }

    case "transport/set-step": {
      const stepIndex = clamp(Math.floor(action.payload.stepIndex), 0, state.stepCount - 1);
      if (state.stepCount <= 1 || state.durationMs <= 0) {
        return deriveState(state, {
          positionMs: 0
        });
      }

      const segment = state.durationMs / state.stepCount;
      return deriveState(state, {
        positionMs: Math.floor(stepIndex * segment)
      });
    }

    case "transport/set-rate": {
      return deriveState(state, {
        playbackRate: safeRate(action.payload.playbackRate)
      });
    }

    case "transport/toggle-loop": {
      const nextLoop =
        typeof action.payload?.loop === "boolean" ? action.payload.loop : !state.loop;

      return deriveState(state, {
        loop: nextLoop
      });
    }

    default: {
      return state;
    }
  }
}
