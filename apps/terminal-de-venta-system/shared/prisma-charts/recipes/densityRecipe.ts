import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const densityRecipe: PrismaChartVisualRecipe = {
  family: "density",
  tokens: ["chart.grid.soft", "status.partial", "risk.critical"],
  defaults: { heatIntensity: 1, cellRadius: 6, gridOpacity: 0.22, timeLabelDensity: "standard" },
  surfaceOverrides: { pc: { timeLabelDensity: "standard" }, tablet: { timeLabelDensity: "compact" }, mobile: { timeLabelDensity: "compact" } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "standard",
  motion: "safe"
};

