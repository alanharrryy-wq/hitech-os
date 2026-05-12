import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const stackRecipe: PrismaChartVisualRecipe = {
  family: "stack",
  tokens: ["risk.low", "risk.medium", "risk.high", "risk.critical"],
  defaults: { barThickness: 14, stackGap: 4, labelVisibility: "auto", legendDensity: "compact" },
  surfaceOverrides: { mobile: { barThickness: 12, legendDensity: "minimal" }, pc: { legendDensity: "standard" } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "standard",
  motion: "safe"
};

