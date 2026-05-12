import { chartOpsIds, fail, pass, read } from "./chart-lab-script-utils.mjs";

const controls = read("src/prisma-charts/chart-lab-control-model.ts");
const shell = read("src/components/PrismaChartLabShell.tsx");
const deck = read("src/components/ChartControlDeck.tsx");
const requiredTypes = ["segmented", "select", "chip-group", "toggle", "range", "numeric", "search"];
const chartIds = chartOpsIds();

for (const id of chartIds) {
  if (controls.includes(`"${id}"`)) pass(`control schema exists: ${id}`);
  else fail(`missing control schema: ${id}`);
}

for (const type of requiredTypes) {
  if (controls.includes(`"${type}"`) || deck.includes(`"${type}"`)) pass(`control type supported: ${type}`);
  else fail(`missing control type support: ${type}`);
}

for (const needle of [
  "severityFilter",
  "confidenceFloor",
  "ribbonWidth",
  "ribbonOpacity",
  "showLabels",
  "animation",
  "detailLevel",
  "stageFocus",
  "layoutDensity",
  "evidenceMode"
]) {
  if (controls.includes(needle)) pass(`Causal Flow Ribbon control present: ${needle}`);
  else fail(`missing Causal Flow Ribbon control: ${needle}`);
}

const workingTransforms = [
  "applyCausalControls",
  "series.nodeWidth",
  "lineStyle.opacity",
  "applyScenario",
  "filterNumericSeriesData",
  "applySeriesLabels",
  "applyVisualIntensity"
];
for (const needle of workingTransforms) {
  if (controls.includes(needle)) pass(`runtime transform wired: ${needle}`);
  else fail(`runtime transform missing: ${needle}`);
}

for (const needle of ["Copy Current Config JSON", "Reset current chart", "Reset all", "Control Summary", "ChartControlDeck"]) {
  if (shell.includes(needle)) pass(`UI control affordance present: ${needle}`);
  else fail(`missing UI control affordance: ${needle}`);
}

if (!process.exitCode) pass("controls verification complete");
