"use client";

export type SceneLookBackground = "neutral" | "gradient" | "cinematic";
export type SceneLookStageStyle = "default" | "cinematic" | "minimal";
export type SceneLookCardStyle = "default" | "glass" | "solid";
export type SceneLookMotion = "off" | "on" | "reduced";
export type SceneLookDensity = "comfortable" | "compact";

export interface SceneLookModel {
  readonly background: SceneLookBackground;
  readonly overlays: {
    readonly grid: boolean;
    readonly safeAreas: boolean;
    readonly debugLabels: boolean;
  };
  readonly visualEffects: {
    readonly bloom: boolean;
    readonly grain: boolean;
    readonly vignette: boolean;
  };
  readonly stageStyle: SceneLookStageStyle;
  readonly cardStyle: SceneLookCardStyle;
  readonly motion: SceneLookMotion;
  readonly density: SceneLookDensity;
}

export type SceneLookModelPatch = Omit<Partial<SceneLookModel>, "overlays" | "visualEffects"> & {
  overlays?: Partial<SceneLookModel["overlays"]>;
  visualEffects?: Partial<SceneLookModel["visualEffects"]>;
};

export const DEFAULT_SCENE_LOOK_MODEL: SceneLookModel = {
  background: "neutral",
  overlays: {
    grid: false,
    safeAreas: false,
    debugLabels: false
  },
  visualEffects: {
    bloom: false,
    grain: false,
    vignette: false
  },
  stageStyle: "default",
  cardStyle: "default",
  motion: "off",
  density: "comfortable"
};

const BACKGROUND_VALUES = new Set<SceneLookBackground>(["neutral", "gradient", "cinematic"]);
const STAGE_STYLE_VALUES = new Set<SceneLookStageStyle>(["default", "cinematic", "minimal"]);
const CARD_STYLE_VALUES = new Set<SceneLookCardStyle>(["default", "glass", "solid"]);
const MOTION_VALUES = new Set<SceneLookMotion>(["off", "on", "reduced"]);
const DENSITY_VALUES = new Set<SceneLookDensity>(["comfortable", "compact"]);

function readBoolean(value: unknown, fallback: boolean): boolean {
  if (typeof value === "boolean") {
    return value;
  }
  return fallback;
}

function readFromSet<T extends string>(value: unknown, allowed: ReadonlySet<T>, fallback: T): T {
  if (typeof value === "string" && allowed.has(value as T)) {
    return value as T;
  }
  return fallback;
}

export function normalizeSceneLookModel(input: unknown): SceneLookModel {
  if (!input || typeof input !== "object") {
    return DEFAULT_SCENE_LOOK_MODEL;
  }

  const candidate = input as Partial<SceneLookModel>;
  const overlays = (candidate.overlays ?? {}) as Partial<SceneLookModel["overlays"]>;
  const visualEffects = (candidate.visualEffects ?? {}) as Partial<SceneLookModel["visualEffects"]>;

  return {
    background: readFromSet(candidate.background, BACKGROUND_VALUES, DEFAULT_SCENE_LOOK_MODEL.background),
    overlays: {
      grid: readBoolean(overlays.grid, DEFAULT_SCENE_LOOK_MODEL.overlays.grid),
      safeAreas: readBoolean(overlays.safeAreas, DEFAULT_SCENE_LOOK_MODEL.overlays.safeAreas),
      debugLabels: readBoolean(overlays.debugLabels, DEFAULT_SCENE_LOOK_MODEL.overlays.debugLabels)
    },
    visualEffects: {
      bloom: readBoolean(visualEffects.bloom, DEFAULT_SCENE_LOOK_MODEL.visualEffects.bloom),
      grain: readBoolean(visualEffects.grain, DEFAULT_SCENE_LOOK_MODEL.visualEffects.grain),
      vignette: readBoolean(visualEffects.vignette, DEFAULT_SCENE_LOOK_MODEL.visualEffects.vignette)
    },
    stageStyle: readFromSet(candidate.stageStyle, STAGE_STYLE_VALUES, DEFAULT_SCENE_LOOK_MODEL.stageStyle),
    cardStyle: readFromSet(candidate.cardStyle, CARD_STYLE_VALUES, DEFAULT_SCENE_LOOK_MODEL.cardStyle),
    motion: readFromSet(candidate.motion, MOTION_VALUES, DEFAULT_SCENE_LOOK_MODEL.motion),
    density: readFromSet(candidate.density, DENSITY_VALUES, DEFAULT_SCENE_LOOK_MODEL.density)
  };
}

export function isSceneLookModel(value: unknown): value is SceneLookModel {
  if (!value || typeof value !== "object") {
    return false;
  }
  const normalized = normalizeSceneLookModel(value);
  return JSON.stringify(normalized) === JSON.stringify(value);
}

export function mergeSceneLookModel(
  base: SceneLookModel,
  patch: SceneLookModelPatch | ((previous: SceneLookModel) => SceneLookModelPatch)
): SceneLookModel {
  const nextPatch = typeof patch === "function" ? patch(base) : patch;
  return normalizeSceneLookModel({
    ...base,
    ...nextPatch,
    overlays: {
      ...base.overlays,
      ...(nextPatch.overlays ?? {})
    },
    visualEffects: {
      ...base.visualEffects,
      ...(nextPatch.visualEffects ?? {})
    }
  });
}

export function sceneLookModelToDatasetEntries(model: SceneLookModel): Readonly<Record<string, string>> {
  const overlays = [
    model.overlays.grid ? "grid" : null,
    model.overlays.safeAreas ? "safe-areas" : null,
    model.overlays.debugLabels ? "debug-labels" : null
  ].filter((value): value is string => Boolean(value));

  const effects = [
    model.visualEffects.bloom ? "bloom" : null,
    model.visualEffects.grain ? "grain" : null,
    model.visualEffects.vignette ? "vignette" : null
  ].filter((value): value is string => Boolean(value));

  return {
    sceneLookBackground: model.background,
    sceneLookOverlays: overlays.join(","),
    sceneLookEffects: effects.join(","),
    sceneLookStageStyle: model.stageStyle,
    sceneLookCardStyle: model.cardStyle,
    sceneLookMotion: model.motion,
    sceneLookDensity: model.density
  };
}

export function applySceneLookModelToElement(
  element: Pick<HTMLElement, "dataset">,
  model: SceneLookModel
): void {
  const entries = sceneLookModelToDatasetEntries(model);
  for (const [key, value] of Object.entries(entries)) {
    element.dataset[key] = value;
  }
}
