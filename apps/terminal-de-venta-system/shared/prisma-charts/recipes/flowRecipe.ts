import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const flowRecipe: PrismaChartVisualRecipe = {
  family: "flow",
  tokens: ["chart.line.premium", "risk.medium", "risk.critical"],
  defaults: { ribbonWidth: 14, ribbonOpacity: 0.42, nodeSpacing: 12, tooltipDensity: "rich" },
  surfaceOverrides: { pc: { tooltipDensity: "rich" }, tablet: { ribbonWidth: 10 }, mobile: { ribbonWidth: 8 } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "rich",
  motion: "safe"
};

