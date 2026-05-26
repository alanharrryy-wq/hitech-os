// PRISMA_CHART_LAB_V3_VERIFIER
import { read, assert, report } from "./verify-chart-lab-v3-helper.mjs";
const failures = [];
const frame = read("src/prisma-charts/components/LabEChartFrame.tsx");
for (const token of ["ResizeObserver", "resize", "dispose", "setOption", "tourSignal", "dispatchAction", "showTip"]) assert(frame.includes(token), `Missing ECharts frame token ${token}`, failures);
report("chart-lab-resize-contract-v3", failures);
