// PRISMA_CHART_LAB_V31_VISUAL_QA_CONTRACT
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";

const failures = [];
const shell = read("src/components/PrismaChartLabShell.tsx");
const frame = read("src/prisma-charts/components/LabEChartFrame.tsx");
const css = read("app/globals.css");
const source = `${shell}\n${frame}\n${css}`;

for (const token of [
  "PRISMA_CHART_LAB_V31_VISUAL_QA_FIX",
  "Chart rendered, but visible data looks too faint or empty.",
  "Clipboard blocked. Copy manually below.",
  "controls ·",
  "overrides",
  "studio-mobile-actions",
  "lab-echart__visibility-warning"
]) {
  assert(source.includes(token), `Missing V3.1 visual QA token: ${token}`, failures);
}

assert(!shell.includes("active knobs"), "Misleading active knobs copy is still visible in shell", failures);

report("chart-lab-v31-visual-qa-contract", failures);
