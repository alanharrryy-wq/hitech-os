import type { PrismaChartVisualRecipe } from "./recipeTypes";

export const matrixRecipe: PrismaChartVisualRecipe = {
  family: "matrix",
  tokens: ["status.live", "status.partial", "risk.critical"],
  defaults: { cellSize: 30, statusIconStyle: "text", rowDensity: "standard", columnDensity: "standard", offlineEmphasis: true },
  surfaceOverrides: { tablet: { cellSize: 40, rowDensity: "touch" }, mobile: { cellSize: 26, rowDensity: "compact" } },
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: "compact",
  motion: "subtle"
};

