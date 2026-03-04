import { describe, expect, it } from "vitest";
import {
  canonicalizeSequence,
  computeDerived,
  deserializeSequence,
  formatSequenceValidationErrors,
  hashSequence,
  migrateSequenceToV1,
  parseSequence,
  serializeSequence,
  validateSequence
} from "../../lib/pitch-engine/index.js";
import { createSceneRecord, createSequence, deepClone } from "./fixtures.js";

describe("sequence-schema", () => {
  it("accepts valid sequence", () => {
    const sequence = createSequence();
    const parsed = parseSequence(sequence);

    expect(parsed.sequenceId).toBe("sequence.demo.01");
    expect(parsed.timelineDSL.keyframes.length).toBeGreaterThan(0);
  });

  it("returns legible validation errors", () => {
    const invalid = createSequence({ sequenceId: "" });
    const text = formatSequenceValidationErrors(invalid);

    expect(text).toContain("Validation failed at sequenceId");
  });

  it("validator safe result reports path", () => {
    const invalid = createSequence({
      rules: {
        ...createSequence().rules,
        motionBudget: {
          maxHeroMotions: -1,
          maxTrackKeyframes: 10
        }
      }
    });

    const result = validateSequence(invalid);
    expect(result.ok).toBe(false);
    expect(result.errors[0]?.path).toContain("rules.motionBudget.maxHeroMotions");
  });

  const invalidCases: ReadonlyArray<{
    readonly name: string;
    readonly mutate: (sequence: ReturnType<typeof createSequence>) => unknown;
    readonly expectedPath: string;
  }> = [
    {
      name: "rejects empty sequenceId",
      mutate: (sequence) => ({ ...sequence, sequenceId: "" }),
      expectedPath: "sequenceId"
    },
    {
      name: "rejects malformed sequenceId",
      mutate: (sequence) => ({ ...sequence, sequenceId: "bad id" }),
      expectedPath: "sequenceId"
    },
    {
      name: "rejects invalid schemaVersion",
      mutate: (sequence) => ({ ...sequence, schemaVersion: 2 }),
      expectedPath: "schemaVersion"
    },
    {
      name: "rejects invalid createdAt",
      mutate: (sequence) => ({ ...sequence, createdAt: "now" }),
      expectedPath: "createdAt"
    },
    {
      name: "rejects invalid updatedAt",
      mutate: (sequence) => ({ ...sequence, updatedAt: "today" }),
      expectedPath: "updatedAt"
    },
    {
      name: "rejects updatedAt before createdAt",
      mutate: (sequence) => ({
        ...sequence,
        createdAt: "2026-03-01T00:00:10.000Z",
        updatedAt: "2026-03-01T00:00:01.000Z"
      }),
      expectedPath: "updatedAt"
    },
    {
      name: "rejects empty tracks",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          tracks: []
        }
      }),
      expectedPath: "timelineDSL.tracks"
    },
    {
      name: "rejects duplicate tracks",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          tracks: ["camera", "camera"]
        }
      }),
      expectedPath: "timelineDSL.tracks"
    },
    {
      name: "rejects unknown track enum",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          tracks: ["camera", "audio" as never]
        }
      }),
      expectedPath: "timelineDSL.tracks[1]"
    },
    {
      name: "rejects keyframe time below zero",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], tMs: -1 }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].tMs"
    },
    {
      name: "rejects keyframe time above max",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], tMs: 200_000 }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].tMs"
    },
    {
      name: "rejects keyframe unknown track",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], track: "audio" as never }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].track"
    },
    {
      name: "rejects keyframe key not allowed for track",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], track: "camera", key: "headline" }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].key"
    },
    {
      name: "rejects keyframe unknown easing",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], easing: "spring" as never }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].easing"
    },
    {
      name: "rejects keyframe value object without value",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], value: { unit: "px" } as never }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].value"
    },
    {
      name: "rejects keyframe value array too long",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{
            ...sequence.timelineDSL.keyframes[0],
            value: Array.from({ length: 200 }, (_, index) => `item-${index}`)
          }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].value"
    },
    {
      name: "rejects keyframe out of declared tracks",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          tracks: ["camera"],
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], track: "overlay" }],
          markers: sequence.timelineDSL.markers
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].track"
    },
    {
      name: "rejects unsorted keyframes",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [
            { ...sequence.timelineDSL.keyframes[1], tMs: 1_000 },
            { ...sequence.timelineDSL.keyframes[0], tMs: 200 }
          ]
        }
      }),
      expectedPath: "timelineDSL.keyframes[1].tMs"
    },
    {
      name: "rejects duplicate keyframe signature",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [
            { ...sequence.timelineDSL.keyframes[0], tMs: 500, track: "camera", key: "zoom" },
            { ...sequence.timelineDSL.keyframes[1], tMs: 500, track: "camera", key: "zoom" }
          ]
        }
      }),
      expectedPath: "timelineDSL.keyframes[1]"
    },
    {
      name: "rejects marker time below zero",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          markers: [{ tMs: -1, label: "bad" }]
        }
      }),
      expectedPath: "timelineDSL.markers[0].tMs"
    },
    {
      name: "rejects marker label empty",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          markers: [{ tMs: 100, label: "" }]
        }
      }),
      expectedPath: "timelineDSL.markers[0].label"
    },
    {
      name: "rejects duplicate marker signature",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          markers: [
            { tMs: 400, label: "Reveal" },
            { tMs: 400, label: "Reveal" }
          ]
        }
      }),
      expectedPath: "timelineDSL.markers[1]"
    },
    {
      name: "rejects motion budget negative hero",
      mutate: (sequence) => ({
        ...sequence,
        rules: {
          ...sequence.rules,
          motionBudget: {
            maxHeroMotions: -1,
            maxTrackKeyframes: 10
          }
        }
      }),
      expectedPath: "rules.motionBudget.maxHeroMotions"
    },
    {
      name: "rejects motion budget hero above max",
      mutate: (sequence) => ({
        ...sequence,
        rules: {
          ...sequence.rules,
          motionBudget: {
            maxHeroMotions: 13,
            maxTrackKeyframes: 10
          }
        }
      }),
      expectedPath: "rules.motionBudget.maxHeroMotions"
    },
    {
      name: "rejects motion budget keyframe below min",
      mutate: (sequence) => ({
        ...sequence,
        rules: {
          ...sequence.rules,
          motionBudget: {
            maxHeroMotions: 1,
            maxTrackKeyframes: 0
          }
        }
      }),
      expectedPath: "rules.motionBudget.maxTrackKeyframes"
    },
    {
      name: "rejects maxTrackKeyframes less than timeline count",
      mutate: (sequence) => ({
        ...sequence,
        rules: {
          ...sequence.rules,
          motionBudget: {
            maxHeroMotions: 2,
            maxTrackKeyframes: 2
          }
        }
      }),
      expectedPath: "rules.motionBudget.maxTrackKeyframes"
    },
    {
      name: "rejects reducedMotion strategy unsupported",
      mutate: (sequence) => ({
        ...sequence,
        rules: {
          ...sequence.rules,
          reducedMotion: {
            strategy: "fadeOut" as never
          }
        }
      }),
      expectedPath: "rules.reducedMotion.strategy"
    },
    {
      name: "rejects perfDegrade strategy unsupported",
      mutate: (sequence) => ({
        ...sequence,
        rules: {
          ...sequence.rules,
          perfDegrade: {
            strategy: "off" as never
          }
        }
      }),
      expectedPath: "rules.perfDegrade.strategy"
    },
    {
      name: "rejects unknown key in rules",
      mutate: (sequence) => ({
        ...sequence,
        rules: {
          ...sequence.rules,
          extra: true
        }
      }),
      expectedPath: "rules"
    },
    {
      name: "rejects unknown key in timelineDSL",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          notes: "x"
        }
      }),
      expectedPath: "timelineDSL"
    },
    {
      name: "rejects unknown key in marker",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          markers: [{ tMs: 10, label: "x", note: "extra" } as never]
        }
      }),
      expectedPath: "timelineDSL.markers[0]"
    },
    {
      name: "rejects unknown key in keyframe",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], note: "extra" } as never]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0]"
    },
    {
      name: "rejects too many keyframes",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: Array.from({ length: 8_100 }, (_, index) => ({
            tMs: index,
            track: "camera",
            key: "zoom",
            value: 1,
            easing: "linear"
          }))
        }
      }),
      expectedPath: "timelineDSL.keyframes"
    },
    {
      name: "rejects too many markers",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          markers: Array.from({ length: 1_200 }, (_, index) => ({ tMs: index, label: `m-${index}` }))
        }
      }),
      expectedPath: "timelineDSL.markers"
    },
    {
      name: "rejects base scene route missing slash",
      mutate: (sequence) => ({
        ...sequence,
        baseSceneRef: {
          type: "inlineScene",
          scene: createSceneRecord({ route: "pitch" })
        }
      }),
      expectedPath: "baseSceneRef.scene.route"
    },
    {
      name: "rejects base scene profile unknown",
      mutate: (sequence) => ({
        ...sequence,
        baseSceneRef: {
          type: "inlineScene",
          scene: createSceneRecord({ profile: "legacy" as never })
        }
      }),
      expectedPath: "baseSceneRef.scene.profile"
    },
    {
      name: "rejects base scene layer id format",
      mutate: (sequence) => ({
        ...sequence,
        baseSceneRef: {
          type: "inlineScene",
          scene: createSceneRecord({ layers: ["bad id"] })
        }
      }),
      expectedPath: "baseSceneRef.scene.layers[0]"
    },
    {
      name: "rejects base scene query value too long",
      mutate: (sequence) => ({
        ...sequence,
        baseSceneRef: {
          type: "inlineScene",
          scene: createSceneRecord({ query: { x: "v".repeat(300) } })
        }
      }),
      expectedPath: "baseSceneRef.scene.query.x"
    },
    {
      name: "rejects base scene id invalid",
      mutate: (sequence) => ({
        ...sequence,
        baseSceneRef: {
          type: "sceneId",
          sceneId: "bad id"
        }
      }),
      expectedPath: "baseSceneRef.sceneId"
    },
    {
      name: "rejects unknown key root",
      mutate: (sequence) => ({
        ...sequence,
        extra: true
      }),
      expectedPath: "<root>"
    },
    {
      name: "rejects keyframe string value too long",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], value: "x".repeat(900) }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].value"
    },
    {
      name: "rejects keyframe object unit too long",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], value: { value: 1, unit: "x".repeat(100) } }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].value"
    },
    {
      name: "rejects keyframe non-finite number",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          keyframes: [{ ...sequence.timelineDSL.keyframes[0], value: Number.NaN }]
        }
      }),
      expectedPath: "timelineDSL.keyframes[0].value"
    },
    {
      name: "rejects marker label too long",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          markers: [{ tMs: 10, label: "x".repeat(300) }]
        }
      }),
      expectedPath: "timelineDSL.markers[0].label"
    },
    {
      name: "rejects timeline tracks above max",
      mutate: (sequence) => ({
        ...sequence,
        timelineDSL: {
          ...sequence.timelineDSL,
          tracks: ["camera", "overlay", "motion", "layers", "camera"] as never
        }
      }),
      expectedPath: "timelineDSL.tracks"
    }
  ];

  it.each(invalidCases)("$name", ({ mutate, expectedPath }) => {
    const input = mutate(deepClone(createSequence()) as ReturnType<typeof createSequence>);
    const result = validateSequence(input);

    expect(result.ok).toBe(false);
    const pathSummary = result.errors.map((error) => error.path).join("|");
    expect(pathSummary).toContain(expectedPath);
  });

  it("canonicalization sorts tracks keyframes and markers deterministically", () => {
    const sequence = createSequence({
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers", "camera"],
        keyframes: [
          { tMs: 600, track: "overlay", key: "headline", value: "A", easing: "easeOut" },
          { tMs: 0, track: "camera", key: "zoom", value: 1, easing: "linear" },
          { tMs: 600, track: "camera", key: "panX", value: 0.2, easing: "linear" }
        ],
        markers: [
          { tMs: 1000, label: "B" },
          { tMs: 400, label: "A" }
        ]
      }
    });

    const canonical = canonicalizeSequence(sequence);

    expect(canonical.timelineDSL.tracks).toEqual(["camera", "overlay", "motion", "layers"]);
    expect(canonical.timelineDSL.keyframes[0]?.track).toBe("camera");
    expect(canonical.timelineDSL.markers[0]?.label).toBe("A");
  });

  it("serializer + deserializer preserve canonical sequence semantics", () => {
    const sequence = createSequence();
    const serialized = serializeSequence(sequence);
    const reparsed = deserializeSequence(serialized);

    expect(serializeSequence(reparsed)).toBe(serialized);
  });

  it("hash is stable for semantically equivalent sequence", () => {
    const left = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        tracks: ["camera", "overlay", "layers", "motion"]
      }
    });

    const right = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        tracks: ["motion", "camera", "overlay", "layers"]
      }
    });

    expect(hashSequence(left)).toBe(hashSequence(right));
  });

  it("computeDerived captures start keyframe marker and end timestamps", () => {
    const plan = computeDerived(createSequence());

    expect(plan.timestamps[0]).toBe(0);
    expect(plan.timestamps).toContain(3_600);
    expect(plan.entries.some((entry) => entry.reason === "end")).toBe(true);
  });

  it("migration stub upgrades unknown version sequence", () => {
    const legacy = {
      ...createSequence(),
      schemaVersion: undefined
    };

    const migrated = migrateSequenceToV1(legacy);

    expect(migrated.sequence.schemaVersion).toBe(1);
    expect(migrated.migrations).toHaveLength(1);
    expect(migrated.migrations[0]?.fromVersion).toBe("unknown");
  });

  it("migration passthrough leaves v1 unchanged", () => {
    const sequence = createSequence();
    const migrated = migrateSequenceToV1(sequence);

    expect(migrated.sequence.sequenceId).toBe(sequence.sequenceId);
    expect(migrated.migrations).toHaveLength(0);
  });
});
