import {
  PITCH_PROGRAM_SCHEMA_VERSION,
  SEQUENCE_SCHEMA_VERSION,
  type DirectorSequence,
  type PitchProgram,
  type SceneRecord
} from "../../lib/pitch-engine/index.js";

export function createSceneRecord(overrides: Partial<SceneRecord> = {}): SceneRecord {
  const scene: SceneRecord = {
    sceneId: "scene.demo.01",
    route: "/pitch/01-double-engine",
    query: {
      org: "hitech",
      mode: "demo"
    },
    viewport: {
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1
    },
    profile: "neutral",
    layers: ["hero", "kpis", "cta"],
    motion: {
      enabled: true,
      intensity: "medium",
      reducedMotionPolicy: "respect"
    }
  };

  return {
    ...scene,
    ...overrides,
    query: overrides.query ?? scene.query,
    viewport: overrides.viewport ?? scene.viewport,
    layers: overrides.layers ?? scene.layers,
    motion: overrides.motion ?? scene.motion
  };
}

export function createPitchProgram(overrides: Partial<PitchProgram> = {}): PitchProgram {
  const createdAt = "2026-03-01T00:00:00.000Z";
  const updatedAt = "2026-03-01T00:00:10.000Z";

  const base: PitchProgram = {
    schemaVersion: PITCH_PROGRAM_SCHEMA_VERSION,
    programId: "program.demo.01",
    title: "Demo Program",
    description: "Program for deterministic tests",
    tags: ["investor", "deck"],
    createdAt,
    updatedAt,
    defaultPresetId: "neutral",
    chapters: [
      {
        chapterId: "chapter.1",
        label: "Intro",
        stepId: "step.1"
      },
      {
        chapterId: "chapter.2",
        label: "Value",
        stepId: "step.2"
      }
    ],
    steps: [
      {
        stepId: "step.1",
        title: "Opening",
        label: "Open",
        sceneRef: {
          type: "inlineScene",
          scene: createSceneRecord()
        },
        durationMs: 5_000,
        transition: {
          type: "fade",
          ms: 500,
          easing: "easeInOut"
        },
        presetId: "neutral",
        markers: ["Reveal", "Settle"],
        director: {
          sequenceId: "sequence.demo.01",
          apply: true
        },
        expectations: {
          requiredDataAttributes: ["org", "mode"],
          requiredLayers: ["hero", "kpis"],
          minEnabledLayers: 2
        }
      },
      {
        stepId: "step.2",
        title: "Closing",
        label: "Close",
        sceneRef: {
          type: "sceneId",
          sceneId: "scene.demo.02"
        },
        durationMs: 6_000,
        transition: {
          type: "crossfade",
          ms: 700,
          easing: "easeOut"
        },
        presetId: "investor",
        markers: ["CTA"],
        director: {
          apply: false
        },
        expectations: {
          requiredLayers: ["cta"],
          minEnabledLayers: 1
        }
      }
    ],
    capabilityRequest: {
      director: "full"
    },
    metadata: {
      source: "tests",
      gitHash: "abcdef1",
      notes: "fixture"
    }
  };

  return {
    ...base,
    ...overrides,
    tags: overrides.tags ?? base.tags,
    chapters: overrides.chapters ?? base.chapters,
    steps: overrides.steps ?? base.steps,
    capabilityRequest: overrides.capabilityRequest ?? base.capabilityRequest,
    metadata: overrides.metadata ?? base.metadata
  };
}

export function createSequence(overrides: Partial<DirectorSequence> = {}): DirectorSequence {
  const createdAt = "2026-03-01T00:01:00.000Z";
  const updatedAt = "2026-03-01T00:01:10.000Z";

  const base: DirectorSequence = {
    sequenceId: "sequence.demo.01",
    schemaVersion: SEQUENCE_SCHEMA_VERSION,
    createdAt,
    updatedAt,
    baseSceneRef: {
      type: "inlineScene",
      scene: createSceneRecord()
    },
    timelineDSL: {
      tracks: ["camera", "overlay", "motion", "layers"],
      keyframes: [
        {
          tMs: 0,
          track: "camera",
          key: "zoom",
          value: 1,
          easing: "linear"
        },
        {
          tMs: 600,
          track: "overlay",
          key: "headline",
          value: "Opening",
          easing: "easeOut"
        },
        {
          tMs: 1_200,
          track: "motion",
          key: "heroEntrance",
          value: "slide-up",
          easing: "easeIn"
        },
        {
          tMs: 1_800,
          track: "layers",
          key: "intensity",
          value: 0.9,
          easing: "linear"
        },
        {
          tMs: 2_400,
          track: "camera",
          key: "panX",
          value: 0.1,
          easing: "easeInOut"
        },
        {
          tMs: 3_000,
          track: "motion",
          key: "parallax",
          value: 0.8,
          easing: "linear"
        },
        {
          tMs: 3_600,
          track: "overlay",
          key: "cta",
          value: "Book a demo",
          easing: "easeInOut"
        }
      ],
      markers: [
        {
          tMs: 0,
          label: "Reveal"
        },
        {
          tMs: 2_000,
          label: "Settle"
        },
        {
          tMs: 3_600,
          label: "CTA"
        }
      ]
    },
    rules: {
      motionBudget: {
        maxHeroMotions: 2,
        maxTrackKeyframes: 10
      },
      reducedMotion: {
        strategy: "jumpToFinal"
      },
      perfDegrade: {
        strategy: "lite"
      }
    }
  };

  return {
    ...base,
    ...overrides,
    baseSceneRef: overrides.baseSceneRef ?? base.baseSceneRef,
    timelineDSL: overrides.timelineDSL ?? base.timelineDSL,
    rules: overrides.rules ?? base.rules
  };
}

export function deepClone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}
