import type { PitchPreset } from "./preset-neutral.js";

export const PRESET_MINIMAL: PitchPreset = {
  id: "minimal",
  title: "Minimal",
  description: "Lite transitions with overlays favored over motion",
  directorMode: "lite",
  transitionType: "fade",
  transitionMs: 250,
  easing: "easeIn",
  motionScale: 0.15,
  layerIntensity: 0.5
};
