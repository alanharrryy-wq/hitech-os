import type { PitchPreset } from "./preset-neutral.js";

export const PRESET_INVESTOR: PitchPreset = {
  id: "investor",
  title: "Investor",
  description: "Narrative-forward sequencing tuned for decision meetings",
  directorMode: "full",
  transitionType: "crossfade",
  transitionMs: 700,
  easing: "easeOut",
  motionScale: 0.75,
  layerIntensity: 0.85
};
