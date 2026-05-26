// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const pipeline = read("src/prisma-charts/chart-lab-option-pipeline.ts");
for (const token of ["buildChartLabOption", "applyChartLabControls", "applyTargetProfileToOption", "resolveChartLabVisualPreset", "resolveChartLabMotionPreset", "resolveChartLabInteractionPreset", "applyChartLabAdvancedPatch", "appliedLayers"]) assert(pipeline.includes(token), `Missing option pipeline token ${token}`, failures);
report("chart-lab-option-pipeline-v3", failures);
