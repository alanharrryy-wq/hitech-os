import type { PitchPreset } from "./preset-neutral.js";

export const PRESET_PERFORMANCE: PitchPreset = {
  id: "performance",
  title: "Performance",
  description: "Lite director mode with reduced rendering cost",
  directorMode: "lite",
  transitionType: "cut",
  transitionMs: 120,
  easing: "linear",
  motionScale: 0.3,
  layerIntensity: 0.6
};
