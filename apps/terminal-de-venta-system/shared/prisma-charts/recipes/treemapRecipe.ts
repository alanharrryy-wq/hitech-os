import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const treemapRecipe: PrismaChartVisualRecipe = {
  family: "treemap",
  tokens: ["risk.low", "risk.medium", "risk.critical"],
  defaults: { tilePadding: 4, labelDensity: "standard", breadcrumbDepth: 1, impactEmphasis: true },
  surfaceOverrides: { pc: { labelDensity: "standard" }, tablet: { labelDensity: "compact" }, mobile: { labelDensity: "compact" } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "rich",
  motion: "safe"
};

