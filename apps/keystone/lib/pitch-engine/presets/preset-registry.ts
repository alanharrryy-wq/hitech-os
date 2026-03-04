import type { PitchPreset } from "./preset-neutral.js";
import { PRESET_NEUTRAL } from "./preset-neutral.js";
import { PRESET_CINEMATIC } from "./preset-cinematic.js";
import { PRESET_INVESTOR } from "./preset-investor.js";
import { PRESET_PERFORMANCE } from "./preset-performance.js";
import { PRESET_MINIMAL } from "./preset-minimal.js";
import { PRESET_DEBUG } from "./preset-debug.js";

export const PITCH_PRESET_REGISTRY: Readonly<Record<string, PitchPreset>> = {
  cinematic: PRESET_CINEMATIC,
  investor: PRESET_INVESTOR,
  performance: PRESET_PERFORMANCE,
  minimal: PRESET_MINIMAL,
  debug: PRESET_DEBUG,
  neutral: PRESET_NEUTRAL
};

export const PITCH_PRESET_ORDER = [
  "cinematic",
  "investor",
  "performance",
  "minimal",
  "debug",
  "neutral"
] as const;

export type PitchPresetId = (typeof PITCH_PRESET_ORDER)[number];

export function listPitchPresets(): readonly PitchPreset[] {
  return PITCH_PRESET_ORDER.map((id) => PITCH_PRESET_REGISTRY[id]);
}

export function getPitchPreset(id: string | undefined): PitchPreset {
  if (id && PITCH_PRESET_REGISTRY[id]) {
    return PITCH_PRESET_REGISTRY[id];
  }

  return PRESET_NEUTRAL;
}

export function resolvePresetChain(input: {
  readonly stepPresetId?: string;
  readonly programDefaultPresetId?: string;
}): PitchPreset {
  return getPitchPreset(input.stepPresetId ?? input.programDefaultPresetId ?? "neutral");
}

export function hasPreset(id: string): boolean {
  return Boolean(PITCH_PRESET_REGISTRY[id]);
}
