import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const networkRecipe: PrismaChartVisualRecipe = {
  family: "network",
  tokens: ["status.live", "status.partial", "risk.critical"],
  defaults: { nodeSize: 46, edgeThickness: 2, edgeOpacity: 0.72, criticalHalo: true, layoutForce: 210 },
  surfaceOverrides: { pc: { nodeSize: 50 }, tablet: { nodeSize: 38 }, mobile: { nodeSize: 34 } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "standard",
  motion: "safe"
};

