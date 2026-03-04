import type { PitchPreset } from "./preset-neutral.js";

export const PRESET_CINEMATIC: PitchPreset = {
  id: "cinematic",
  title: "Cinematic",
  description: "Full director mode with layered motion and fades",
  directorMode: "full",
  transitionType: "fade",
  transitionMs: 900,
  easing: "easeInOut",
  motionScale: 1,
  layerIntensity: 1
};
