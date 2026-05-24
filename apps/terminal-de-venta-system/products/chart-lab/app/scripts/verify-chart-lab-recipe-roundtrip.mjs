// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const recipe = read("src/prisma-charts/chart-lab-recipe-model.ts");
for (const token of ["CHART_LAB_RECIPE_VERSION", "createChartLabRecipe", "serializeChartLabRecipe", "parseChartLabRecipe", "roundTripChartLabRecipe", "validateChartLabRecipe", "manualOverrides", "advancedPatch"]) assert(recipe.includes(token), `Missing recipe token ${token}`, failures);
assert(recipe.includes("recipeVersion: ChartLabRecipeVersion"), "Recipe version is not strongly typed", failures);
report("chart-lab-recipe-roundtrip-v3", failures);
