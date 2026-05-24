// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report, countMatches } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const tour = read("src/prisma-charts/chart-lab-guided-tour.ts");
for (const token of ["highlight", "showTip", "downplay", "hideTip", "dataZoom", "restore", "createDispatchActionPlan", "validateGuidedTourContracts"]) assert(tour.includes(token), `Missing guided tour action ${token}`, failures);
assert(countMatches(tour, /delayMs:/g) >= 5, "Expected multiple guided tour steps", failures);
report("chart-lab-guided-tour-contract-v3", failures);
