// PRISMA_CHART_LAB_V3_VERIFIER
import { read, exists, assert, report } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const required = [
  "src/prisma-charts/chart-lab-recipe-model.ts",
  "src/prisma-charts/chart-lab-power-presets.ts",
  "src/prisma-charts/chart-lab-target-profiles.ts",
  "src/prisma-charts/chart-lab-option-pipeline.ts",
  "src/prisma-charts/chart-lab-control-contracts.ts",
  "src/prisma-charts/chart-lab-guided-tour.ts",
  "src/prisma-charts/chart-lab-advanced-patch.ts"
];
for (const file of required) assert(exists(file), `Missing V3 runtime module ${file}`, failures);
const shell = read("src/components/PrismaChartLabShell.tsx");
const css = read("app/globals.css");
for (const token of ["studio-left-rail", "studio-canvas", "studio-right-rail", "single-chart-dropdown", "Power Studio", "Guided tour", "Copy recipe", "Copy option"]) assert(shell.includes(token) || css.includes(token), `Missing UI token ${token}`, failures);
report("chart-lab-checklist-coverage-v3", failures);
