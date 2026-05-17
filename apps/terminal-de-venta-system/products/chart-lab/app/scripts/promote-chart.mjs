import fs from "node:fs";
import path from "node:path";
import { chartOpsIds, fail, parseArgs, pass, terminalRoot, writeEvidence } from "./chart-lab-script-utils.mjs";

const args = parseArgs();
const chartId = String(args.chart ?? "");
const target = String(args.target ?? "");
const dryRun = Boolean(args["dry-run"]);
const apply = Boolean(args.apply);
const allowedTargets = ["pc", "tablet", "mobile", "web"];

const chartIds = chartOpsIds();
if (!chartIds.includes(chartId)) fail(`Unknown chart: ${chartId}`);
if (!allowedTargets.includes(target)) fail(`Unknown target: ${target}`);
if (!dryRun && !apply) fail("Choose exactly one mode: --dry-run or --apply");
if (dryRun && apply) fail("Use only one mode: --dry-run or --apply");

const sourceSurface = chartId.split(".")[0];
const validTargets = sourceSurface === "pc" ? ["pc", "web"] : sourceSurface === "tablet" ? ["tablet", "web"] : ["mobile", "web"];
const compatible = validTargets.includes(target);
if (!compatible) fail(`Target ${target} is not compatible with ${chartId}. Valid targets: ${validTargets.join(", ")}`);

const componentStem = chartId
  .split(".")
  .map((part) => part.replace(/(^|-)([a-z])/g, (_, dash, letter) => `${dash ? "" : ""}${letter.toUpperCase()}`))
  .join("");

const plan = {
  schemaVersion: "1.0",
  generatedAt: new Date().toISOString(),
  bridgeName: "Chart Promotion Bridge",
  mode: dryRun ? "dry-run" : "apply",
  chartId,
  target,
  compatible,
  productLaw: {
    tablet: "Tablet operates and keeps local-sale autonomy.",
    pc: "PC governs and must not become POS.",
    mobile: "Mobile supervises and remains read-only.",
    core: "Core records.",
    control: "Control audits; clean score remains text-only."
  },
  sourceFiles: [
    "shared/prisma-charts/prismaChartContracts.ts",
    "shared/prisma-charts/prismaChartOptions.ts",
    "shared/prisma-charts/prismaChartAdapters.ts",
    "shared/prisma-charts/prismaChartMocks.ts",
    `shared/prisma-charts/passports/${chartId}.passport.ts`,
    "products/chart-lab/app/src/prisma-charts/chart-lab-control-model.ts"
  ],
  targetFiles:
    target === "pc"
      ? [`products/pc/app/app/prisma-insights/charts/${componentStem}.tsx`]
      : target === "tablet"
        ? [`products/tablet/app/app/prisma-charts/${componentStem}.tsx`]
        : target === "mobile"
          ? [`products/mobile/app/app/prisma-charts/${componentStem}.tsx`]
          : [`products/chart-lab/app/out/${chartId}/index.html`],
  featureFlag: `PRISMA_CHART_${chartId.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_PREVIEW=false`,
  backupRoot: "tools/_local/backups/chart-promotion",
  rollbackManifest: "tools/_local/evidence/chart-lab/promotion-rollback-manifest.json",
  validationCommands: [
    "pnpm -C products/chart-lab/app verify:promotion",
    "pnpm -C products/chart-lab/app verify:echarts-boundary",
    target === "pc" ? "pnpm -C products/pc/app typecheck" : target === "tablet" ? "pnpm -C products/tablet/app typecheck" : target === "mobile" ? "pnpm -C products/mobile/app typecheck" : "pnpm -C products/chart-lab/app verify:no-leaks"
  ],
  writePolicy: "Dry-run is fully supported. Apply is blocked until an operator approves the exact target wrapper file and feature flag path.",
  applyStatus: "BLOCKED_BY_DEFAULT_SAFE_POLICY"
};

const reportPath = writeEvidence(`promotion-${chartId.replace(/[^a-z0-9]+/gi, "-")}-${target}-${dryRun ? "dry-run" : "apply"}.json`, plan);

if (process.exitCode) {
  console.error(JSON.stringify(plan, null, 2));
  process.exit(process.exitCode);
}

if (dryRun) {
  pass(`promotion dry-run written: ${reportPath}`);
  console.log(JSON.stringify(plan, null, 2));
  process.exit(0);
}

const backupRoot = path.join(terminalRoot, "tools", "_local", "backups", "chart-promotion", new Date().toISOString().replace(/[:.]/g, "-"));
fs.mkdirSync(backupRoot, { recursive: true });
fs.writeFileSync(path.join(backupRoot, "BLOCKED_APPLY_MANIFEST.json"), JSON.stringify(plan, null, 2));
fail(`apply blocked by default safe policy; backup/rollback manifest staged at ${backupRoot}`);
