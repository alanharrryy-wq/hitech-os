import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const waterfallRecipe: PrismaChartVisualRecipe = {
  family: "waterfall",
  tokens: ["risk.low", "risk.medium", "risk.critical", "chart.axis.subtle"],
  defaults: { connectorStyle: "subtle", totalBarEmphasis: true, labelFormatter: "currency", valueDensity: "executive" },
  surfaceOverrides: { pc: { valueDensity: "executive" }, tablet: { valueDensity: "compact" }, mobile: { valueDensity: "compact" } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "rich",
  motion: "safe"
};

