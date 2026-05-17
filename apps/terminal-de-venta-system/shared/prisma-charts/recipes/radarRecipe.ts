import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const radarRecipe: PrismaChartVisualRecipe = {
  family: "radar",
  tokens: ["chart.line.premium", "chart.area.crystal", "chart.point.accent"],
  defaults: { radius: "64%", axisNameWeight: 800, splitLineOpacity: 0.16, areaFillOpacity: 0.18, lineWidth: 3, pointGlow: true },
  surfaceOverrides: { mobile: { radius: "62%", axisNameWeight: 800 }, pc: { radius: "68%" } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "standard",
  motion: "safe"
};

