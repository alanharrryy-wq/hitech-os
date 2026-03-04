"use client";

import { create } from "zustand";
import { DEFAULT_PROGRAM_LIBRARY } from "../program-library/default-programs";
import { ensurePreset } from "../timeline/preset-scripts";
import type {
  ArtifactRunIndex,
  ArtifactTriageItem,
  CapabilityMode,
  CapabilityStatus,
  OperatorHudStatus,
  PitchEngineUiState,
  PitchProgram,
  PitchScene,
  PitchSequence,
  ProgramCreateInput,
  ProgramSelection,
  RecorderRequest,
  SceneRecorderSnapshot,
  SequenceCreateInput,
  TimelineMarker,
  TimelineTrack,
  TransportState,
  TriageActionResult
} from "../types";
import { evaluateCapability, toCapabilityStatus } from "../utils/capability";
import { buildStableId, nowIso } from "../utils/id";
import {
  buildDefaultHudStatus,
  LOCAL_STORAGE_KEYS,
  readJsonStorage,
  writeJsonStorage
} from "../utils/storage";
import {
  clampMs,
  createMarker,
  createSequenceFromPreset,
  getSequenceDuration,
  patchTrack
} from "../utils/timeline";

export interface PitchEngineActions {
  readonly hydratePrograms: (programs: PitchProgram[]) => void;
  readonly selectProgram: (programId: string) => void;
  readonly selectScene: (sceneId: string) => void;
  readonly selectSequence: (sequenceId: string) => void;
  readonly createProgram: (input: ProgramCreateInput) => PitchProgram;
  readonly replaceProgram: (program: PitchProgram) => void;
  readonly removeProgram: (programId: string) => void;
  readonly importProgram: (program: PitchProgram) => void;
  readonly createSequence: (input: SequenceCreateInput) => void;
  readonly updateTrack: (
    sequenceId: string,
    trackId: string,
    updater: (track: TimelineTrack) => TimelineTrack
  ) => void;
  readonly addMarker: (
    sequenceId: string,
    input: {
      readonly type: TimelineMarker["type"];
      readonly label: string;
      readonly t: number;
      readonly note: string;
    }
  ) => void;
  readonly removeMarker: (sequenceId: string, markerId: string) => void;
  readonly setTransportPlaying: (value: boolean) => void;
  readonly setTransportLooping: (value: boolean) => void;
  readonly setTransportRate: (rate: TransportState["playbackRate"]) => void;
  readonly setTransportMs: (ms: number) => void;
  readonly tickTransport: (deltaMs: number) => void;
  readonly jumpToMarker: (markerId: string) => void;
  readonly setTimelineWipePercent: (value: number) => void;
  readonly setTimelineZoom: (value: number) => void;
  readonly setTimelinePan: (value: { readonly x: number; readonly y: number }) => void;
  readonly updateCapabilityMode: (mode: CapabilityMode, input?: { readonly debug?: boolean }) => void;
  readonly setOperatorHud: (hud: OperatorHudStatus) => void;
  readonly mergeOperatorHud: (hud: Partial<OperatorHudStatus>) => void;
  readonly setArtifactRuns: (runs: ArtifactRunIndex[]) => void;
  readonly selectTriageItem: (itemId: string | null) => void;
  readonly applyTriageResult: (result: TriageActionResult) => void;
  readonly setUiError: (message: string | null) => void;
  readonly recordSnapshot: (request: RecorderRequest) => void;
  readonly undoLastRecord: () => void;
  readonly setSecureOrigin: (origin: string | null) => void;
  readonly incrementRejectedMessages: () => void;
}

interface UndoRecord {
  readonly programId: string;
  readonly programBefore: PitchProgram;
}

export type PitchEngineStore = PitchEngineUiState &
  PitchEngineActions & {
    readonly __undoStack: UndoRecord[];
  };

const DEV_ENV = process.env.NODE_ENV !== "production";

function cloneProgram(program: PitchProgram): PitchProgram {
  return JSON.parse(JSON.stringify(program)) as PitchProgram;
}

function findProgram(programs: readonly PitchProgram[], programId: string | null): PitchProgram | null {
  if (!programId) {
    return null;
  }
  return programs.find((program) => program.id === programId) ?? null;
}

function pickInitialSelection(programs: readonly PitchProgram[]): ProgramSelection {
  if (programs.length === 0) {
    return { programId: null, sceneId: null, sequenceId: null };
  }

  const program = programs[0];
  const scene = program.scenes[0] ?? null;
  const sequence = scene
    ? program.sequences.find((item) => item.sceneId === scene.id) ?? program.sequences[0] ?? null
    : program.sequences[0] ?? null;

  return {
    programId: program.id,
    sceneId: scene?.id ?? null,
    sequenceId: sequence?.id ?? null
  };
}

function selectConsistentSelection(programs: readonly PitchProgram[], selection: ProgramSelection): ProgramSelection {
  const program = findProgram(programs, selection.programId);
  if (!program) {
    return pickInitialSelection(programs);
  }

  const scene = selection.sceneId
    ? program.scenes.find((item) => item.id === selection.sceneId) ?? null
    : program.scenes[0] ?? null;

  const sequence = selection.sequenceId
    ? program.sequences.find((item) => item.id === selection.sequenceId) ?? null
    : scene
      ? program.sequences.find((item) => item.sceneId === scene.id) ?? null
      : program.sequences[0] ?? null;

  return {
    programId: program.id,
    sceneId: scene?.id ?? null,
    sequenceId: sequence?.id ?? null
  };
}

function persistSelection(selection: ProgramSelection): void {
  writeJsonStorage(LOCAL_STORAGE_KEYS.librarySelection, selection);
}

function readSelection(programs: readonly PitchProgram[]): ProgramSelection {
  const saved = readJsonStorage<ProgramSelection>(LOCAL_STORAGE_KEYS.librarySelection);
  return saved ? selectConsistentSelection(programs, saved) : pickInitialSelection(programs);
}

function initialCapabilityStatus(): CapabilityStatus {
  const requested = readJsonStorage<CapabilityMode>(LOCAL_STORAGE_KEYS.capabilityRequestedMode) ?? "debug";

  const result = evaluateCapability({
    requestedMode: requested,
    isDevEnvironment: DEV_ENV,
    debugTokenPresent: true,
    envOverrideEnabled: false,
    viewportWidth: 1920,
    prefersReducedMotion: false,
    deviceMemoryGb: 8,
    hardwareConcurrency: 8
  });

  return toCapabilityStatus({
    evalResult: result,
    isDev: DEV_ENV,
    debugTokenPresent: true,
    envOverrideEnabled: false
  });
}

function mutateProgram(
  programs: readonly PitchProgram[],
  programId: string,
  updater: (program: PitchProgram) => PitchProgram
): PitchProgram[] {
  return programs.map((program) => (program.id === programId ? updater(program) : program));
}

function selectedProgramFromState(state: PitchEngineStore): PitchProgram | null {
  return findProgram(state.library.programs, state.library.selectedProgramId);
}

function selectedSequenceFromState(state: PitchEngineStore): PitchSequence | null {
  const program = selectedProgramFromState(state);
  if (!program || !state.library.selectedSequenceId) {
    return null;
  }

  return program.sequences.find((item) => item.id === state.library.selectedSequenceId) ?? null;
}

function updateWithProgram(
  state: PitchEngineStore,
  updater: (program: PitchProgram) => {
    readonly program: PitchProgram;
    readonly selection: ProgramSelection;
    readonly undo?: UndoRecord;
  }
): Partial<PitchEngineStore> {
  const selected = selectedProgramFromState(state);
  if (!selected) {
    return {};
  }

  const next = updater(selected);
  persistSelection(next.selection);

  return {
    library: {
      programs: mutateProgram(state.library.programs, selected.id, () => next.program),
      selectedProgramId: next.selection.programId,
      selectedSceneId: next.selection.sceneId,
      selectedSequenceId: next.selection.sequenceId
    },
    ...(next.undo ? { __undoStack: [next.undo, ...state.__undoStack] } : {})
  } as Partial<PitchEngineStore>;
}

function computeDuration(state: PitchEngineStore): number {
  const sequence = selectedSequenceFromState(state);
  return getSequenceDuration(sequence);
}

const DEFAULT_PROGRAMS = DEFAULT_PROGRAM_LIBRARY.map(cloneProgram);
const INITIAL_SELECTION = readSelection(DEFAULT_PROGRAMS);

export const usePitchEngineStore = create<PitchEngineStore>()((set, get) => {
  const hud = readJsonStorage<OperatorHudStatus>(LOCAL_STORAGE_KEYS.hud) ?? buildDefaultHudStatus();

  return {
    capabilityStatus: initialCapabilityStatus(),
    library: {
      programs: DEFAULT_PROGRAMS,
      selectedProgramId: INITIAL_SELECTION.programId,
      selectedSceneId: INITIAL_SELECTION.sceneId,
      selectedSequenceId: INITIAL_SELECTION.sequenceId
    },
    transport: {
      isPlaying: false,
      isLooping: false,
      currentMs: 0,
      durationMs: 9000,
      playbackRate: 1,
      markerJumpId: null
    },
    operatorHud: hud,
    recorder: {
      lastSnapshot: null,
      undoAvailable: false,
      lastRecordMessage: null,
      secureOrigin: null,
      rejectedMessages: 0
    },
    triageRuns: [],
    selectedTriageItemId: null,
    timelineWipePercent: 50,
    timelineZoom: readJsonStorage<number>(LOCAL_STORAGE_KEYS.triageZoom) ?? 1,
    timelinePan: { x: 0, y: 0 },
    reducedMotionApplied: false,
    uiError: null,
    __undoStack: [],

    hydratePrograms: (programs) => {
      set((state) => {
        const nextPrograms = programs.length > 0 ? programs.map(cloneProgram) : state.library.programs;
        const nextSelection = selectConsistentSelection(nextPrograms, {
          programId: state.library.selectedProgramId,
          sceneId: state.library.selectedSceneId,
          sequenceId: state.library.selectedSequenceId
        });

        persistSelection(nextSelection);

        const nextState = {
          ...state,
          library: {
            programs: nextPrograms,
            selectedProgramId: nextSelection.programId,
            selectedSceneId: nextSelection.sceneId,
            selectedSequenceId: nextSelection.sequenceId
          }
        } as PitchEngineStore;

        return {
          library: nextState.library,
          transport: {
            ...state.transport,
            durationMs: computeDuration(nextState),
            currentMs: 0,
            markerJumpId: null
          }
        };
      });
    },

    selectProgram: (programId) => {
      set((state) => {
        const program = state.library.programs.find((item) => item.id === programId);
        if (!program) {
          return {};
        }

        const scene = program.scenes[0] ?? null;
        const sequence = scene
          ? program.sequences.find((item) => item.sceneId === scene.id) ?? program.sequences[0] ?? null
          : program.sequences[0] ?? null;

        const selection = {
          programId: program.id,
          sceneId: scene?.id ?? null,
          sequenceId: sequence?.id ?? null
        };
        persistSelection(selection);

        return {
          library: {
            ...state.library,
            selectedProgramId: selection.programId,
            selectedSceneId: selection.sceneId,
            selectedSequenceId: selection.sequenceId
          },
          transport: {
            ...state.transport,
            currentMs: 0,
            durationMs: sequence?.timeline.durationMs ?? 0,
            markerJumpId: null
          }
        };
      });
    },

    selectScene: (sceneId) => {
      set((state) => {
        const program = selectedProgramFromState(state);
        if (!program) {
          return {};
        }

        const scene = program.scenes.find((item) => item.id === sceneId);
        if (!scene) {
          return {};
        }

        const sequence = program.sequences.find((item) => item.sceneId === scene.id) ?? null;
        const selection = {
          programId: program.id,
          sceneId: scene.id,
          sequenceId: sequence?.id ?? null
        };
        persistSelection(selection);

        return {
          library: {
            ...state.library,
            selectedSceneId: scene.id,
            selectedSequenceId: sequence?.id ?? null
          },
          transport: {
            ...state.transport,
            currentMs: 0,
            durationMs: sequence?.timeline.durationMs ?? 0,
            markerJumpId: null
          }
        };
      });
    },

    selectSequence: (sequenceId) => {
      set((state) => {
        const program = selectedProgramFromState(state);
        if (!program) {
          return {};
        }

        const sequence = program.sequences.find((item) => item.id === sequenceId);
        if (!sequence) {
          return {};
        }

        const selection = {
          programId: program.id,
          sceneId: sequence.sceneId,
          sequenceId: sequence.id
        };
        persistSelection(selection);

        return {
          library: {
            ...state.library,
            selectedSceneId: sequence.sceneId,
            selectedSequenceId: sequence.id
          },
          transport: {
            ...state.transport,
            currentMs: 0,
            durationMs: sequence.timeline.durationMs,
            markerJumpId: null
          }
        };
      });
    },

    createProgram: (input) => {
      const state = get();
      const now = nowIso();
      const id = buildStableId("program", input.name, state.library.programs.map((item) => item.id));

      const program: PitchProgram = {
        id,
        name: input.name,
        description: input.description,
        owner: input.owner,
        version: "1.0.0",
        createdAt: now,
        updatedAt: now,
        scenes: [],
        sequences: [],
        diagnostics: {
          source: "user",
          lastSaveError: null,
          warnings: [],
          artifactLinks: []
        }
      };

      set((current) => {
        const selection = { programId: id, sceneId: null, sequenceId: null };
        persistSelection(selection);

        return {
          library: {
            programs: [...current.library.programs, program],
            selectedProgramId: id,
            selectedSceneId: null,
            selectedSequenceId: null
          }
        };
      });

      return program;
    },

    replaceProgram: (program) => {
      set((state) => {
        const exists = state.library.programs.some((item) => item.id === program.id);
        const programs = exists
          ? state.library.programs.map((item) => (item.id === program.id ? cloneProgram(program) : item))
          : [...state.library.programs, cloneProgram(program)];

        const selection = selectConsistentSelection(programs, {
          programId: state.library.selectedProgramId,
          sceneId: state.library.selectedSceneId,
          sequenceId: state.library.selectedSequenceId
        });
        persistSelection(selection);

        return {
          library: {
            programs,
            selectedProgramId: selection.programId,
            selectedSceneId: selection.sceneId,
            selectedSequenceId: selection.sequenceId
          }
        };
      });
    },

    removeProgram: (programId) => {
      set((state) => {
        const programs = state.library.programs.filter((item) => item.id !== programId);
        const selection = pickInitialSelection(programs);
        persistSelection(selection);

        return {
          library: {
            programs,
            selectedProgramId: selection.programId,
            selectedSceneId: selection.sceneId,
            selectedSequenceId: selection.sequenceId
          },
          transport: {
            ...state.transport,
            currentMs: 0,
            durationMs: 0,
            markerJumpId: null
          }
        };
      });
    },

    importProgram: (program) => {
      set((state) => {
        const existingIds = state.library.programs.map((item) => item.id);
        const imported = existingIds.includes(program.id)
          ? { ...program, id: buildStableId("program-import", program.name, existingIds) }
          : program;

        const selection = {
          programId: imported.id,
          sceneId: imported.scenes[0]?.id ?? null,
          sequenceId: imported.sequences[0]?.id ?? null
        };
        persistSelection(selection);

        return {
          library: {
            programs: [...state.library.programs, cloneProgram(imported)],
            selectedProgramId: selection.programId,
            selectedSceneId: selection.sceneId,
            selectedSequenceId: selection.sequenceId
          }
        };
      });
    },

    createSequence: (input) => {
      set((state) => {
        const patch = updateWithProgram(state, (program) => {
          const scene = program.scenes.find((item) => item.id === input.baseSceneId);
          if (!scene) {
            return {
              program,
              selection: {
                programId: state.library.selectedProgramId,
                sceneId: state.library.selectedSceneId,
                sequenceId: state.library.selectedSequenceId
              }
            };
          }

          const preset = ensurePreset(input.presetId);
          const created = createSequenceFromPreset({
            scene,
            existingSequences: program.sequences,
            create: input,
            preset
          });

          const nextProgram: PitchProgram = {
            ...program,
            updatedAt: nowIso(),
            sequences: [...program.sequences, created],
            scenes: program.scenes.map((item) =>
              item.id === scene.id && item.defaultSequenceId === null
                ? { ...item, defaultSequenceId: created.id }
                : item
            )
          };

          return {
            program: nextProgram,
            selection: {
              programId: program.id,
              sceneId: created.sceneId,
              sequenceId: created.id
            }
          };
        });

        const next = { ...state, ...patch } as PitchEngineStore;

        return {
          ...patch,
          transport: {
            ...state.transport,
            currentMs: 0,
            durationMs: computeDuration(next),
            markerJumpId: null
          }
        };
      });
    },

    updateTrack: (sequenceId, trackId, updater) => {
      set((state) =>
        updateWithProgram(state, (program) => {
          const sequence = program.sequences.find((item) => item.id === sequenceId);
          if (!sequence) {
            return {
              program,
              selection: {
                programId: state.library.selectedProgramId,
                sceneId: state.library.selectedSceneId,
                sequenceId: state.library.selectedSequenceId
              }
            };
          }

          const nextSequence: PitchSequence = {
            ...sequence,
            updatedAt: nowIso(),
            timeline: {
              ...sequence.timeline,
              tracks: patchTrack(sequence.timeline.tracks, trackId, updater)
            }
          };

          const nextProgram: PitchProgram = {
            ...program,
            updatedAt: nowIso(),
            sequences: program.sequences.map((item) => (item.id === sequenceId ? nextSequence : item))
          };

          return {
            program: nextProgram,
            selection: {
              programId: program.id,
              sceneId: nextSequence.sceneId,
              sequenceId: nextSequence.id
            }
          };
        })
      );
    },

    addMarker: (sequenceId, input) => {
      set((state) =>
        updateWithProgram(state, (program) => {
          const sequence = program.sequences.find((item) => item.id === sequenceId);
          if (!sequence) {
            return {
              program,
              selection: {
                programId: state.library.selectedProgramId,
                sceneId: state.library.selectedSceneId,
                sequenceId: state.library.selectedSequenceId
              }
            };
          }

          const marker = createMarker(sequence.id, sequence.timeline.markers, input);
          const nextSequence: PitchSequence = {
            ...sequence,
            updatedAt: nowIso(),
            timeline: {
              ...sequence.timeline,
              markers: [...sequence.timeline.markers, marker].sort((a, b) => a.t - b.t)
            }
          };

          return {
            program: {
              ...program,
              updatedAt: nowIso(),
              sequences: program.sequences.map((item) => (item.id === sequence.id ? nextSequence : item))
            },
            selection: {
              programId: program.id,
              sceneId: nextSequence.sceneId,
              sequenceId: nextSequence.id
            }
          };
        })
      );
    },

    removeMarker: (sequenceId, markerId) => {
      set((state) =>
        updateWithProgram(state, (program) => {
          const sequence = program.sequences.find((item) => item.id === sequenceId);
          if (!sequence) {
            return {
              program,
              selection: {
                programId: state.library.selectedProgramId,
                sceneId: state.library.selectedSceneId,
                sequenceId: state.library.selectedSequenceId
              }
            };
          }

          const nextSequence: PitchSequence = {
            ...sequence,
            updatedAt: nowIso(),
            timeline: {
              ...sequence.timeline,
              markers: sequence.timeline.markers.filter((marker) => marker.id !== markerId)
            }
          };

          return {
            program: {
              ...program,
              updatedAt: nowIso(),
              sequences: program.sequences.map((item) => (item.id === sequence.id ? nextSequence : item))
            },
            selection: {
              programId: program.id,
              sceneId: nextSequence.sceneId,
              sequenceId: nextSequence.id
            }
          };
        })
      );
    },

    setTransportPlaying: (value) => {
      set((state) => ({ transport: { ...state.transport, isPlaying: value } }));
    },

    setTransportLooping: (value) => {
      set((state) => ({ transport: { ...state.transport, isLooping: value } }));
    },

    setTransportRate: (rate) => {
      set((state) => ({ transport: { ...state.transport, playbackRate: rate } }));
    },

    setTransportMs: (ms) => {
      set((state) => ({
        transport: {
          ...state.transport,
          currentMs: clampMs(ms, 0, state.transport.durationMs)
        }
      }));
    },

    tickTransport: (deltaMs) => {
      set((state) => {
        if (!state.transport.isPlaying) {
          return {};
        }

        const delta = deltaMs * state.transport.playbackRate;
        const nextMs = state.transport.currentMs + delta;

        if (nextMs >= state.transport.durationMs) {
          if (state.transport.isLooping) {
            return {
              transport: {
                ...state.transport,
                currentMs: 0,
                markerJumpId: null
              }
            };
          }

          return {
            transport: {
              ...state.transport,
              isPlaying: false,
              currentMs: state.transport.durationMs,
              markerJumpId: null
            }
          };
        }

        return {
          transport: {
            ...state.transport,
            currentMs: nextMs,
            markerJumpId: null
          }
        };
      });
    },

    jumpToMarker: (markerId) => {
      set((state) => {
        const sequence = selectedSequenceFromState(state);
        if (!sequence) {
          return {};
        }

        const marker = sequence.timeline.markers.find((item) => item.id === markerId);
        if (!marker) {
          return {};
        }

        return {
          transport: {
            ...state.transport,
            currentMs: clampMs(marker.t, 0, sequence.timeline.durationMs),
            markerJumpId: marker.id
          }
        };
      });
    },

    setTimelineWipePercent: (value) => {
      set({ timelineWipePercent: clampMs(value, 0, 100) });
    },

    setTimelineZoom: (value) => {
      const zoom = clampMs(value, 0.5, 4);
      set({ timelineZoom: zoom });
      writeJsonStorage(LOCAL_STORAGE_KEYS.triageZoom, zoom);
    },

    setTimelinePan: (value) => {
      set({ timelinePan: value });
    },

    updateCapabilityMode: (mode, input) => {
      set((state) => {
        const result = evaluateCapability({
          requestedMode: mode,
          isDevEnvironment: DEV_ENV,
          debugTokenPresent: input?.debug ?? state.capabilityStatus.debugTokenPresent,
          envOverrideEnabled: state.capabilityStatus.envOverrideEnabled,
          viewportWidth: 1920,
          prefersReducedMotion: false,
          deviceMemoryGb: 8,
          hardwareConcurrency: 8
        });

        writeJsonStorage(LOCAL_STORAGE_KEYS.capabilityRequestedMode, mode);

        return {
          capabilityStatus: toCapabilityStatus({
            evalResult: result,
            isDev: DEV_ENV,
            debugTokenPresent: input?.debug ?? state.capabilityStatus.debugTokenPresent,
            envOverrideEnabled: state.capabilityStatus.envOverrideEnabled
          }),
          reducedMotionApplied: result.degradeReasons.includes("reduced-motion")
        };
      });
    },

    setOperatorHud: (hudUpdate) => {
      writeJsonStorage(LOCAL_STORAGE_KEYS.hud, hudUpdate);
      set({ operatorHud: hudUpdate });
    },

    mergeOperatorHud: (hudUpdate) => {
      set((state) => {
        const merged: OperatorHudStatus = {
          ...state.operatorHud,
          ...hudUpdate,
          updatedAt: nowIso()
        };
        writeJsonStorage(LOCAL_STORAGE_KEYS.hud, merged);
        return { operatorHud: merged };
      });
    },

    setArtifactRuns: (runs) => {
      set((state) => ({
        triageRuns: runs,
        selectedTriageItemId:
          state.selectedTriageItemId && runs.some((run) => run.items.some((item) => item.id === state.selectedTriageItemId))
            ? state.selectedTriageItemId
            : runs[0]?.items[0]?.id ?? null
      }));
    },

    selectTriageItem: (itemId) => {
      set({ selectedTriageItemId: itemId });
    },

    applyTriageResult: (result) => {
      if (!result.updatedItem) {
        return;
      }

      set((state) => {
        const triageRuns = state.triageRuns.map((run) =>
          run.runId === result.updatedItem?.runId
            ? {
                ...run,
                items: run.items.map((item) => (item.id === result.updatedItem?.id ? result.updatedItem : item))
              }
            : run
        );

        const operatorHud: OperatorHudStatus = {
          ...state.operatorHud,
          lastRunStatus: result.ok ? "ok" : "fail",
          lastErrorTail: result.stderr.length > 0 ? result.stderr : null,
          updatedAt: nowIso()
        };

        writeJsonStorage(LOCAL_STORAGE_KEYS.hud, operatorHud);

        return {
          triageRuns,
          operatorHud
        };
      });
    },

    setUiError: (message) => {
      set({ uiError: message });
    },

    recordSnapshot: (request) => {
      set((state) => {
        const patch = updateWithProgram(state, (program) => {
          const sceneId = buildStableId(
            "scene-recorded",
            request.snapshot.title || request.snapshot.route,
            program.scenes.map((item) => item.id)
          );

          const now = nowIso();

          const scene: PitchScene = {
            id: sceneId,
            name: request.snapshot.title,
            route: request.snapshot.route,
            canonicalUrl: request.snapshot.canonicalUrl,
            description: `Recorded from secure preview bridge at ${request.snapshot.capturedAt}`,
            tags: ["recorded", "bridge", "scene-recorder"],
            defaultSequenceId: null,
            recorderSnapshot: request.snapshot,
            createdAt: now,
            updatedAt: now
          };

          let sequenceId: string | null = null;
          let sequences = program.sequences;

          if (request.createSequence) {
            const preset = ensurePreset(request.sequencePresetId);
            const generated = createSequenceFromPreset({
              scene,
              existingSequences: program.sequences,
              create: {
                baseSceneId: sceneId,
                name: request.sequenceName,
                description: "Generated from recorder snapshot.",
                presetId: request.sequencePresetId
              },
              preset
            });

            sequenceId = generated.id;
            sequences = [...program.sequences, generated];
          }

          const nextProgram: PitchProgram = {
            ...program,
            updatedAt: now,
            diagnostics: {
              ...program.diagnostics,
              source: "recorded"
            },
            scenes: [...program.scenes, { ...scene, defaultSequenceId: sequenceId }],
            sequences
          };

          return {
            program: nextProgram,
            selection: {
              programId: program.id,
              sceneId,
              sequenceId
            },
            undo: {
              programId: program.id,
              programBefore: cloneProgram(program)
            }
          };
        });

        const stack = (patch as { __undoStack?: UndoRecord[] }).__undoStack ?? state.__undoStack;

        return {
          ...patch,
          __undoStack: stack,
          recorder: {
            ...state.recorder,
            lastSnapshot: request.snapshot as SceneRecorderSnapshot,
            undoAvailable: stack.length > 0,
            lastRecordMessage: `Recorded ${request.snapshot.route} at ${request.snapshot.capturedAt}`
          }
        };
      });
    },

    undoLastRecord: () => {
      set((state) => {
        const [head, ...tail] = state.__undoStack;
        if (!head) {
          return {};
        }

        const programs = mutateProgram(state.library.programs, head.programId, () => cloneProgram(head.programBefore));
        const selection = selectConsistentSelection(programs, {
          programId: state.library.selectedProgramId,
          sceneId: state.library.selectedSceneId,
          sequenceId: state.library.selectedSequenceId
        });
        persistSelection(selection);

        return {
          __undoStack: tail,
          library: {
            programs,
            selectedProgramId: selection.programId,
            selectedSceneId: selection.sceneId,
            selectedSequenceId: selection.sequenceId
          },
          recorder: {
            ...state.recorder,
            undoAvailable: tail.length > 0,
            lastRecordMessage: "Undo applied"
          }
        };
      });
    },

    setSecureOrigin: (origin) => {
      set((state) => ({ recorder: { ...state.recorder, secureOrigin: origin } }));
    },

    incrementRejectedMessages: () => {
      set((state) => ({
        recorder: {
          ...state.recorder,
          rejectedMessages: state.recorder.rejectedMessages + 1
        }
      }));
    }
  };
});

export function useSelectedProgram(): PitchProgram | null {
  return usePitchEngineStore((state) =>
    state.library.programs.find((program) => program.id === state.library.selectedProgramId) ?? null
  );
}

export function useSelectedScene(): PitchScene | null {
  return usePitchEngineStore((state) => {
    const program = state.library.programs.find((item) => item.id === state.library.selectedProgramId);
    if (!program) {
      return null;
    }

    return program.scenes.find((scene) => scene.id === state.library.selectedSceneId) ?? null;
  });
}

export function useSelectedSequence(): PitchSequence | null {
  return usePitchEngineStore((state) => {
    const program = state.library.programs.find((item) => item.id === state.library.selectedProgramId);
    if (!program) {
      return null;
    }

    return program.sequences.find((sequence) => sequence.id === state.library.selectedSequenceId) ?? null;
  });
}

export function useSelectedTriageItem(): ArtifactTriageItem | null {
  return usePitchEngineStore((state) => {
    if (!state.selectedTriageItemId) {
      return null;
    }

    for (const run of state.triageRuns) {
      const item = run.items.find((candidate) => candidate.id === state.selectedTriageItemId);
      if (item) {
        return item;
      }
    }

    return null;
  });
}
