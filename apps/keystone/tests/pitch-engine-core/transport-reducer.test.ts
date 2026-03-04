import { describe, expect, it } from "vitest";
import {
  selectCanPause,
  selectCanPlay,
  selectCurrentStepIndex,
  selectCurrentStepLabel,
  selectTransportIsPlaying,
  selectTransportProgress,
  selectTransportRemainingMs,
  transportActions,
  TRANSPORT_INITIAL_STATE,
  transportReducer,
  type TransportState
} from "../../lib/pitch-engine/index.js";

function reduce(actions: Parameters<typeof transportReducer>[1][]): TransportState {
  return actions.reduce((state, action) => transportReducer(state, action), TRANSPORT_INITIAL_STATE);
}

describe("transport-reducer", () => {
  it("starts from initial state", () => {
    expect(TRANSPORT_INITIAL_STATE.status).toBe("idle");
    expect(TRANSPORT_INITIAL_STATE.positionMs).toBe(0);
    expect(TRANSPORT_INITIAL_STATE.playbackRate).toBe(1);
  });

  it("load sets ready state with duration and steps", () => {
    const state = reduce([transportActions.load({ durationMs: 10_000, stepCount: 4 })]);

    expect(state.status).toBe("ready");
    expect(state.durationMs).toBe(10_000);
    expect(state.stepCount).toBe(4);
    expect(state.currentStepIndex).toBe(0);
  });

  it("load clamps invalid duration and stepCount", () => {
    const state = reduce([transportActions.load({ durationMs: -10, stepCount: 0 })]);

    expect(state.durationMs).toBe(0);
    expect(state.stepCount).toBe(1);
  });

  it("play moves ready state to playing", () => {
    const state = reduce([
      transportActions.load({ durationMs: 5_000, stepCount: 2 }),
      transportActions.play()
    ]);

    expect(state.status).toBe("playing");
  });

  it("play on zero duration keeps ready", () => {
    const state = reduce([
      transportActions.load({ durationMs: 0, stepCount: 2 }),
      transportActions.play()
    ]);

    expect(state.status).toBe("ready");
  });

  it("pause only affects playing state", () => {
    const state = reduce([
      transportActions.load({ durationMs: 5_000, stepCount: 2 }),
      transportActions.pause()
    ]);

    expect(state.status).toBe("ready");
  });

  it("pause transitions playing to paused", () => {
    const state = reduce([
      transportActions.load({ durationMs: 5_000, stepCount: 2 }),
      transportActions.play(),
      transportActions.pause()
    ]);

    expect(state.status).toBe("paused");
  });

  it("stop resets position and status to ready when loaded", () => {
    const state = reduce([
      transportActions.load({ durationMs: 10_000, stepCount: 4 }),
      transportActions.play(),
      transportActions.tick(800),
      transportActions.stop()
    ]);

    expect(state.status).toBe("ready");
    expect(state.positionMs).toBe(0);
  });

  it("stop from idle stays idle", () => {
    const state = reduce([transportActions.stop()]);

    expect(state.status).toBe("idle");
    expect(state.positionMs).toBe(0);
  });

  const tickCases: ReadonlyArray<{
    readonly name: string;
    readonly delta: number;
    readonly rate: number;
    readonly expectedPosition: number;
  }> = [
    {
      name: "tick with delta 100 rate 1",
      delta: 100,
      rate: 1,
      expectedPosition: 100
    },
    {
      name: "tick with delta 250 rate 1",
      delta: 250,
      rate: 1,
      expectedPosition: 250
    },
    {
      name: "tick with delta 400 rate 1",
      delta: 400,
      rate: 1,
      expectedPosition: 400
    },
    {
      name: "tick with delta 100 rate 1.5",
      delta: 100,
      rate: 1.5,
      expectedPosition: 150
    },
    {
      name: "tick with delta 200 rate 1.5",
      delta: 200,
      rate: 1.5,
      expectedPosition: 300
    },
    {
      name: "tick with delta 400 rate 0.5",
      delta: 400,
      rate: 0.5,
      expectedPosition: 200
    },
    {
      name: "tick floors fractional results",
      delta: 333,
      rate: 1.1,
      expectedPosition: 366
    },
    {
      name: "tick with zero delta keeps position",
      delta: 0,
      rate: 1,
      expectedPosition: 0
    },
    {
      name: "tick with negative delta clamps to zero movement",
      delta: -50,
      rate: 1,
      expectedPosition: 0
    },
    {
      name: "tick with high rate clamps later via set-rate",
      delta: 200,
      rate: 4,
      expectedPosition: 800
    }
  ];

  it.each(tickCases)("$name", ({ delta, rate, expectedPosition }) => {
    const state = reduce([
      transportActions.load({ durationMs: 10_000, stepCount: 5 }),
      transportActions.setRate(rate),
      transportActions.play(),
      transportActions.tick(delta)
    ]);

    expect(state.positionMs).toBe(expectedPosition);
  });

  it("tick while paused does nothing", () => {
    const state = reduce([
      transportActions.load({ durationMs: 5_000, stepCount: 4 }),
      transportActions.play(),
      transportActions.tick(300),
      transportActions.pause(),
      transportActions.tick(500)
    ]);

    expect(state.positionMs).toBe(300);
  });

  it("tick stops at end when loop disabled", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 4 }),
      transportActions.play(),
      transportActions.tick(2_000)
    ]);

    expect(state.positionMs).toBe(1_000);
    expect(state.status).toBe("ended");
  });

  it("tick wraps when loop enabled", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 4 }),
      transportActions.toggleLoop(true),
      transportActions.play(),
      transportActions.tick(2_250)
    ]);

    expect(state.positionMs).toBe(250);
    expect(state.status).toBe("playing");
  });

  it("seek clamps below zero", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 4 }),
      transportActions.seek(-10)
    ]);

    expect(state.positionMs).toBe(0);
  });

  it("seek clamps above duration", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 4 }),
      transportActions.seek(5_000)
    ]);

    expect(state.positionMs).toBe(1_000);
    expect(state.status).toBe("ended");
  });

  it("seek to middle updates current step index", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 4 }),
      transportActions.seek(600)
    ]);

    expect(state.currentStepIndex).toBe(2);
  });

  const stepCases: ReadonlyArray<{
    readonly stepIndex: number;
    readonly expectedPosition: number;
    readonly expectedCurrentStep: number;
  }> = [
    { stepIndex: 0, expectedPosition: 0, expectedCurrentStep: 0 },
    { stepIndex: 1, expectedPosition: 250, expectedCurrentStep: 1 },
    { stepIndex: 2, expectedPosition: 500, expectedCurrentStep: 2 },
    { stepIndex: 3, expectedPosition: 750, expectedCurrentStep: 3 },
    { stepIndex: 4, expectedPosition: 750, expectedCurrentStep: 3 },
    { stepIndex: 99, expectedPosition: 750, expectedCurrentStep: 3 },
    { stepIndex: -5, expectedPosition: 0, expectedCurrentStep: 0 }
  ];

  it.each(stepCases)("set-step $stepIndex maps to expected segment", ({
    stepIndex,
    expectedPosition,
    expectedCurrentStep
  }) => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 4 }),
      transportActions.setStep(stepIndex)
    ]);

    expect(state.positionMs).toBe(expectedPosition);
    expect(state.currentStepIndex).toBe(expectedCurrentStep);
  });

  const rateCases: ReadonlyArray<{
    readonly rate: number;
    readonly expected: number;
  }> = [
    { rate: 0, expected: 0.1 },
    { rate: -2, expected: 0.1 },
    { rate: 0.2, expected: 0.2 },
    { rate: 1, expected: 1 },
    { rate: 2.5, expected: 2.5 },
    { rate: 9, expected: 4 },
    { rate: Number.POSITIVE_INFINITY, expected: 1 },
    { rate: Number.NaN, expected: 1 }
  ];

  it.each(rateCases)("set-rate clamps $rate", ({ rate, expected }) => {
    const state = reduce([
      transportActions.load({ durationMs: 5_000, stepCount: 4 }),
      transportActions.setRate(rate)
    ]);

    expect(state.playbackRate).toBe(expected);
  });

  it("toggle-loop true forces loop on", () => {
    const state = reduce([
      transportActions.load({ durationMs: 2_000, stepCount: 2 }),
      transportActions.toggleLoop(true)
    ]);

    expect(state.loop).toBe(true);
  });

  it("toggle-loop false forces loop off", () => {
    const state = reduce([
      transportActions.load({ durationMs: 2_000, stepCount: 2 }),
      transportActions.toggleLoop(true),
      transportActions.toggleLoop(false)
    ]);

    expect(state.loop).toBe(false);
  });

  it("toggle-loop without payload toggles", () => {
    const state = reduce([
      transportActions.load({ durationMs: 2_000, stepCount: 2 }),
      transportActions.toggleLoop(),
      transportActions.toggleLoop()
    ]);

    expect(state.loop).toBe(false);
  });

  it("unknown action returns same state reference equivalence semantics", () => {
    const loaded = reduce([transportActions.load({ durationMs: 1_000, stepCount: 2 })]);
    const unknown = transportReducer(loaded, { type: "unknown" } as never);

    expect(unknown).toEqual(loaded);
  });

  it("selector progress returns 0 for zero duration", () => {
    const state = TRANSPORT_INITIAL_STATE;
    expect(selectTransportProgress(state)).toBe(0);
  });

  it("selector progress returns normalized percentage", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 2 }),
      transportActions.seek(250)
    ]);

    expect(selectTransportProgress(state)).toBe(0.25);
  });

  it("selector remaining ms computes from duration and position", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 2 }),
      transportActions.seek(250)
    ]);

    expect(selectTransportRemainingMs(state)).toBe(750);
  });

  it("selector isPlaying true when status playing", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 2 }),
      transportActions.play()
    ]);

    expect(selectTransportIsPlaying(state)).toBe(true);
  });

  it("selector current step index mirrors state", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 4 }),
      transportActions.seek(700)
    ]);

    expect(selectCurrentStepIndex(state)).toBe(2);
  });

  it("selector current step label is deterministic", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 4 }),
      transportActions.seek(700)
    ]);

    expect(selectCurrentStepLabel(state)).toBe("step-3");
  });

  it("selector canPlay false while playing", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 2 }),
      transportActions.play()
    ]);

    expect(selectCanPlay(state)).toBe(false);
  });

  it("selector canPlay true for ready state", () => {
    const state = reduce([transportActions.load({ durationMs: 1_000, stepCount: 2 })]);

    expect(selectCanPlay(state)).toBe(true);
  });

  it("selector canPause true only while playing", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 2 }),
      transportActions.play()
    ]);

    expect(selectCanPause(state)).toBe(true);
  });

  it("selector canPause false when paused", () => {
    const state = reduce([
      transportActions.load({ durationMs: 1_000, stepCount: 2 }),
      transportActions.play(),
      transportActions.pause()
    ]);

    expect(selectCanPause(state)).toBe(false);
  });

  const reducerSequenceCases: ReadonlyArray<{
    readonly name: string;
    readonly actions: Parameters<typeof transportReducer>[1][];
    readonly expected: Partial<TransportState>;
  }> = [
    {
      name: "load play tick pause",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.play(),
        transportActions.tick(500),
        transportActions.pause()
      ],
      expected: {
        status: "paused",
        positionMs: 500,
        currentStepIndex: 1
      }
    },
    {
      name: "load play end",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.play(),
        transportActions.tick(2_100)
      ],
      expected: {
        status: "ended",
        positionMs: 2_000,
        currentStepIndex: 3
      }
    },
    {
      name: "load play loop wrap",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.toggleLoop(true),
        transportActions.play(),
        transportActions.tick(2_500)
      ],
      expected: {
        status: "playing",
        positionMs: 500,
        currentStepIndex: 1
      }
    },
    {
      name: "load seek stop",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.seek(1_600),
        transportActions.stop()
      ],
      expected: {
        status: "ready",
        positionMs: 0,
        currentStepIndex: 0
      }
    },
    {
      name: "load set-step play tick",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.setStep(2),
        transportActions.play(),
        transportActions.tick(250)
      ],
      expected: {
        status: "playing",
        positionMs: 1_250,
        currentStepIndex: 2
      }
    },
    {
      name: "load set-rate play tick",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.setRate(2),
        transportActions.play(),
        transportActions.tick(250)
      ],
      expected: {
        status: "playing",
        positionMs: 500,
        currentStepIndex: 1
      }
    },
    {
      name: "load toggle loop default",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.toggleLoop()
      ],
      expected: {
        loop: true
      }
    },
    {
      name: "tick ignored when ready",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.tick(100)
      ],
      expected: {
        status: "ready",
        positionMs: 0
      }
    },
    {
      name: "seek can create ended state",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.seek(2_000)
      ],
      expected: {
        status: "ended",
        currentStepIndex: 3
      }
    },
    {
      name: "play from ended stays ended",
      actions: [
        transportActions.load({ durationMs: 2_000, stepCount: 4 }),
        transportActions.seek(2_000),
        transportActions.play()
      ],
      expected: {
        status: "ended"
      }
    }
  ];

  it.each(reducerSequenceCases)("$name", ({ actions, expected }) => {
    const state = reduce(actions);

    for (const [key, value] of Object.entries(expected)) {
      expect((state as Record<string, unknown>)[key]).toEqual(value);
    }
  });
});
