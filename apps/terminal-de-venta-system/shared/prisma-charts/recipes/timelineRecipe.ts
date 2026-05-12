import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const timelineRecipe: PrismaChartVisualRecipe = {
  family: "timeline",
  tokens: ["chart.line.premium", "status.partial", "risk.medium"],
  defaults: { markerSize: 12, lineSmoothness: 0.42, eventDensity: "standard", dateLabelDensity: "standard" },
  surfaceOverrides: { pc: { eventDensity: "standard" }, mobile: { eventDensity: "compact", markerSize: 8 } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "standard",
  motion: "safe"
};

