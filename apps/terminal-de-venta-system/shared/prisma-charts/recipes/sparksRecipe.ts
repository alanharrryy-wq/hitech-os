import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const sparksRecipe: PrismaChartVisualRecipe = {
  family: "sparks",
  tokens: ["chart.line.premium", "risk.medium", "risk.critical"],
  defaults: { sparklineWidth: 3, areaFill: 0.1, endpointDot: true, deltaBadge: true, sparklineGlow: "controlled" },
  surfaceOverrides: { mobile: { sparklineWidth: 2, deltaBadge: true }, pc: { sparklineWidth: 3 } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "compact",
  motion: "subtle"
};

