import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const fail = (message) => {
  console.error(`[PRISMA Chart Atlas] FAIL: ${message}`);
  process.exitCode = 1;
};
const pass = (message) => console.log(`[PRISMA Chart Atlas] PASS: ${message}`);

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

function walk(dir, acc = []) {
  const absolute = path.join(root, dir);
  if (!fs.existsSync(absolute)) return acc;
  for (const entry of fs.readdirSync(absolute, { withFileTypes: true })) {
    const relative = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (["node_modules", ".next", "dist", "build", "coverage"].includes(entry.name)) continue;
      walk(relative, acc);
    }
    else acc.push(relative.replaceAll("\\", "/"));
  }
  return acc;
}

function field(source, name) {
  const match = source.match(new RegExp(`${name}:\\s*"([^"]+)"`));
  return match?.[1] ?? null;
}

function arrayFieldCount(source, name) {
  const match = source.match(new RegExp(`${name}:\\s*\\[([\\s\\S]*?)\\]`));
  if (!match) return 0;
  return [...match[1].matchAll(/"[^"]+"/g)].length;
}

const expectedChartIds = [
  "pc.causal-flow-ribbon",
  "pc.operational-density-field",
  "pc.service-dependency-graph",
  "pc.inventory-risk-treemap",
  "pc.decision-ledger-timeline",
  "pc.financial-operational-waterfall",
  "tablet.shift-pulse-strip",
  "tablet.sync-outbox-status-matrix",
  "mobile.owner-pulse-timeline",
  "mobile.action-inbox-priority-stack",
  "mobile.health-radar-compact",
  "mobile.freshness-beacon-grid",
  "mobile.incident-spark-cards",
  "mobile.confidence-meter-bands"
];

const requiredFiles = [
  "shared/prisma-charts/prismaChartAtlas.ts",
  "shared/prisma-charts/prismaChartTokens.ts",
  "shared/prisma-charts/prismaChartIntentDictionary.ts",
  "shared/prisma-charts/state-gallery/prismaChartStates.ts",
  "products/pc/app/app/prisma-insights/chart-lab/page.tsx",
  "docs/prisma/PRISMA_CHART_ATLAS.md",
  "docs/prisma/PRISMA_CHARTOPS_LAYER_V01.md",
  "docs/prisma/PRISMA_CHART_CREATION_KIT.md",
  "docs/prisma/PRISMA_CHARTS_BASELINE_BEFORE_WIRING.md",
  "docs/prisma/PRISMA_CHART_REAL_DATA_SOURCE_MAP.md"
];

for (const file of requiredFiles) {
  if (exists(file)) pass(`required file exists: ${file}`);
  else fail(`missing required file: ${file}`);
}

const passportFiles = walk("shared/prisma-charts/passports").filter((file) => file.endsWith(".passport.ts"));
if (passportFiles.length === 14) pass("14 passport files exist");
else fail(`expected 14 passport files, found ${passportFiles.length}`);

const passports = passportFiles.map((file) => ({ file, source: read(file) }));
const chartIds = passports.map((passport) => field(passport.source, "chartId")).filter(Boolean);
const duplicateIds = chartIds.filter((id, index) => chartIds.indexOf(id) !== index);
if (new Set(chartIds).size === chartIds.length) pass("chartId values are unique");
else fail(`duplicate chartId values: ${Array.from(new Set(duplicateIds)).join(", ")}`);

for (const expected of expectedChartIds) {
  if (chartIds.includes(expected)) pass(`passport exists for ${expected}`);
  else fail(`missing passport for ${expected}`);
}

const atlasSource = read("shared/prisma-charts/prismaChartAtlas.ts");
for (const expected of expectedChartIds) {
  if (atlasSource.includes(expected)) pass(`atlas references ${expected}`);
  else fail(`atlas does not reference ${expected}`);
}

const optionsSource = read("shared/prisma-charts/prismaChartOptions.ts");
const contractsSource = read("shared/prisma-charts/prismaChartContracts.ts");
const adaptersSource = read("shared/prisma-charts/prismaChartAdapters.ts");

for (const passport of passports) {
  const componentFile = field(passport.source, "componentFile");
  const optionBuilderName = field(passport.source, "optionBuilderName");
  const contractType = field(passport.source, "contractType");
  const adapterName = field(passport.source, "adapterName");
  const status = field(passport.source, "status");
  const visualRecipe = field(passport.source, "visualRecipe");
  if (componentFile && exists(componentFile)) pass(`component exists: ${componentFile}`);
  else fail(`component missing for ${passport.file}: ${componentFile}`);
  if (optionBuilderName && optionsSource.includes(`function ${optionBuilderName}`)) pass(`option builder exists: ${optionBuilderName}`);
  else fail(`option builder missing for ${passport.file}: ${optionBuilderName}`);
  const contractTokens = [...(contractType ?? "").matchAll(/[A-Z][A-Za-z0-9]+/g)].map((match) => match[0]);
  if (contractTokens.length && contractTokens.every((token) => contractsSource.includes(token))) pass(`contract referenced: ${contractType}`);
  else fail(`contract not referenced for ${passport.file}: ${contractType}`);
  if (adapterName && adaptersSource.includes(`function ${adapterName}`)) pass(`adapter exists: ${adapterName}`);
  else if (status === "preview_mock" && passport.source.includes("knownRisks")) pass(`adapter explicitly mock/unavailable: ${passport.file}`);
  else fail(`adapter missing for ${passport.file}: ${adapterName}`);
  if (visualRecipe && exists(`shared/prisma-charts/recipes/${visualRecipe}.ts`)) pass(`recipe exists: ${visualRecipe}`);
  else fail(`recipe missing for ${passport.file}: ${visualRecipe}`);
  if (arrayFieldCount(passport.source, "visualKnobs") > 0 || passport.source.includes("knob(")) pass(`visual knobs declared: ${passport.file}`);
  else fail(`visualKnobs missing: ${passport.file}`);
  if (passport.source.includes("states: supportedStates")) pass(`states declared: ${passport.file}`);
  else fail(`states missing: ${passport.file}`);
}

const sourceMap = read("docs/prisma/PRISMA_CHART_REAL_DATA_SOURCE_MAP.md");
if (/marked as real without a safe source/i.test(sourceMap)) {
  fail("source map includes a real-without-safe-source warning");
} else {
  pass("source map does not mark charts real without safe source warning");
}

const appTsconfigs = [
  "products/pc/app/tsconfig.json",
  "products/tablet/app/tsconfig.json",
  "products/mobile/app/tsconfig.json"
];
const reactTypeAliasHits = appTsconfigs.filter((file) => read(file).includes("node_modules/@types/react"));
if (reactTypeAliasHits.length === 0) pass("React runtime aliases do not point at @types/react");
else fail(`React runtime aliases point at @types/react: ${reactTypeAliasHits.join(", ")}`);
const reactPathAliasHits = appTsconfigs.filter((file) => {
  const tsconfig = JSON.parse(read(file));
  const paths = tsconfig.compilerOptions?.paths ?? {};
  return "react" in paths || "react/jsx-runtime" in paths || "react/jsx-dev-runtime" in paths;
});
if (reactPathAliasHits.length === 0) pass("React and JSX runtime are not tsconfig-aliased");
else fail(`React runtime must not be aliased in tsconfig paths: ${reactPathAliasHits.join(", ")}`);

const checkedFiles = walk("products").concat(walk("shared"), walk("tools")).filter((file) => /\.(ts|tsx|mjs|js)$/.test(file));
const directEchartsImports = checkedFiles
  .filter((file) => !file.startsWith("shared/prisma-charts/"))
  .filter((file) => /from\s+["']echarts|import\(["']echarts/.test(read(file)));
if (directEchartsImports.length === 0) pass("no direct ECharts imports outside shared/prisma-charts");
else fail(`direct ECharts imports outside shared/prisma-charts: ${directEchartsImports.join(", ")}`);

const registry = read("shared/prisma-charts/prismaChartRegistry.ts");
const registryIds = [...registry.matchAll(/id:\s*"([^"]+)"/g)].map((match) => match[1]).filter((id) => id.startsWith("pc.") || id.startsWith("tablet.") || id.startsWith("mobile."));
const registryMissing = expectedChartIds.filter((id) => !registryIds.includes(id));
if (registryMissing.length === 0 && registryIds.length === 14) pass("registry and atlas chart ids align");
else fail(`registry mismatch. missing=${registryMissing.join(", ")} count=${registryIds.length}`);

if (!process.exitCode) pass("verification complete");
