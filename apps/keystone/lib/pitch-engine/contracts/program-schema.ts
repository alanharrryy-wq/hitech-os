import { z } from "zod";
import {
  DIRECTOR_MODES,
  EASING_TYPES,
  PRESET_IDS,
  PITCH_PROGRAM_SCHEMA_VERSION,
  TRANSITION_TYPES,
  type PitchProgram,
  type PitchProgramV1,
  type ProgramValidationResult,
  type PitchSceneRef,
  type SceneRecord
} from "./program-types.js";
import {
  formatValidationMessage,
  normalizeZodIssues,
  parseOrThrow,
  parseWithSchema,
  type PitchEngineValidationError
} from "../shared/validation.js";
import { isIsoUtcString } from "../shared/deterministic.js";

const Identifier = z
  .string()
  .min(1)
  .max(96)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._:-]*$/, "Must be a stable identifier");

const HumanLabel = z.string().min(1).max(240);
const LongLabel = z.string().min(1).max(2_000);

const SceneViewportSchema = z
  .object({
    width: z.number().int().min(320).max(8_192),
    height: z.number().int().min(240).max(8_192),
    deviceScaleFactor: z.number().min(0.5).max(4).optional()
  })
  .strict();

const SceneMotionSchema = z
  .object({
    enabled: z.boolean(),
    intensity: z.enum(["none", "low", "medium", "high"]),
    reducedMotionPolicy: z.enum(["respect", "ignore"]).optional()
  })
  .strict();

export const SceneRecordSchema: z.ZodType<SceneRecord> = z
  .object({
    sceneId: Identifier,
    route: z.string().min(1).max(256).regex(/^\//, "Route must start with '/'") ,
    query: z.record(z.string().max(120), z.string().max(240)),
    viewport: SceneViewportSchema,
    profile: z.enum(PRESET_IDS),
    layers: z.array(Identifier).max(128),
    motion: SceneMotionSchema
  })
  .strict();

const SceneRefByIdSchema = z
  .object({
    type: z.literal("sceneId"),
    sceneId: Identifier
  })
  .strict();

const SceneRefInlineSchema = z
  .object({
    type: z.literal("inlineScene"),
    scene: SceneRecordSchema
  })
  .strict();

export const PitchSceneRefSchema: z.ZodType<PitchSceneRef> = z.discriminatedUnion("type", [
  SceneRefByIdSchema,
  SceneRefInlineSchema
]);

export const PitchStepTransitionSchema = z
  .object({
    type: z.enum(TRANSITION_TYPES),
    ms: z.number().int().min(0).max(15_000),
    easing: z.enum(EASING_TYPES)
  })
  .strict();

export const PitchStepSchema = z
  .object({
    stepId: Identifier,
    title: HumanLabel,
    label: HumanLabel.optional(),
    sceneRef: PitchSceneRefSchema,
    durationMs: z.number().int().min(250).max(120_000),
    transition: PitchStepTransitionSchema,
    presetId: z.enum(PRESET_IDS).optional(),
    markers: z.array(HumanLabel).max(32).optional(),
    director: z
      .object({
        sequenceId: Identifier.optional(),
        apply: z.boolean().optional()
      })
      .strict()
      .optional(),
    expectations: z
      .object({
        requiredDataAttributes: z.array(z.string().min(1).max(96)).max(64).optional(),
        requiredLayers: z.array(Identifier).max(64).optional(),
        minEnabledLayers: z.number().int().min(0).max(64).optional()
      })
      .strict()
      .optional()
  })
  .strict();

export const PitchChapterMarkerSchema = z
  .object({
    chapterId: Identifier,
    label: HumanLabel,
    stepId: Identifier
  })
  .strict();

const IsoUtcString = z
  .string()
  .refine((value) => isIsoUtcString(value), "Must be a UTC ISO-8601 timestamp");

export const PitchProgramSchema: z.ZodType<PitchProgramV1> = z
  .object({
    schemaVersion: z.literal(PITCH_PROGRAM_SCHEMA_VERSION),
    programId: Identifier,
    title: HumanLabel,
    description: LongLabel.optional(),
    tags: z.array(Identifier).max(128),
    createdAt: IsoUtcString,
    updatedAt: IsoUtcString,
    defaultPresetId: z.enum(PRESET_IDS).optional(),
    chapters: z.array(PitchChapterMarkerSchema).max(256).optional(),
    steps: z.array(PitchStepSchema).min(1).max(1_000),
    capabilityRequest: z
      .object({
        director: z.enum(DIRECTOR_MODES)
      })
      .strict()
      .optional(),
    metadata: z
      .object({
        source: z.string().min(1).max(400).optional(),
        gitHash: z.string().min(7).max(64).optional(),
        notes: z.string().min(1).max(2_000).optional()
      })
      .strict()
      .optional()
  })
  .strict()
  .superRefine((program, ctx) => {
    const seenSteps = new Set<string>();

    for (let index = 0; index < program.steps.length; index += 1) {
      const step = program.steps[index];
      if (!step) {
        continue;
      }

      if (seenSteps.has(step.stepId)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["steps", index, "stepId"],
          message: `Duplicate stepId '${step.stepId}'`
        });
      }
      seenSteps.add(step.stepId);

      if (step.expectations?.minEnabledLayers !== undefined) {
        const requiredLayers = step.expectations.requiredLayers ?? [];
        if (step.expectations.minEnabledLayers > requiredLayers.length && requiredLayers.length > 0) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ["steps", index, "expectations", "minEnabledLayers"],
            message: "minEnabledLayers cannot exceed requiredLayers length"
          });
        }
      }

      if (step.director?.sequenceId && step.director.apply === false) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["steps", index, "director"],
          message: "director.apply=false cannot be combined with sequenceId"
        });
      }
    }

    if (program.chapters) {
      const seenChapters = new Set<string>();
      for (let index = 0; index < program.chapters.length; index += 1) {
        const chapter = program.chapters[index];
        if (!chapter) {
          continue;
        }

        if (seenChapters.has(chapter.chapterId)) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ["chapters", index, "chapterId"],
            message: `Duplicate chapterId '${chapter.chapterId}'`
          });
        }
        seenChapters.add(chapter.chapterId);

        if (!seenSteps.has(chapter.stepId)) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ["chapters", index, "stepId"],
            message: `Chapter references unknown stepId '${chapter.stepId}'`
          });
        }
      }
    }

    const createdAtMs = Date.parse(program.createdAt);
    const updatedAtMs = Date.parse(program.updatedAt);
    if (Number.isFinite(createdAtMs) && Number.isFinite(updatedAtMs) && updatedAtMs < createdAtMs) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["updatedAt"],
        message: "updatedAt must be greater than or equal to createdAt"
      });
    }
  });

export function validatePitchProgram(input: unknown): ProgramValidationResult {
  const result = parseWithSchema(PitchProgramSchema, input);
  if (result.ok) {
    return {
      ok: true,
      program: result.data as PitchProgram,
      errors: []
    };
  }

  return {
    ok: false,
    errors: result.errors
  };
}

export function parsePitchProgram(input: unknown): PitchProgram {
  return parseOrThrow(PitchProgramSchema, input, "pitch-program");
}

export function formatProgramValidationErrors(input: unknown): string {
  const parsed = PitchProgramSchema.safeParse(input);
  if (parsed.success) {
    return "valid";
  }

  return formatValidationMessage(normalizeZodIssues(parsed.error));
}

export type ProgramSchemaValidationError = PitchEngineValidationError;
