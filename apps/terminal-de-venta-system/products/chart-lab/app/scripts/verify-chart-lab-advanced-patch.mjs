// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const advanced = read("src/prisma-charts/chart-lab-advanced-patch.ts");
for (const token of ["validateChartLabAdvancedPatch", "parseChartLabAdvancedPatch", "applyChartLabAdvancedPatch", "blockedKeys", "__proto__", "Function value is not allowed", "Invalid JSON"]) assert(advanced.includes(token), `Missing advanced patch token ${token}`, failures);
report("chart-lab-advanced-patch-v3", failures);
