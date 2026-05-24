// PRISMA_CHART_LAB_V3_VERIFIER
import { exists, assert, report } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const required = [
"src/components/PrismaChartLabShell.tsx",
"src/components/ChartControlDeck.tsx",
"src/prisma-charts/chart-lab-control-model.ts",
"src/prisma-charts/chart-lab-types.ts",
"src/prisma-charts/components/LabEChartFrame.tsx",
"src/prisma-charts/chart-lab-recipe-model.ts",
"src/prisma-charts/chart-lab-power-presets.ts",
"src/prisma-charts/chart-lab-target-profiles.ts",
"src/prisma-charts/chart-lab-option-pipeline.ts",
"src/prisma-charts/chart-lab-control-contracts.ts",
"src/prisma-charts/chart-lab-guided-tour.ts",
"src/prisma-charts/chart-lab-advanced-patch.ts",
"app/globals.css"];
for (const file of required) assert(exists(file), `Missing installed file ${file}`, failures);
report("chart-lab-installed-files-v3", failures);
