// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const profiles = read("src/prisma-charts/chart-lab-target-profiles.ts");
for (const token of ["pc", "tablet", "mobile", "maxLabelDensity", "animationScale", "tooltipMode", "applyTargetProfileToOption", "validateChartLabTargetProfiles"]) assert(profiles.includes(token), `Missing target profile token ${token}`, failures);
report("chart-lab-target-profiles-v3", failures);
