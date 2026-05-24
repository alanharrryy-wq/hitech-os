// PRISMA_CHART_LAB_V31_NONBLANK_CHART_CONTRACT
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";

const failures = [];
const frame = read("src/prisma-charts/components/LabEChartFrame.tsx");
const pipeline = read("src/prisma-charts/chart-lab-option-pipeline.ts");
const presets = read("src/prisma-charts/chart-lab-power-presets.ts");
const source = `${frame}\n${pipeline}\n${presets}`;

for (const token of [
  "getVisibleSeriesSummary",
  "applyChartLabVisibilityGuard",
  "data-chart-visible-series-count",
  "data-chart-suspected-blank",
  "minSeriesOpacity",
  "minLineOpacity",
  "requestAnimationFrame",
  "setTimeout"
]) {
  assert(source.includes(token), `Missing V3.1 nonblank chart token: ${token}`, failures);
}

assert(frame.includes("hasDatasetData") && frame.includes("suspectedBlankChart: !hasDirectDatasetData"), "Dataset-backed charts must not be marked blank", failures);
assert(pipeline.includes("0.38") && pipeline.includes("0.48") && pipeline.includes("0.18"), "Visibility guard minimums are incomplete", failures);
assert(pipeline.includes("0.52"), "Sankey line opacity floor is missing", failures);

report("chart-lab-v31-nonblank-chart-contract", failures);
