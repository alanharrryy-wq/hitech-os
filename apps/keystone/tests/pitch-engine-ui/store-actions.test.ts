import { usePitchEngineStore } from "../../components/pitch-engine/state/use-pitch-engine-store";

function resetStore(): void {
  usePitchEngineStore.setState((state) => ({
    ...state,
    library: {
      ...state.library,
      selectedProgramId: state.library.programs[0]?.id ?? null,
      selectedSceneId: state.library.programs[0]?.scenes[0]?.id ?? null,
      selectedSequenceId: state.library.programs[0]?.sequences[0]?.id ?? null
    },
    transport: {
      ...state.transport,
      isPlaying: false,
      isLooping: false,
      currentMs: 0,
      playbackRate: 1
    },
    __undoStack: []
  }));
}

describe("pitch engine store", () => {
  beforeEach(() => {
    resetStore();
  });

  it("creates and selects a new sequence via preset injection", () => {
    const before = usePitchEngineStore.getState();
    const programId = before.library.selectedProgramId;
    const sceneId = before.library.selectedSceneId;

    expect(programId).not.toBeNull();
    expect(sceneId).not.toBeNull();

    const beforeProgram = before.library.programs.find((program) => program.id === programId);
    const beforeCount = beforeProgram?.sequences.length ?? 0;

    usePitchEngineStore.getState().createSequence({
      baseSceneId: sceneId ?? "",
      name: "Generated Sequence",
      description: "Injected in test",
      presetId: "preset-01-01"
    });

    const after = usePitchEngineStore.getState();
    const afterProgram = after.library.programs.find((program) => program.id === programId);

    expect((afterProgram?.sequences.length ?? 0) - beforeCount).toBe(1);
    expect(after.library.selectedSequenceId).not.toBeNull();
  });

  it("ticks transport and respects loop mode", () => {
    const store = usePitchEngineStore.getState();

    store.setTransportMs(10);
    store.setTransportRate(1);
    store.setTransportPlaying(true);
    store.setTransportLooping(false);

    store.tickTransport(1000);

    const mid = usePitchEngineStore.getState();
    expect(mid.transport.currentMs).toBeGreaterThan(10);

    store.setTransportLooping(true);
    store.setTransportMs(store.transport.durationMs - 1);
    store.tickTransport(50);

    const looped = usePitchEngineStore.getState();
    expect(looped.transport.currentMs).toBeLessThanOrEqual(looped.transport.durationMs);
  });

  it("records scene snapshots and supports undo", () => {
    const before = usePitchEngineStore.getState();
    const programId = before.library.selectedProgramId;
    expect(programId).not.toBeNull();

    const beforeProgram = before.library.programs.find((program) => program.id === programId);
    const beforeScenes = beforeProgram?.scenes.length ?? 0;

    usePitchEngineStore.getState().recordSnapshot({
      snapshot: {
        route: "/pitch/test",
        canonicalUrl: "https://keystone.local/pitch/test",
        title: "Recorded Test Scene",
        capturedAt: new Date().toISOString(),
        flagSnapshot: {
          resolvedFlags: ["director-mode"],
          unknownTokens: ["legacy-flag"]
        },
        viewport: {
          width: 1280,
          height: 720,
          dpr: 1
        }
      },
      createSequence: true,
      sequenceName: "Recorded Sequence",
      sequencePresetId: "preset-01-01"
    });

    const recorded = usePitchEngineStore.getState();
    const recordedProgram = recorded.library.programs.find((program) => program.id === programId);
    expect((recordedProgram?.scenes.length ?? 0) - beforeScenes).toBe(1);
    expect(recorded.recorder.undoAvailable).toBe(true);

    usePitchEngineStore.getState().undoLastRecord();
    const reverted = usePitchEngineStore.getState();
    const revertedProgram = reverted.library.programs.find((program) => program.id === programId);
    expect(revertedProgram?.scenes.length).toBe(beforeScenes);
  });
});
