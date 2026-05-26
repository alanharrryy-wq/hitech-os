// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report, countMatches } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const model = read("src/prisma-charts/chart-lab-control-model.ts");
const controlCount = countMatches(model, /id:\s*"[^"]+"/g);
const affectedCount = countMatches(model, /affected(OptionPath|DataTransform|Layer):/g);
assert(controlCount >= 40, `Expected broad control inventory, got ${controlCount}`, failures);
assert(affectedCount >= controlCount, `Every control should have affected contract. controls=${controlCount} affected=${affectedCount}`, failures);
assert(model.includes("applyChartLabControls"), "applyChartLabControls missing", failures);
report("chart-lab-no-ghost-controls-v3", failures);
