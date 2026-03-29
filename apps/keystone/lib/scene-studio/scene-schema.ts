import { ALL_LAYERS, LAYER_DOM_SOURCE_VALUES, type LayerId } from "@hitech/ui-kit";
import { z } from "zod";
import {
  SCENE_LAYER_PROFILE_VALUES,
  SCENE_LAYERS_MODE_VALUES,
  SCENE_MOTION_VALUES,
  SCENE_SCHEMA_VERSION,
  SCENE_VIEWPORT_PRESETS,
  type SceneLayersMode,
  type SceneViewportPreset
} from "./scene-constants";
import { ensureSceneId, isSafeSceneId } from "./scene-id";
import { canonicalizeSceneQuery, parseLayersExpression } from "./scene-query";

const ISO_DATETIME_PATTERN =
  /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/;

const LAYER_ID_ENUM = z.enum(ALL_LAYERS as unknown as [LayerId, ...LayerId[]]);
type SceneQueryObjectInput = Record<string, string | string[]>;

const SCENE_QUERY_CANONICAL_SCHEMA = z.preprocess((value) => {
  if (typeof value === "string") {
    const raw = value.startsWith("?") ? value.slice(1) : value;
    return canonicalizeSceneQuery(new URLSearchParams(raw)).toString().replaceAll("%2C", ",");
  }

  if (value && typeof value === "object" && !Array.isArray(value)) {
    return canonicalizeSceneQuery(
      resolveSceneQuerySearchParams(value as SceneQueryObjectInput)
    )
      .toString()
      .replaceAll("%2C", ",");
  }

  return value;
}, z.string());

const SCENE_EXPECTATIONS_SCHEMA = z
  .object({
    minEnabledLayers: z.number().int().min(0).optional(),
    requiredLayers: z.array(LAYER_ID_ENUM).optional(),
    requiredDataAttributes: z.array(z.string().regex(/^data-layer-[a-z0-9-]+$/)).optional(),
    expectedSource: z.enum(LAYER_DOM_SOURCE_VALUES).optional(),
    expectedProfile: z.enum(SCENE_LAYER_PROFILE_VALUES).optional(),
    expectedMotion: z.enum(SCENE_MOTION_VALUES).optional()
  })
  .strict();

const SCENE_LAYERS_OVERRIDE_SCHEMA = z
  .object({
    mode: z.enum(SCENE_LAYERS_MODE_VALUES),
    layerIds: z.array(LAYER_ID_ENUM).default([])
  })
  .strict()
  .superRefine((value, context) => {
    if (value.mode === "list" && value.layerIds.length === 0) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: "layers.mode='list' requires at least one layer id"
      });
    }

    if (value.mode !== "list" && value.layerIds.length > 0) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: "layers.layerIds is only allowed when layers.mode='list'"
      });
    }
  });

const SCENE_VIEWPORT_SCHEMA = z
  .object({
    preset: z.enum(SCENE_VIEWPORT_PRESETS),
    width: z.number().int().min(320).max(3840).optional(),
    height: z.number().int().min(320).max(3840).optional()
  })
  .strict()
  .superRefine((value, context) => {
    if (value.preset === "custom") {
      if (typeof value.width !== "number" || typeof value.height !== "number") {
        context.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Custom viewport requires width and height"
        });
      }
      return;
    }

    if (value.width !== undefined || value.height !== undefined) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Width/height are only allowed for custom viewport"
      });
    }
  });

const SCENE_TAGS_SCHEMA = z
  .array(z.string().trim().min(1).max(32).regex(/^[a-z0-9-]+$/))
  .default([])
  .transform((tags) => Array.from(new Set(tags)).sort((left, right) => left.localeCompare(right)));

const SCENE_BASE_FIELDS = {
  id: z
    .string()
    .trim()
    .min(1)
    .max(120)
    .transform((value) => ensureSceneId(value))
    .refine((value) => isSafeSceneId(value), "Scene id must be kebab-case alphanumeric"),
  title: z.string().trim().min(1).max(180),
  route: z.string().trim().min(1).regex(/^\//, "Route must start with '/'."),
  query: SCENE_QUERY_CANONICAL_SCHEMA.default(""),
  viewport: SCENE_VIEWPORT_SCHEMA,
  layerProfile: z.enum(SCENE_LAYER_PROFILE_VALUES).default("neutral"),
  layers: SCENE_LAYERS_OVERRIDE_SCHEMA,
  motion: z.enum(SCENE_MOTION_VALUES).default("off"),
  notes: z.string().trim().max(1200).optional(),
  tags: SCENE_TAGS_SCHEMA,
  expectations: SCENE_EXPECTATIONS_SCHEMA.optional(),
  createdAt: z.string().regex(ISO_DATETIME_PATTERN, "createdAt must be UTC ISO timestamp"),
  updatedAt: z.string().regex(ISO_DATETIME_PATTERN, "updatedAt must be UTC ISO timestamp")
} as const;

export const SCENE_SCHEMA_V2 = z
  .object({
    schemaVersion: z.literal(SCENE_SCHEMA_VERSION),
    ...SCENE_BASE_FIELDS
  })
  .strict();

const LEGACY_LAYERS_V1_SCHEMA = z.union([
  z.literal("none"),
  z.literal("all"),
  z.array(z.string().trim().min(1))
]);

export const SCENE_SCHEMA_V1 = z
  .object({
    schemaVersion: z.literal(1).optional(),
    id: z.string().trim().min(1),
    title: z.string().trim().min(1),
    route: z.string().trim().min(1),
    query: z.string().optional(),
    viewport: z.enum(["desktop", "mobile", "tablet", "custom"]).optional(),
    customViewport: z
      .object({
        width: z.number().int().min(320),
        height: z.number().int().min(320)
      })
      .optional(),
    layerProfile: z.enum(SCENE_LAYER_PROFILE_VALUES).optional(),
    layers: LEGACY_LAYERS_V1_SCHEMA.optional(),
    motion: z.enum(SCENE_MOTION_VALUES).optional(),
    notes: z.string().optional(),
    tags: z.array(z.string()).optional(),
    createdAt: z.string().optional(),
    updatedAt: z.string().optional()
  })
  .strict();

export const SCENE_EXPORT_ENVELOPE_SCHEMA = z
  .object({
    schemaVersion: z.number().int().min(1),
    exportedAt: z.string().regex(ISO_DATETIME_PATTERN),
    scenes: z.array(z.unknown())
  })
  .strict();

export type SceneRecord = z.infer<typeof SCENE_SCHEMA_V2>;
export type SceneRecordInput = Omit<
  SceneRecord,
  "schemaVersion" | "query" | "createdAt" | "updatedAt"
> & {
  readonly schemaVersion?: number;
  readonly query?: string | SceneQueryObjectInput;
  readonly createdAt?: string;
  readonly updatedAt?: string;
};
export type LegacySceneRecord = z.infer<typeof SCENE_SCHEMA_V1>;

export interface SceneValidationError {
  readonly path: string;
  readonly message: string;
}

export interface SceneValidationResult {
  readonly ok: boolean;
  readonly scene?: SceneRecord;
  readonly errors: readonly SceneValidationError[];
}

function formatIssues(error: z.ZodError): SceneValidationError[] {
  return error.issues.map((issue) => ({
    path: issue.path.join("."),
    message: issue.message
  }));
}

export function resolveSceneQuerySearchParams(query: string | SceneQueryObjectInput): URLSearchParams {
  if (typeof query === "string") {
    return new URLSearchParams(query.startsWith("?") ? query.slice(1) : query);
  }

  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (Array.isArray(value)) {
      for (const entry of value) {
        params.append(key, entry);
      }
      continue;
    }

    params.append(key, value);
  }
  return params;
}

export function inferLayersFromQuery(query: string): {
  readonly mode: SceneLayersMode;
  readonly layerIds: readonly LayerId[];
  readonly unknownLayerTokens: readonly string[];
  readonly motionAliasOn: boolean;
} {
  const search = new URLSearchParams(query.startsWith("?") ? query.slice(1) : query);
  const layers = search.get("layers");
  if (!layers) {
    return {
      mode: "none",
      layerIds: [],
      unknownLayerTokens: [],
      motionAliasOn: false
    };
  }

  return parseLayersExpression(layers);
}

export function normalizeSceneInput(scene: SceneRecordInput): SceneRecordInput {
  const now = new Date().toISOString();
  const createdAt = scene.createdAt ?? now;
  const updatedAt = scene.updatedAt ?? now;

  const rawQuery = scene.query ?? "";
  const query =
    typeof rawQuery === "string"
      ? canonicalizeSceneQuery(
          new URLSearchParams(rawQuery.startsWith("?") ? rawQuery.slice(1) : rawQuery)
        )
          .toString()
          .replaceAll("%2C", ",")
      : canonicalizeSceneQuery(resolveSceneQuerySearchParams(rawQuery))
          .toString()
          .replaceAll("%2C", ",");

  return {
    ...scene,
    schemaVersion: SCENE_SCHEMA_VERSION,
    createdAt,
    updatedAt,
    query
  };
}

export function validateScene(input: unknown): SceneValidationResult {
  const parsed = SCENE_SCHEMA_V2.safeParse(input);
  if (!parsed.success) {
    return {
      ok: false,
      errors: formatIssues(parsed.error)
    };
  }

  return {
    ok: true,
    scene: parsed.data,
    errors: []
  };
}

export function parseSceneOrThrow(input: unknown): SceneRecord {
  return SCENE_SCHEMA_V2.parse(input);
}

export function parseSceneQuerySnapshot(input: string | Record<string, string | string[] | undefined>): string {
  if (typeof input === "string") {
    return canonicalizeSceneQuery(new URLSearchParams(input.startsWith("?") ? input.slice(1) : input))
      .toString()
      .replaceAll("%2C", ",");
  }

  return canonicalizeSceneQuery(new URLSearchParams(Object.entries(input).flatMap(([key, value]) => {
    if (Array.isArray(value)) {
      return value.map((entry) => [key, entry]);
    }

    if (typeof value === "string") {
      return [[key, value]];
    }

    return [];
  })))
    .toString()
    .replaceAll("%2C", ",");
}

export function coerceViewportPreset(value: string | undefined): SceneViewportPreset {
  if (!value) {
    return "desktop";
  }

  const normalized = value.trim();
  if ((SCENE_VIEWPORT_PRESETS as readonly string[]).includes(normalized)) {
    return normalized as SceneViewportPreset;
  }

  return "desktop";
}
