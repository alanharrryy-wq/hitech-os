// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report, countMatches } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const model = read("src/prisma-charts/chart-lab-control-model.ts");
const contracts = read("src/prisma-charts/chart-lab-control-contracts.ts");
assert(model.includes("export const chartControlSchemas"), "chartControlSchemas export missing", failures);
assert(countMatches(model, /powerTab:\s*"(visual|motion|interaction|labels|data|advanced)"/g) >= 16, "Expected at least 16 explicit powerTab assignments", failures);
for (const token of ["affectedLayer", "validation", "resetBehavior", "Potential ghost control", "validateChartLabControlContracts"]) assert((model + contracts).includes(token), `Missing control contract token ${token}`, failures);
report("chart-lab-control-contracts-v3", failures);
