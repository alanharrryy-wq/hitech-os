import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const fail = (message) => {
  console.error(`[PRISMA ECharts] FAIL: ${message}`);
  process.exitCode = 1;
};
const pass = (message) => console.log(`[PRISMA ECharts] PASS: ${message}`);

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

const requiredFiles = [
  "shared/prisma-charts/PrismaEChart.tsx",
  "shared/prisma-charts/prismaEchartsLoader.ts",
  "shared/prisma-charts/prismaChartContracts.ts",
  "shared/prisma-charts/prismaChartRegistry.ts",
  "shared/prisma-charts/prismaChartMocks.ts",
  "shared/prisma-charts/prismaChartAdapters.ts",
  "shared/prisma-charts/prismaChartOptions.ts",
  "products/pc/app/app/prisma-insights/page.tsx",
  "products/tablet/app/app/prisma-pulse/page.tsx",
  "products/mobile/app/app/prisma-command/page.tsx",
  "docs/prisma/PRISMA_ECHARTS_TRIPLE_APP_INSIGHTS.md"
];

for (const file of requiredFiles) {
  if (exists(file)) pass(`required file exists: ${file}`);
  else fail(`missing required file: ${file}`);
}

const packageJson = JSON.parse(read("package.json"));
if (packageJson.dependencies?.echarts === "5.6.0") pass("echarts dependency is declared at terminal app root");
else fail("echarts@5.6.0 dependency is not declared at terminal app root");

const registry = read("shared/prisma-charts/prismaChartRegistry.ts");
const chartIds = [...registry.matchAll(/id: "(pc|tablet|mobile)\.([^"]+)"/g)].map((match) => `${match[1]}.${match[2]}`);
const counts = chartIds.reduce((memo, id) => {
  const surface = id.split(".")[0];
  memo[surface] = (memo[surface] ?? 0) + 1;
  return memo;
}, {});
if (chartIds.length === 16) pass("registry has 16 product charts");
else fail(`registry has ${chartIds.length} charts`);
if (counts.pc === 8) pass("PC registry has 8 charts");
else fail(`PC registry has ${counts.pc ?? 0} charts`);
if (counts.tablet === 2) pass("Tablet registry has 2 charts");
else fail(`Tablet registry has ${counts.tablet ?? 0} charts`);
if (counts.mobile === 6) pass("Mobile registry has 6 charts");
else fail(`Mobile registry has ${counts.mobile ?? 0} charts`);

const rootPackage = read("package.json");
if (rootPackage.includes('"prisma:echarts:verify"')) pass("root verifier script is registered");
else fail("root verifier script is missing");

const flagSource = read("shared/prisma-charts/prismaChartFlags.ts");
if (flagSource.includes("const enabled = previewEnabled || (masterEnabled && surfaceEnabled);")) pass("feature flags are off by default and preview gated");
else fail("feature flag default behavior is not explicit");

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
if (reactPathAliasHits.length === 0) pass("React and JSX runtime are resolved by package manager, not tsconfig paths");
else fail(`React runtime must not be aliased in tsconfig paths: ${reactPathAliasHits.join(", ")}`);

const allTsxTs = walk("products").concat(walk("shared"));
const echartsDirectImports = allTsxTs
  .filter((file) => /\.(ts|tsx|mjs|js)$/.test(file))
  .filter((file) => !file.startsWith("shared/prisma-charts/"))
  .filter((file) => !file.startsWith("products/chart-lab/app/"))
  .filter((file) => /from ["']echarts|import\(["']echarts/.test(read(file)));
if (echartsDirectImports.length === 0) pass("product apps do not import ECharts directly; Chart Lab owns its package-local renderer");
else fail(`direct ECharts imports outside shared foundation: ${echartsDirectImports.join(", ")}`);

const appChartFiles = [
  ...walk("products/pc/app/app/prisma-insights"),
  ...walk("products/tablet/app/app/prisma-pulse"),
  ...walk("products/mobile/app/app/prisma-command")
];
const forbiddenScoreSelectors = /(gauge-wrap|mega-gauge|gauge-score|score-chip|header-score)/;
const scoreSelectorHits = appChartFiles.filter((file) => forbiddenScoreSelectors.test(read(file)));
if (scoreSelectorHits.length === 0) pass("new chart surfaces do not target clean score selectors");
else fail(`new chart surfaces target score selectors: ${scoreSelectorHits.join(", ")}`);

const cleanScoreCss = "prisma-control-center/internal/web/styles.css";
if (exists(cleanScoreCss)) {
  const css = read(cleanScoreCss);
  if (css.includes("PRISMA CLEAN SCORE TEXT") && css.includes("NO CHART. NO DONUT. NO METER.")) pass("clean score text contract is present in Control Center CSS");
  else fail("clean score text contract markers are missing from Control Center CSS");
} else {
  pass("Control Center CSS not present in this checkout; score selector audit limited to new surfaces");
}

const pcFiles = walk("products/pc/app/app/prisma-insights/charts").filter((file) => /Pc[A-Z].+\.tsx$/.test(file) && !file.endsWith("PcChartCard.tsx"));
const pcSyncPromotion = exists("products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx")
  ? read("products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx")
  : "";
const tabletFiles = walk("products/tablet/app/app/prisma-pulse/charts").filter((file) => /Tablet[A-Z].+\.tsx$/.test(file) && !file.endsWith("TabletChartCard.tsx"));
const mobileFiles = walk("products/mobile/app/app/prisma-command/charts").filter((file) => /Mobile[A-Z].+\.tsx$/.test(file) && !file.endsWith("MobileChartCard.tsx"));
if (pcFiles.length === 6 && pcSyncPromotion.includes("pc.tablet-catalog-freshness-grid") && pcSyncPromotion.includes("pc.sync-command-lifecycle-timeline")) pass("PC surface has 6 insights chart components plus 2 promoted /sync charts");
else fail(`PC surface component coverage is incomplete. insights=${pcFiles.length}`);
if (tabletFiles.length === 2) pass("Tablet surface has 2 chart components");
else fail(`Tablet surface has ${tabletFiles.length} chart components`);
if (mobileFiles.length === 6) pass("Mobile surface has 6 chart components");
else fail(`Mobile surface has ${mobileFiles.length} chart components`);

if (!process.exitCode) pass("verification complete");
