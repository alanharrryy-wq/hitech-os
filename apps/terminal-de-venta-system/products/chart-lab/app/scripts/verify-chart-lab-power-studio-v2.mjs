// PRISMA_CHART_LAB_POWER_STUDIO_VERIFIER_V2
// Static verifier for Single Chart Workbench + ECharts Power Studio.
// It intentionally checks product decisions, migration inventory, ECharts safety hooks,
// and “no ghost control” guarantees before the slower build/typecheck phase.
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
    const detail = fn();
    checks.push({ name, status: "PASS", detail: detail || "" });
  } catch (error) {
    checks.push({ name, status: "FAIL", message: error instanceof Error ? error.message : String(error) });
  }
}

function requireTokens(name, source, tokens) {
  const missing = tokens.filter((token) => !source.includes(token));
  if (missing.length) throw new Error(`${name} missing token(s): ${missing.join(", ")}`);
  return `${tokens.length} token(s) present.`;
}

function extractControlIds(model) {
  const ids = new Set();
  const re = /id:\s*["']([^"']+)["']/g;
  let match;
  while ((match = re.exec(model))) ids.add(match[1]);
  return [...ids].sort();
}

const shell = read("src/components/PrismaChartLabShell.tsx");
const deck = read("src/components/ChartControlDeck.tsx");
const frame = read("src/prisma-charts/components/LabEChartFrame.tsx");
const model = read("src/prisma-charts/chart-lab-control-model.ts");
const types = read("src/prisma-charts/chart-lab-types.ts");
const css = read("app/globals.css");

const controlIds = extractControlIds(model);

check("01 single chart workbench shell marker", () =>
  requireTokens("shell", shell, ["SINGLE_CHART_WORKBENCH_POWER_STUDIO"])
);

check("02 one obvious current chart dropdown", () =>
  requireTokens("shell", shell, ["data-testid=\"single-chart-dropdown\"", "selectedChart", "selectChart"])
);

check("03 1080p three-pane layout exists", () =>
  requireTokens("shell/css", shell + css, ["studio-left-rail", "studio-canvas", "studio-right-rail", "chart-lab-workbench"])
);

check("04 no focus mode as primary layout dependency", () => {
  for (const forbidden of ["Focus Mode", "focusMode", "data-focus-mode"] ) {
    if (shell.includes(forbidden)) throw new Error(`Forbidden focus dependency remains: ${forbidden}`);
  }
  return "focus-mode removed from shell decisions.";
});

check("05 create-new and technical metadata are collapsed", () =>
  requireTokens("shell", shell, ["Create new chart", "Technical info", "componentPath", "mockPath", "dataStatus"])
);

check("06 Power Studio side rail tabs", () =>
  requireTokens("deck/shell", deck + shell, ["visual", "motion", "interaction", "labels", "data", "advanced", "control-deck--power-studio"])
);

check("07 current controls conserved plus new ECharts power controls", () => {
  const required = [
    "dataScenario", "themePreset", "showLabels", "animation", "visualIntensity",
    "severityFilter", "confidenceFloor", "ribbonWidth", "ribbonOpacity", "detailLevel", "stageFocus", "layoutDensity", "evidenceMode",
    "contrastPunch", "glowAura", "motionPreset", "entranceDuration", "updateDuration", "staggerDelay", "easingCurve", "motionMode",
    "tooltipMode", "hoverSpotlight", "showCallouts", "heatPalette", "heatZoneMode", "hotspotBias", "showCellNumbers"
  ];
  const missing = required.filter((id) => !controlIds.includes(id));
  if (missing.length) throw new Error(`Missing required controls: ${missing.join(", ")}`);
  return `${required.length} required controls present; ${controlIds.length} total IDs discovered.`;
});

check("08 control descriptors support Power Studio grouping", () =>
  requireTokens("types/model", types + model, ["powerTab?", "powerTab: \"visual\"", "powerTab: \"motion\"", "powerTab: \"interaction\"", "powerTab: \"labels\"", "powerTab: \"data\""])
);

check("09 safe wild insane ranges are visible", () =>
  requireTokens("deck/model", deck + model, ["range-zone--${zone}", "safe", "wild", "insane", "data-control-zone"])
);

check("10 ECharts resize and lifecycle safety", () =>
  requireTokens("frame", frame, ["ResizeObserver", ".resize()", ".dispose()", "setOption", "renderer"])
);

check("11 ECharts interaction/guided tour hooks", () =>
  requireTokens("frame/model", frame + model, ["tourSignal", "dispatchAction", "showTip", "highlight", "downplay", "dataZoom", "brush", "tooltip"])
);

check("12 motion and reduced-motion safety", () =>
  requireTokens("model/frame", model + frame, ["animationDuration", "animationDurationUpdate", "animationEasing", "animationDelay", "reducedMotion", "universalTransition"])
);

check("13 recipe, variant, remix, before-after actions", () =>
  requireTokens("shell", shell, ["Copy recipe", "Copy option", "Save variant", "Before / After", "Guided tour", "Remix", "buildRecipe", "SavedVariant"])
);

check("14 target previews PC Tablet Mobile", () =>
  requireTokens("shell/types", shell + types, ["LabChartPreviewFrame", "pc", "tablet", "mobile", "target"])
);

check("15 CSS locks canvas-first layout without global scroll dependency", () =>
  requireTokens("css", css, ["height: calc(100dvh - 20px)", "grid-template-columns: minmax(230px, 270px) minmax(0, 1fr) minmax(330px, 400px)", "overflow: hidden", "min-height: 0", "min-width: 0"])
);

check("16 no package.json replacement required", () => {
  if (fs.existsSync(path.join(appRoot, "package.json"))) return "package.json exists; installer does not replace it.";
  throw new Error("package.json missing in app root");
});

const failed = checks.filter((item) => item.status !== "PASS");
for (const item of checks) {
  console.log(`${item.status}: ${item.name}${item.message ? ` - ${item.message}` : item.detail ? ` - ${item.detail}` : ""}`);
}

if (failed.length) {
  console.error(`PRISMA Chart Lab Power Studio verifier V2 failed: ${failed.length} failure(s).`);
  process.exit(1);
}

console.log(`PRISMA Chart Lab Power Studio verifier V2 passed: ${checks.length} checks.`);
