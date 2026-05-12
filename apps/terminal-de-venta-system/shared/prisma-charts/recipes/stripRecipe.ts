import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const stripRecipe: PrismaChartVisualRecipe = {
  family: "strip",
  tokens: ["status.live", "status.partial", "status.offline"],
  defaults: { segmentHeight: 28, gap: 6, timeTickDensity: "compact", touchTargetSize: 44 },
  surfaceOverrides: { tablet: { touchTargetSize: 52 }, mobile: { segmentHeight: 22 } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "compact",
  motion: "subtle"
};

