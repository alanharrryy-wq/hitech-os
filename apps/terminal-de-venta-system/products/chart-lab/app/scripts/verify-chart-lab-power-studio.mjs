// PRISMA_CHART_LAB_POWER_STUDIO_VERIFIER_V1
import fs from "node:fs";
import path from "node:path";

const appRoot = path.resolve(process.cwd());
const checks = [];

function read(rel) {
  const absolute = path.join(appRoot, rel);
  if (!fs.existsSync(absolute)) throw new Error(`Missing file: ${rel}`);
  return fs.readFileSync(absolute, "utf8");
}

function check(name, fn) {
  try {
    fn();
    checks.push({ name, status: "PASS" });
  } catch (error) {
    checks.push({ name, status: "FAIL", message: error instanceof Error ? error.message : String(error) });
  }
}

const shell = read("src/components/PrismaChartLabShell.tsx");
const deck = read("src/components/ChartControlDeck.tsx");
const frame = read("src/prisma-charts/components/LabEChartFrame.tsx");
const model = read("src/prisma-charts/chart-lab-control-model.ts");
const types = read("src/prisma-charts/chart-lab-types.ts");
const css = read("app/globals.css");

check("single chart workbench shell marker", () => {
  if (!shell.includes("SINGLE_CHART_WORKBENCH_POWER_STUDIO")) throw new Error("Shell marker missing");
});

check("unique current chart dropdown exists", () => {
  if (!shell.includes('data-testid="single-chart-dropdown"')) throw new Error("Single chart dropdown test id missing");
});

check("left rail, canvas, right rail layout exists", () => {
  for (const token of ["studio-left-rail", "studio-canvas", "studio-right-rail"]) {
    if (!shell.includes(token) || !css.includes(token)) throw new Error(`${token} missing from shell/css`);
  }
});

check("power tabs exist", () => {
  for (const token of ["visual", "motion", "interaction", "labels", "data", "advanced"]) {
    if (!shell.includes(`\"${token}\"`) && !shell.includes(`>${token}<`)) throw new Error(`Power tab missing: ${token}`);
  }
});

check("controls are in Power Studio side rail", () => {
  if (!deck.includes("control-deck--power-studio")) throw new Error("Power Studio deck class missing");
  if (!deck.includes("range-zone--")) throw new Error("Range zone indicator logic missing");
});

check("wide range controls are present", () => {
  for (const token of ["visualIntensity", "contrastPunch", "glowAura", "entranceDuration", "updateDuration", "staggerDelay", "tooltipMode", "hoverSpotlight"]) {
    if (!model.includes(token)) throw new Error(`Missing Power Studio control: ${token}`);
  }
});

check("control descriptors support power tabs", () => {
  if (!types.includes("powerTab?")) throw new Error("LabChartRuntimeControl.powerTab optional field missing");
});

check("ECharts frame supports ResizeObserver and guided tour", () => {
  if (!frame.includes("ResizeObserver")) throw new Error("ResizeObserver missing");
  if (!frame.includes("tourSignal")) throw new Error("Guided tour signal missing");
  if (!frame.includes("dispatchAction({ type: \"showTip\"")) throw new Error("showTip guided action missing");
});

check("focus mode is not a primary layout dependency", () => {
  if (shell.includes("Focus Mode") || shell.includes("focusMode")) throw new Error("Old focus mode dependency still present in shell");
});

check("metadata and create new chart are collapsed", () => {
  if (!shell.includes("Create new chart") || !shell.includes("Technical info")) throw new Error("Create/technical accordions missing");
});

check("variant and recipe actions exist", () => {
  for (const token of ["Save variant", "Copy recipe", "Copy option", "Before / After", "Guided tour", "Remix"]) {
    if (!shell.includes(token)) throw new Error(`Missing action: ${token}`);
  }
});

check("CSS uses 1080p-friendly grid", () => {
  if (!css.includes("grid-template-columns: minmax(230px, 270px) minmax(0, 1fr) minmax(330px, 400px)")) throw new Error("Expected 1080p workbench grid missing");
  if (!css.includes("height: calc(100dvh - 20px)")) throw new Error("Viewport height layout missing");
});

const failed = checks.filter((item) => item.status !== "PASS");
for (const item of checks) {
  console.log(`${item.status}: ${item.name}${item.message ? ` - ${item.message}` : ""}`);
}

if (failed.length) {
  console.error(`PRISMA Chart Lab Power Studio verifier failed: ${failed.length} failure(s).`);
  process.exit(1);
}

console.log(`PRISMA Chart Lab Power Studio verifier passed: ${checks.length} checks.`);
