// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const files = [
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
for (const file of files) assert(read(file).includes("PRISMA_CHART_LAB") || file.endsWith("globals.css"), `${file} missing PRISMA marker`, failures);
const shell = read("src/components/PrismaChartLabShell.tsx");
assert(!shell.includes("Focus Mode"), "Focus Mode concept leaked back into shell", failures);
report("chart-lab-v3-final-gates", failures);
