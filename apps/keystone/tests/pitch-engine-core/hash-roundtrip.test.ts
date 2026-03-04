import { describe, expect, it } from "vitest";
import {
  assertProgramRoundtrip,
  canonicalizePitchProgram,
  canonicalizeSequence,
  compareProgramHashes,
  compareSequenceHashes,
  deserializePitchProgram,
  deserializeSequence,
  hashPitchProgram,
  hashSequence,
  parsePitchProgramJson,
  parseSequenceJson,
  roundtripPitchProgram,
  serializePitchProgram,
  serializeSequence
} from "../../lib/pitch-engine/index.js";
import { createPitchProgram, createSequence } from "./fixtures.js";

describe("hash-roundtrip", () => {
  it("program roundtrip preserves semantic match", () => {
    const result = roundtripPitchProgram(createPitchProgram());

    expect(result.semanticMatch).toBe(true);
    expect(result.serialized.length).toBeGreaterThan(100);
  });

  it("assertProgramRoundtrip does not throw for valid program", () => {
    expect(() => assertProgramRoundtrip(createPitchProgram())).not.toThrow();
  });

  it("program serializer output is deterministic", () => {
    const program = createPitchProgram();

    const first = serializePitchProgram(program);
    const second = serializePitchProgram(program);

    expect(first).toBe(second);
  });

  it("program parser handles serialized JSON", () => {
    const program = createPitchProgram();
    const parsed = parsePitchProgramJson(serializePitchProgram(program));

    expect(parsed.programId).toBe(program.programId);
  });

  it("program deserialize returns canonical object", () => {
    const program = createPitchProgram({ tags: ["z", "a", "a"] });
    const deserialized = deserializePitchProgram(serializePitchProgram(program));

    expect(deserialized.tags).toEqual(["a", "z"]);
  });

  it("program hash stable for canonical equivalents", () => {
    const a = createPitchProgram({ tags: ["a", "b"] });
    const b = createPitchProgram({ tags: ["b", "a", "a"] });

    expect(hashPitchProgram(a)).toBe(hashPitchProgram(b));
    expect(compareProgramHashes(a, b)).toBe(true);
  });

  it("program hash differs when semantic content changes", () => {
    const a = createPitchProgram({ title: "A" });
    const b = createPitchProgram({ title: "B" });

    expect(hashPitchProgram(a)).not.toBe(hashPitchProgram(b));
    expect(compareProgramHashes(a, b)).toBe(false);
  });

  const programHashCases: ReadonlyArray<{
    readonly name: string;
    readonly left: ReturnType<typeof createPitchProgram>;
    readonly right: ReturnType<typeof createPitchProgram>;
    readonly equal: boolean;
  }> = [
    {
      name: "tags order ignored",
      left: createPitchProgram({ tags: ["a", "b"] }),
      right: createPitchProgram({ tags: ["b", "a"] }),
      equal: true
    },
    {
      name: "markers order ignored in canonicalization",
      left: createPitchProgram({
        steps: [
          { ...createPitchProgram().steps[0], markers: ["Reveal", "Settle"] },
          createPitchProgram().steps[1]
        ]
      }),
      right: createPitchProgram({
        steps: [
          { ...createPitchProgram().steps[0], markers: ["Settle", "Reveal"] },
          createPitchProgram().steps[1]
        ]
      }),
      equal: true
    },
    {
      name: "transition ms changes hash",
      left: createPitchProgram({
        steps: [
          { ...createPitchProgram().steps[0], transition: { ...createPitchProgram().steps[0]!.transition, ms: 400 } },
          createPitchProgram().steps[1]
        ]
      }),
      right: createPitchProgram({
        steps: [
          { ...createPitchProgram().steps[0], transition: { ...createPitchProgram().steps[0]!.transition, ms: 401 } },
          createPitchProgram().steps[1]
        ]
      }),
      equal: false
    },
    {
      name: "scene query key order ignored",
      left: createPitchProgram({
        steps: [
          {
            ...createPitchProgram().steps[0],
            sceneRef: {
              type: "inlineScene",
              scene: {
                ...createPitchProgram().steps[0]!.sceneRef.type === "inlineScene"
                  ? createPitchProgram().steps[0]!.sceneRef.scene
                  : createPitchProgram().steps[0]!.sceneRef,
                sceneId: "scene.demo.01",
                route: "/pitch/01-double-engine",
                query: { a: "1", z: "2" },
                viewport: { width: 1920, height: 1080 },
                profile: "neutral",
                layers: ["hero", "kpis"],
                motion: { enabled: true, intensity: "medium" }
              }
            }
          },
          createPitchProgram().steps[1]
        ]
      }),
      right: createPitchProgram({
        steps: [
          {
            ...createPitchProgram().steps[0],
            sceneRef: {
              type: "inlineScene",
              scene: {
                sceneId: "scene.demo.01",
                route: "/pitch/01-double-engine",
                query: { z: "2", a: "1" },
                viewport: { width: 1920, height: 1080 },
                profile: "neutral",
                layers: ["kpis", "hero"],
                motion: { enabled: true, intensity: "medium" }
              }
            }
          },
          createPitchProgram().steps[1]
        ]
      }),
      equal: true
    },
    {
      name: "program title changes hash",
      left: createPitchProgram({ title: "Alpha" }),
      right: createPitchProgram({ title: "Beta" }),
      equal: false
    }
  ];

  it.each(programHashCases)("program hash case: $name", ({ left, right, equal }) => {
    expect(compareProgramHashes(left, right)).toBe(equal);
  });

  it("sequence serializer output is deterministic", () => {
    const sequence = createSequence();

    const first = serializeSequence(sequence);
    const second = serializeSequence(sequence);

    expect(first).toBe(second);
  });

  it("sequence parser handles serialized JSON", () => {
    const sequence = createSequence();
    const parsed = parseSequenceJson(serializeSequence(sequence));

    expect(parsed.sequenceId).toBe(sequence.sequenceId);
  });

  it("sequence deserialize canonicalizes track order", () => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        tracks: ["motion", "camera", "overlay", "layers"]
      }
    });

    const deserialized = deserializeSequence(serializeSequence(sequence));

    expect(deserialized.timelineDSL.tracks).toEqual(["camera", "overlay", "motion", "layers"]);
  });

  it("sequence hash stable for canonical equivalents", () => {
    const left = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        tracks: ["motion", "camera", "overlay", "layers"]
      }
    });

    const right = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        tracks: ["camera", "overlay", "motion", "layers"]
      }
    });

    expect(hashSequence(left)).toBe(hashSequence(right));
    expect(compareSequenceHashes(left, right)).toBe(true);
  });

  it("sequence hash differs when keyframe value changes", () => {
    const left = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [{ ...createSequence().timelineDSL.keyframes[0], value: 1 }]
      }
    });

    const right = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        keyframes: [{ ...createSequence().timelineDSL.keyframes[0], value: 1.1 }]
      }
    });

    expect(hashSequence(left)).not.toBe(hashSequence(right));
    expect(compareSequenceHashes(left, right)).toBe(false);
  });

  const sequenceHashCases: ReadonlyArray<{
    readonly name: string;
    readonly left: ReturnType<typeof createSequence>;
    readonly right: ReturnType<typeof createSequence>;
    readonly equal: boolean;
  }> = [
    {
      name: "keyframes order normalized",
      left: createSequence({
        timelineDSL: {
          ...createSequence().timelineDSL,
          keyframes: [
            { tMs: 100, track: "overlay", key: "headline", value: "A", easing: "linear" },
            { tMs: 0, track: "camera", key: "zoom", value: 1, easing: "linear" }
          ]
        }
      }),
      right: createSequence({
        timelineDSL: {
          ...createSequence().timelineDSL,
          keyframes: [
            { tMs: 0, track: "camera", key: "zoom", value: 1, easing: "linear" },
            { tMs: 100, track: "overlay", key: "headline", value: "A", easing: "linear" }
          ]
        }
      }),
      equal: true
    },
    {
      name: "markers order normalized",
      left: createSequence({
        timelineDSL: {
          ...createSequence().timelineDSL,
          markers: [
            { tMs: 600, label: "B" },
            { tMs: 100, label: "A" }
          ]
        }
      }),
      right: createSequence({
        timelineDSL: {
          ...createSequence().timelineDSL,
          markers: [
            { tMs: 100, label: "A" },
            { tMs: 600, label: "B" }
          ]
        }
      }),
      equal: true
    },
    {
      name: "rule change affects hash",
      left: createSequence({
        rules: {
          ...createSequence().rules,
          motionBudget: {
            maxHeroMotions: 2,
            maxTrackKeyframes: 10
          }
        }
      }),
      right: createSequence({
        rules: {
          ...createSequence().rules,
          motionBudget: {
            maxHeroMotions: 1,
            maxTrackKeyframes: 10
          }
        }
      }),
      equal: false
    },
    {
      name: "baseSceneRef sceneId change affects hash",
      left: createSequence({
        baseSceneRef: {
          type: "sceneId",
          sceneId: "scene.1"
        }
      }),
      right: createSequence({
        baseSceneRef: {
          type: "sceneId",
          sceneId: "scene.2"
        }
      }),
      equal: false
    },
    {
      name: "createdAt change affects hash",
      left: createSequence({
        createdAt: "2026-03-01T00:00:00.000Z"
      }),
      right: createSequence({
        createdAt: "2026-03-02T00:00:00.000Z"
      }),
      equal: false
    }
  ];

  it.each(sequenceHashCases)("sequence hash case: $name", ({ left, right, equal }) => {
    expect(compareSequenceHashes(left, right)).toBe(equal);
  });

  it("canonicalizeProgram is idempotent", () => {
    const program = createPitchProgram({ tags: ["c", "b", "a"] });

    const first = canonicalizePitchProgram(program);
    const second = canonicalizePitchProgram(first);

    expect(first).toEqual(second);
  });

  it("canonicalizeSequence is idempotent", () => {
    const sequence = createSequence({
      timelineDSL: {
        ...createSequence().timelineDSL,
        tracks: ["motion", "camera", "overlay", "layers"]
      }
    });

    const first = canonicalizeSequence(sequence);
    const second = canonicalizeSequence(first);

    expect(first).toEqual(second);
  });

  it("serialized program output can be reserialized without drift", () => {
    const program = createPitchProgram();

    const serialized = serializePitchProgram(program);
    const reparsed = deserializePitchProgram(serialized);
    const reserialized = serializePitchProgram(reparsed);

    expect(reserialized).toBe(serialized);
  });

  it("serialized sequence output can be reserialized without drift", () => {
    const sequence = createSequence();

    const serialized = serializeSequence(sequence);
    const reparsed = deserializeSequence(serialized);
    const reserialized = serializeSequence(reparsed);

    expect(reserialized).toBe(serialized);
  });
});
