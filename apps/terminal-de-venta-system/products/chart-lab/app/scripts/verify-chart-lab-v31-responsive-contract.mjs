// PRISMA_CHART_LAB_V31_RESPONSIVE_CONTRACT
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";

const failures = [];
const css = read("app/globals.css");

for (const token of [
  "@media (max-width: 720px)",
  "@media (max-width: 1120px)",
  ".studio-mobile-actions",
  ".power-tabs",
  "overflow-x",
  ".lab-echart__canvas",
  "z-index",
  ".lab-echart__visibility-warning"
]) {
  assert(css.includes(token), `Missing V3.1 responsive token: ${token}`, failures);
}

assert(css.includes("grid-template-areas") && css.includes("chart") && css.includes("target"), "Mobile topbar must keep chart selector and target controls visible", failures);
assert(css.includes("flex-wrap: nowrap") && css.includes("text-overflow: ellipsis"), "Power tabs need narrow-width protection", failures);

report("chart-lab-v31-responsive-contract", failures);
