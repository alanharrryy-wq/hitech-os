import type { DirectorCapabilityMode, PitchEasingType, PitchTransitionType } from "../contracts/program-types.js";

export interface PitchPreset {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly directorMode: DirectorCapabilityMode;
  readonly transitionType: PitchTransitionType;
  readonly transitionMs: number;
  readonly easing: PitchEasingType;
  readonly motionScale: number;
  readonly layerIntensity: number;
}

export const PRESET_NEUTRAL: PitchPreset = {
  id: "neutral",
  title: "Neutral",
  description: "Deterministic baseline with minimal motion",
  directorMode: "off",
  transitionType: "cut",
  transitionMs: 0,
  easing: "linear",
  motionScale: 0,
  layerIntensity: 1
};
