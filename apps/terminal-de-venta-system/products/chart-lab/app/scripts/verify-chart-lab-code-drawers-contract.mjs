// PRISMA_CHART_LAB_CODE_DRAWERS_CONTRACT_V1
import { assert, exists, read, report } from "./verify-chart-lab-v3-helper.mjs";

const failures = [];

const drawerPath = "src/prisma-charts/chart-lab-code-drawers.ts";
assert(exists(drawerPath), "chart-lab-code-drawers.ts exists", failures);

const drawers = exists(drawerPath) ? read(drawerPath) : "";
const shell = read("src/components/PrismaChartLabShell.tsx");
const deck = read("src/components/ChartControlDeck.tsx");
const pipeline = read("src/prisma-charts/chart-lab-option-pipeline.ts");
const types = read("src/prisma-charts/chart-lab-types.ts");

const requiredDrawerIds = [
  "baseOptionPatch",
  "seriesPatch",
  "itemStylePatch",
  "lineStylePatch",
  "areaStylePatch",
  "labelPatch",
  "visualMapPatch",
  "graphicOverlayPatch",
  "datasetPatch",
  "animationPatch",
  "tooltipFormatter",
  "labelFormatter",
  "rawOptionPatch"
];

for (const id of requiredDrawerIds) {
  assert(drawers.includes(`"${id}"`), `Required drawer id missing: ${id}`, failures);
}

for (const token of [
  "export type CodeDrawerId",
  "export type CodeDrawerKind",
  "export type CodeDrawerState",
  "export type ChartCodeDrawerRecipe",
  "export function getDefaultCodeDrawers",
  "export function validateCodeDrawer",
  "export function applyCodeDrawersToOption",
  "export function safeDeepMergeOption"
]) {
  assert(drawers.includes(token), `Missing code drawer export token: ${token}`, failures);
}

assert(shell.includes('"code"') && deck.includes("Code"), "Code tab exists", failures);
for (const tab of ["visual", "motion", "interaction", "labels", "data", "advanced"]) {
  assert(shell.includes(`"${tab}"`) && deck.includes(tab), `Existing Power Studio tab removed or missing: ${tab}`, failures);
}
assert(types.includes('"code"'), "PowerStudioTab/code type path is present", failures);

assert(pipeline.includes("applyCodeDrawersToOption"), "Pipeline applies code drawers", failures);
assert(pipeline.indexOf("applyCodeDrawersToOption") < pipeline.indexOf("applyChartLabVisibilityGuard(finalOption"), "Code drawers apply before final visibility guard", failures);
assert(drawers.includes("Invalid JSON") && drawers.includes("continue;"), "Invalid JSON does not apply", failures);
assert(drawers.includes('"rawOptionPatch"') && drawers.includes("rawOptionPatch") && drawers.includes("validateCodeDrawer"), "rawOptionPatch exists but is guarded", failures);
assert(drawers.includes('"tooltipFormatter"') && drawers.includes('"labelFormatter"') && drawers.includes("enabled: false"), "formatter drawers are disabled by default", failures);

assert(!drawers.includes("Math.random") && !shell.includes("Math.random"), "No Math.random in Code Drawers or shell runtime path", failures);
assert(!shell.includes("useState(() => readJson") && !shell.includes("initialSearchParam"), "No localStorage/window read during initial render", failures);
assert(shell.includes("setHydrated(true)") && shell.includes("if (!hydrated) return;"), "Drawer persistence is gated until after hydration", failures);

for (const token of [
  "Apply drawer",
  "Disable",
  "Reset",
  "Copy",
  "Copy final ECharts option",
  "Show final option diff",
  "Last known good option fallback"
]) {
  assert(shell.includes(token), `Missing Code drawer UI token: ${token}`, failures);
}

report("chart-lab-code-drawers-contract", failures);
