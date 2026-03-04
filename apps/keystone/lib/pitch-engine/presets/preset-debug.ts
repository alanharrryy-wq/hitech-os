import type { PitchPreset } from "./preset-neutral.js";

export const PRESET_DEBUG: PitchPreset = {
  id: "debug",
  title: "Debug",
  description: "Debug mode keeps transitions deterministic while exposing overlays",
  directorMode: "debug",
  transitionType: "wipe",
  transitionMs: 300,
  easing: "linear",
  motionScale: 0.5,
  layerIntensity: 1
};
