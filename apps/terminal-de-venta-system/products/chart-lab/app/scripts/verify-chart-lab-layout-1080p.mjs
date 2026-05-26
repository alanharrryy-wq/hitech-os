// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const css = read("app/globals.css");
for (const token of ["chart-lab-workbench", "studio-topbar", "studio-left-rail", "studio-canvas", "studio-right-rail", "100dvh", "minmax(0, 1fr)", "overflow"] ) assert(css.includes(token), `Missing layout/css token ${token}`, failures);
report("chart-lab-layout-1080p-v3", failures);
