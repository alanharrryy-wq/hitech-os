import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const ringsRecipe: PrismaChartVisualRecipe = {
  family: "rings",
  tokens: ["status.live", "status.stale", "status.offline", "status.unknown"],
  defaults: { ringThickness: 10, ringGap: 4, centerLabelSize: 14, staleEmphasis: true },
  surfaceOverrides: { mobile: { ringThickness: 8, centerLabelSize: 13 }, pc: { ringThickness: 12 } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "compact",
  motion: "subtle"
};

