import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const bandsRecipe: PrismaChartVisualRecipe = {
  family: "bands",
  tokens: ["status.live", "status.partial", "status.unknown"],
  defaults: { bandHeight: 14, trackOpacity: 0.18, fillGradient: true, handleSize: 0, percentagePillStyle: "inline" },
  surfaceOverrides: { mobile: { bandHeight: 12, percentagePillStyle: "inline" }, pc: { bandHeight: 16 } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "standard",
  motion: "safe"
};

