import { z } from "zod";
import { PitchSceneRefSchema } from "../contracts/program-schema.js";
import { isIsoUtcString } from "../shared/deterministic.js";
import { formatValidationMessage, normalizeZodIssues, parseOrThrow, parseWithSchema } from "../shared/validation.js";
import {
  isTrackKeyAllowed,
  SEQUENCE_EASINGS,
  SEQUENCE_SCHEMA_VERSION,
  SEQUENCE_TRACKS,
  type SequenceKey,
  type SequenceTrack
} from "./dsl.js";
import type {
  DirectorSequence,
  DirectorSequenceV1,
  SequenceValidationResult
} from "./sequence-types.js";

const Identifier = z
  .string()
  .min(1)
  .max(96)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._:-]*$/, "Must be a stable identifier");

const IsoUtcString = z
  .string()
  .refine((value) => isIsoUtcString(value), "Must be a UTC ISO-8601 timestamp");

const ValueSchema = z.union([
  z.string().max(400),
  z.number().finite(),
  z.boolean(),
  z.null(),
  z.array(z.string().max(120)).max(128),
  z
    .object({
      value: z.union([z.string().max(120), z.number().finite(), z.boolean()]),
      unit: z.string().max(24).optional()
    })
    .strict()
]);

export const SequenceKeyframeSchema = z
  .object({
    tMs: z.number().int().min(0).max(120_000),
    track: z.enum(SEQUENCE_TRACKS),
    key: Identifier,
    value: ValueSchema,
    easing: z.enum(SEQUENCE_EASINGS)
  })
  .strict()
  .superRefine((keyframe, ctx) => {
    if (!isTrackKeyAllowed(keyframe.track as SequenceTrack, keyframe.key)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["key"],
        message: `Key '${keyframe.key}' is not allowed for track '${keyframe.track}'`
      });
    }
  });

export const SequenceMarkerSchema = z
  .object({
    tMs: z.number().int().min(0).max(120_000),
    label: z.string().min(1).max(120)
  })
  .strict();

export const SequenceTimelineDslSchema = z
  .object({
    tracks: z.array(z.enum(SEQUENCE_TRACKS)).min(1).max(SEQUENCE_TRACKS.length),
    keyframes: z.array(SequenceKeyframeSchema).max(8_000),
    markers: z.array(SequenceMarkerSchema).max(1_000)
  })
  .strict()
  .superRefine((timeline, ctx) => {
    const uniqueTracks = new Set(timeline.tracks);
    if (uniqueTracks.size !== timeline.tracks.length) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["tracks"],
        message: "timelineDSL.tracks must not contain duplicates"
      });
    }

    const trackSet = new Set(timeline.tracks);

    let lastTime = -1;
    const keyframeSignatures = new Set<string>();

    for (let index = 0; index < timeline.keyframes.length; index += 1) {
      const keyframe = timeline.keyframes[index];
      if (!keyframe) {
        continue;
      }

      if (!trackSet.has(keyframe.track)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["keyframes", index, "track"],
          message: `Track '${keyframe.track}' is not declared in timelineDSL.tracks`
        });
      }

      if (keyframe.tMs < lastTime) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["keyframes", index, "tMs"],
          message: "timelineDSL.keyframes must be sorted by tMs"
        });
      }

      lastTime = keyframe.tMs;

      const signature = `${keyframe.tMs}:${keyframe.track}:${keyframe.key}`;
      if (keyframeSignatures.has(signature)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["keyframes", index],
          message: `Duplicate keyframe for ${signature}`
        });
      }
      keyframeSignatures.add(signature);
    }

    const markerSignatures = new Set<string>();
    for (let index = 0; index < timeline.markers.length; index += 1) {
      const marker = timeline.markers[index];
      if (!marker) {
        continue;
      }

      const signature = `${marker.tMs}:${marker.label}`;
      if (markerSignatures.has(signature)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["markers", index],
          message: `Duplicate marker '${signature}'`
        });
      }
      markerSignatures.add(signature);
    }
  });

export const SequenceRulesSchema = z
  .object({
    motionBudget: z
      .object({
        maxHeroMotions: z.number().int().min(0).max(12).default(1),
        maxTrackKeyframes: z.number().int().min(1).max(2_000)
      })
      .strict(),
    reducedMotion: z
      .object({
        strategy: z.literal("jumpToFinal")
      })
      .strict(),
    perfDegrade: z
      .object({
        strategy: z.literal("lite")
      })
      .strict()
  })
  .strict();

export const DirectorSequenceSchema: z.ZodType<DirectorSequenceV1> = z
  .object({
    sequenceId: Identifier,
    schemaVersion: z.literal(SEQUENCE_SCHEMA_VERSION),
    createdAt: IsoUtcString,
    updatedAt: IsoUtcString,
    baseSceneRef: PitchSceneRefSchema,
    timelineDSL: SequenceTimelineDslSchema,
    rules: SequenceRulesSchema
  })
  .strict()
  .superRefine((sequence, ctx) => {
    const createdAtMs = Date.parse(sequence.createdAt);
    const updatedAtMs = Date.parse(sequence.updatedAt);
    if (Number.isFinite(createdAtMs) && Number.isFinite(updatedAtMs) && updatedAtMs < createdAtMs) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["updatedAt"],
        message: "updatedAt must be greater than or equal to createdAt"
      });
    }

    if (sequence.rules.motionBudget.maxTrackKeyframes < sequence.timelineDSL.keyframes.length) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["rules", "motionBudget", "maxTrackKeyframes"],
        message: "maxTrackKeyframes cannot be less than the number of keyframes in the sequence"
      });
    }
  });

export function validateSequence(input: unknown): SequenceValidationResult {
  const parsed = parseWithSchema(DirectorSequenceSchema, input);

  if (parsed.ok) {
    return {
      ok: true,
      sequence: parsed.data as DirectorSequence,
      errors: []
    };
  }

  return {
    ok: false,
    errors: parsed.errors
  };
}

export function parseSequence(input: unknown): DirectorSequence {
  return parseOrThrow(DirectorSequenceSchema, input, "pitch-sequence");
}

export function formatSequenceValidationErrors(input: unknown): string {
  const parsed = DirectorSequenceSchema.safeParse(input);
  if (parsed.success) {
    return "valid";
  }

  return formatValidationMessage(normalizeZodIssues(parsed.error));
}

export function assertSequenceKeyIsDeterministic(track: SequenceTrack, key: string): key is SequenceKey {
  return isTrackKeyAllowed(track, key);
}
