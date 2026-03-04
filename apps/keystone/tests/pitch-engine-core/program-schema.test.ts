import { describe, expect, it } from "vitest";
import {
  canonicalizePitchProgram,
  deserializePitchProgram,
  formatProgramValidationErrors,
  hashPitchProgram,
  migrateProgramToV1,
  parsePitchProgram,
  PITCH_PROGRAM_SCHEMA_VERSION,
  serializePitchProgram,
  validatePitchProgram
} from "../../lib/pitch-engine/index.js";
import { createPitchProgram, createSceneRecord, deepClone } from "./fixtures.js";

describe("program-schema", () => {
  it("accepts a valid v1 program", () => {
    const program = createPitchProgram();
    const parsed = parsePitchProgram(program);

    expect(parsed.programId).toBe("program.demo.01");
    expect(parsed.schemaVersion).toBe(PITCH_PROGRAM_SCHEMA_VERSION);
    expect(parsed.steps).toHaveLength(2);
  });

  it("validator returns legible error for first issue", () => {
    const program = createPitchProgram({
      steps: []
    });

    const message = formatProgramValidationErrors(program);
    expect(message).toContain("Validation failed at steps");
  });

  it("safe validator returns structured errors", () => {
    const program = createPitchProgram({
      programId: ""
    });

    const result = validatePitchProgram(program);
    expect(result.ok).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
    expect(result.errors[0]?.path).toBe("programId");
  });

  const invalidCases: ReadonlyArray<{
    readonly name: string;
    readonly mutate: (program: ReturnType<typeof createPitchProgram>) => unknown;
    readonly expectedPath: string;
  }> = [
    {
      name: "rejects empty programId",
      mutate: (program) => ({ ...program, programId: "" }),
      expectedPath: "programId"
    },
    {
      name: "rejects invalid programId characters",
      mutate: (program) => ({ ...program, programId: "bad id" }),
      expectedPath: "programId"
    },
    {
      name: "rejects empty title",
      mutate: (program) => ({ ...program, title: "" }),
      expectedPath: "title"
    },
    {
      name: "rejects too-long description",
      mutate: (program) => ({ ...program, description: "x".repeat(3_000) }),
      expectedPath: "description"
    },
    {
      name: "rejects tags above max",
      mutate: (program) => ({ ...program, tags: Array.from({ length: 200 }, (_, index) => `tag-${index}`) }),
      expectedPath: "tags"
    },
    {
      name: "rejects non-iso createdAt",
      mutate: (program) => ({ ...program, createdAt: "03-01-2026" }),
      expectedPath: "createdAt"
    },
    {
      name: "rejects non-iso updatedAt",
      mutate: (program) => ({ ...program, updatedAt: "yesterday" }),
      expectedPath: "updatedAt"
    },
    {
      name: "rejects updatedAt before createdAt",
      mutate: (program) => ({
        ...program,
        createdAt: "2026-03-01T00:00:10.000Z",
        updatedAt: "2026-03-01T00:00:01.000Z"
      }),
      expectedPath: "updatedAt"
    },
    {
      name: "rejects unsupported default preset",
      mutate: (program) => ({ ...program, defaultPresetId: "ultra" as never }),
      expectedPath: "defaultPresetId"
    },
    {
      name: "rejects empty steps",
      mutate: (program) => ({ ...program, steps: [] }),
      expectedPath: "steps"
    },
    {
      name: "rejects more than max steps",
      mutate: (program) => ({
        ...program,
        steps: Array.from({ length: 1_010 }, (_, index) => ({
          ...program.steps[0],
          stepId: `step.${index}`
        }))
      }),
      expectedPath: "steps"
    },
    {
      name: "rejects duplicate step ids",
      mutate: (program) => ({
        ...program,
        steps: [program.steps[0], { ...program.steps[1], stepId: program.steps[0]!.stepId }]
      }),
      expectedPath: "steps[1].stepId"
    },
    {
      name: "rejects chapter unknown step",
      mutate: (program) => ({
        ...program,
        chapters: [{ chapterId: "chapter.1", label: "bad", stepId: "missing.step" }]
      }),
      expectedPath: "chapters[0].stepId"
    },
    {
      name: "rejects duplicate chapter ids",
      mutate: (program) => ({
        ...program,
        chapters: [
          { chapterId: "chapter.dup", label: "a", stepId: "step.1" },
          { chapterId: "chapter.dup", label: "b", stepId: "step.2" }
        ]
      }),
      expectedPath: "chapters[1].chapterId"
    },
    {
      name: "rejects step duration too short",
      mutate: (program) => ({
        ...program,
        steps: [{ ...program.steps[0], durationMs: 200 }, program.steps[1]]
      }),
      expectedPath: "steps[0].durationMs"
    },
    {
      name: "rejects step duration too long",
      mutate: (program) => ({
        ...program,
        steps: [{ ...program.steps[0], durationMs: 121_000 }, program.steps[1]]
      }),
      expectedPath: "steps[0].durationMs"
    },
    {
      name: "rejects unsupported transition type",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            transition: {
              ...program.steps[0]!.transition,
              type: "zoom" as never
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].transition.type"
    },
    {
      name: "rejects transition duration over max",
      mutate: (program) => ({
        ...program,
        steps: [{ ...program.steps[0], transition: { ...program.steps[0]!.transition, ms: 16_000 } }, program.steps[1]]
      }),
      expectedPath: "steps[0].transition.ms"
    },
    {
      name: "rejects unsupported easing",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            transition: {
              ...program.steps[0]!.transition,
              easing: "bounce" as never
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].transition.easing"
    },
    {
      name: "rejects step with bad scene ref type",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            sceneRef: {
              type: "invalid" as never,
              sceneId: "scene.x"
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].sceneRef.type"
    },
    {
      name: "rejects scene route without slash",
      mutate: (program) => {
        const scene = createSceneRecord({ route: "pitch" });
        return {
          ...program,
          steps: [
            {
              ...program.steps[0],
              sceneRef: {
                type: "inlineScene",
                scene
              }
            },
            program.steps[1]
          ]
        };
      },
      expectedPath: "steps[0].sceneRef.scene.route"
    },
    {
      name: "rejects scene viewport width below min",
      mutate: (program) => {
        const scene = createSceneRecord({
          viewport: {
            width: 100,
            height: 1080
          }
        });
        return {
          ...program,
          steps: [
            {
              ...program.steps[0],
              sceneRef: {
                type: "inlineScene",
                scene
              }
            },
            program.steps[1]
          ]
        };
      },
      expectedPath: "steps[0].sceneRef.scene.viewport.width"
    },
    {
      name: "rejects scene viewport height below min",
      mutate: (program) => {
        const scene = createSceneRecord({
          viewport: {
            width: 1920,
            height: 120
          }
        });
        return {
          ...program,
          steps: [
            {
              ...program.steps[0],
              sceneRef: {
                type: "inlineScene",
                scene
              }
            },
            program.steps[1]
          ]
        };
      },
      expectedPath: "steps[0].sceneRef.scene.viewport.height"
    },
    {
      name: "rejects scene motion intensity invalid",
      mutate: (program) => {
        const scene = createSceneRecord({
          motion: {
            enabled: true,
            intensity: "wild" as never
          }
        });

        return {
          ...program,
          steps: [
            {
              ...program.steps[0],
              sceneRef: {
                type: "inlineScene",
                scene
              }
            },
            program.steps[1]
          ]
        };
      },
      expectedPath: "steps[0].sceneRef.scene.motion.intensity"
    },
    {
      name: "rejects scene profile unsupported",
      mutate: (program) => {
        const scene = createSceneRecord({ profile: "legacy" as never });
        return {
          ...program,
          steps: [
            {
              ...program.steps[0],
              sceneRef: {
                type: "inlineScene",
                scene
              }
            },
            program.steps[1]
          ]
        };
      },
      expectedPath: "steps[0].sceneRef.scene.profile"
    },
    {
      name: "rejects markers above max",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            markers: Array.from({ length: 40 }, (_, index) => `m-${index}`)
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].markers"
    },
    {
      name: "rejects director sequence with apply false",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            director: {
              sequenceId: "sequence.x",
              apply: false
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].director"
    },
    {
      name: "rejects expectations minEnabled over requiredLayers",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            expectations: {
              requiredLayers: ["hero"],
              minEnabledLayers: 2
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].expectations.minEnabledLayers"
    },
    {
      name: "rejects capability request invalid enum",
      mutate: (program) => ({
        ...program,
        capabilityRequest: {
          director: "super" as never
        }
      }),
      expectedPath: "capabilityRequest.director"
    },
    {
      name: "rejects metadata gitHash too short",
      mutate: (program) => ({
        ...program,
        metadata: {
          source: "tests",
          gitHash: "abc"
        }
      }),
      expectedPath: "metadata.gitHash"
    },
    {
      name: "rejects unknown root key",
      mutate: (program) => ({
        ...program,
        ghost: true
      }),
      expectedPath: "<root>"
    },
    {
      name: "rejects chapterId format",
      mutate: (program) => ({
        ...program,
        chapters: [
          {
            chapterId: "bad id",
            label: "bad",
            stepId: "step.1"
          }
        ]
      }),
      expectedPath: "chapters[0].chapterId"
    },
    {
      name: "rejects chapter label empty",
      mutate: (program) => ({
        ...program,
        chapters: [
          {
            chapterId: "chapter.x",
            label: "",
            stepId: "step.1"
          }
        ]
      }),
      expectedPath: "chapters[0].label"
    },
    {
      name: "rejects stepId format",
      mutate: (program) => ({
        ...program,
        steps: [{ ...program.steps[0], stepId: "bad id" }, program.steps[1]]
      }),
      expectedPath: "steps[0].stepId"
    },
    {
      name: "rejects step title empty",
      mutate: (program) => ({
        ...program,
        steps: [{ ...program.steps[0], title: "" }, program.steps[1]]
      }),
      expectedPath: "steps[0].title"
    },
    {
      name: "rejects requiredDataAttributes too many",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            expectations: {
              requiredDataAttributes: Array.from({ length: 70 }, (_, index) => `attr-${index}`)
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].expectations.requiredDataAttributes"
    },
    {
      name: "rejects requiredLayers too many",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            expectations: {
              requiredLayers: Array.from({ length: 80 }, (_, index) => `layer-${index}`)
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].expectations.requiredLayers"
    },
    {
      name: "rejects required layer id bad format",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            expectations: {
              requiredLayers: ["bad id"]
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].expectations.requiredLayers[0]"
    },
    {
      name: "rejects required attribute empty",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            expectations: {
              requiredDataAttributes: [""]
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].expectations.requiredDataAttributes[0]"
    },
    {
      name: "rejects minEnabledLayers negative",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            expectations: {
              minEnabledLayers: -1
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].expectations.minEnabledLayers"
    },
    {
      name: "rejects scene query value too long",
      mutate: (program) => {
        const scene = createSceneRecord({
          query: {
            org: "hitech",
            long: "v".repeat(500)
          }
        });

        return {
          ...program,
          steps: [{ ...program.steps[0], sceneRef: { type: "inlineScene", scene } }, program.steps[1]]
        };
      },
      expectedPath: "steps[0].sceneRef.scene.query.long"
    },
    {
      name: "rejects scene query key too long",
      mutate: (program) => {
        const longKey = "k".repeat(130);
        const scene = createSceneRecord({
          query: {
            [longKey]: "value"
          }
        });

        return {
          ...program,
          steps: [{ ...program.steps[0], sceneRef: { type: "inlineScene", scene } }, program.steps[1]]
        };
      },
      expectedPath: "steps[0].sceneRef.scene.query"
    },
    {
      name: "rejects scene layers too many",
      mutate: (program) => {
        const scene = createSceneRecord({
          layers: Array.from({ length: 200 }, (_, index) => `layer-${index}`)
        });
        return {
          ...program,
          steps: [{ ...program.steps[0], sceneRef: { type: "inlineScene", scene } }, program.steps[1]]
        };
      },
      expectedPath: "steps[0].sceneRef.scene.layers"
    },
    {
      name: "rejects sceneId format in ref",
      mutate: (program) => ({
        ...program,
        steps: [program.steps[0], { ...program.steps[1], sceneRef: { type: "sceneId", sceneId: "bad id" } }]
      }),
      expectedPath: "steps[1].sceneRef.sceneId"
    },
    {
      name: "rejects marker with empty string",
      mutate: (program) => ({
        ...program,
        steps: [{ ...program.steps[0], markers: ["Reveal", ""] }, program.steps[1]]
      }),
      expectedPath: "steps[0].markers[1]"
    },
    {
      name: "rejects metadata source empty",
      mutate: (program) => ({
        ...program,
        metadata: {
          source: ""
        }
      }),
      expectedPath: "metadata.source"
    },
    {
      name: "rejects metadata notes empty",
      mutate: (program) => ({
        ...program,
        metadata: {
          notes: ""
        }
      }),
      expectedPath: "metadata.notes"
    },
    {
      name: "rejects invalid schema version",
      mutate: (program) => ({
        ...program,
        schemaVersion: 2
      }),
      expectedPath: "schemaVersion"
    },
    {
      name: "rejects unknown capability request key",
      mutate: (program) => ({
        ...program,
        capabilityRequest: {
          director: "full",
          other: "x"
        }
      }),
      expectedPath: "capabilityRequest"
    },
    {
      name: "rejects unknown metadata key",
      mutate: (program) => ({
        ...program,
        metadata: {
          source: "tests",
          owner: "qa"
        }
      }),
      expectedPath: "metadata"
    },
    {
      name: "rejects unknown expectations key",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            expectations: {
              requiredLayers: ["hero"],
              unknown: true
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].expectations"
    },
    {
      name: "rejects unknown director key",
      mutate: (program) => ({
        ...program,
        steps: [
          {
            ...program.steps[0],
            director: {
              apply: true,
              verbose: true
            }
          },
          program.steps[1]
        ]
      }),
      expectedPath: "steps[0].director"
    },
    {
      name: "rejects scene motion unknown key",
      mutate: (program) => {
        const scene = {
          ...createSceneRecord(),
          motion: {
            enabled: true,
            intensity: "low",
            custom: true
          }
        };

        return {
          ...program,
          steps: [{ ...program.steps[0], sceneRef: { type: "inlineScene", scene: scene as never } }, program.steps[1]]
        };
      },
      expectedPath: "steps[0].sceneRef.scene.motion"
    }
  ];

  it.each(invalidCases)("$name", ({ mutate, expectedPath }) => {
    const candidate = mutate(deepClone(createPitchProgram()) as ReturnType<typeof createPitchProgram>);
    const result = validatePitchProgram(candidate);

    expect(result.ok).toBe(false);
    const pathSummary = result.errors.map((error) => error.path).join(" |");
    expect(pathSummary).toContain(expectedPath);
  });

  it("canonical serializer sorts tags and inline scene keys deterministically", () => {
    const program = createPitchProgram({
      tags: ["z", "a", "a"],
      steps: [
        {
          ...createPitchProgram().steps[0],
          sceneRef: {
            type: "inlineScene",
            scene: createSceneRecord({
              query: {
                z: "1",
                a: "2"
              },
              layers: ["kpis", "hero", "hero"]
            })
          }
        },
        createPitchProgram().steps[1]
      ]
    });

    const canonical = canonicalizePitchProgram(program);

    expect(canonical.tags).toEqual(["a", "z"]);
    expect(canonical.steps[0]?.sceneRef.type).toBe("inlineScene");
    if (canonical.steps[0]?.sceneRef.type === "inlineScene") {
      expect(Object.keys(canonical.steps[0].sceneRef.scene.query)).toEqual(["a", "z"]);
      expect(canonical.steps[0].sceneRef.scene.layers).toEqual(["hero", "kpis"]);
    }
  });

  it("serializer and deserializer preserve canonical semantics", () => {
    const program = createPitchProgram({
      tags: ["b", "a", "c"]
    });

    const serialized = serializePitchProgram(program);
    const reparsed = deserializePitchProgram(serialized);

    expect(serializePitchProgram(reparsed)).toBe(serialized);
  });

  it("hash is stable for semantically equivalent programs", () => {
    const left = createPitchProgram({
      tags: ["a", "b"],
      steps: [
        {
          ...createPitchProgram().steps[0],
          markers: ["Settle", "Reveal"]
        },
        createPitchProgram().steps[1]
      ]
    });

    const right = createPitchProgram({
      tags: ["b", "a", "a"],
      steps: [
        {
          ...createPitchProgram().steps[0],
          markers: ["Reveal", "Settle"]
        },
        createPitchProgram().steps[1]
      ]
    });

    expect(hashPitchProgram(left)).toBe(hashPitchProgram(right));
  });

  it("migration stub upgrades missing schemaVersion payload", () => {
    const legacy = createPitchProgram();
    const raw = {
      ...legacy,
      schemaVersion: undefined
    };

    const migrated = migrateProgramToV1(raw);

    expect(migrated.program.schemaVersion).toBe(1);
    expect(migrated.migrations).toHaveLength(1);
    expect(migrated.migrations[0]?.fromVersion).toBe("unknown");
  });

  it("migration stub passes-through valid v1 payload without migration", () => {
    const program = createPitchProgram();
    const migrated = migrateProgramToV1(program);

    expect(migrated.program.programId).toBe(program.programId);
    expect(migrated.migrations).toHaveLength(0);
  });

  it("parsing throws with explicit context", () => {
    const invalid = createPitchProgram({ programId: "" });

    expect(() => parsePitchProgram(invalid)).toThrow(/pitch-program/);
  });
});
