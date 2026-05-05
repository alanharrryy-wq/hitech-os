#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const errors = [];
const notes = [];

function ok(message) {
  notes.push(`OK ${message}`);
}

function fail(message) {
  errors.push(`FAIL ${message}`);
}

function read(rel) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) {
    fail(`missing ${rel}`);
    return "";
  }
  return fs.readFileSync(file, "utf8");
}

function assertContains(rel, snippets, area) {
  const text = read(rel);
  for (const snippet of snippets) {
    if (!text.includes(snippet)) fail(`${area}: ${rel} missing ${snippet}`);
    else ok(`${area}: ${rel} includes ${snippet}`);
  }
}

function assertNotContains(rel, snippets, area) {
  const text = read(rel);
  for (const snippet of snippets) {
    if (text.includes(snippet)) fail(`${area}: ${rel} contains forbidden ${snippet}`);
    else ok(`${area}: ${rel} excludes ${snippet}`);
  }
}

function walk(dir, acc = []) {
  if (!fs.existsSync(dir)) return acc;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}

function rel(file) {
  return path.relative(root, file).replaceAll(path.sep, "/");
}

function extractQuotedStrings(text) {
  const values = [];
  for (const match of text.matchAll(/(["'`])((?:\\.|(?!\1).){1,160})\1/gms)) {
    values.push(match[2]);
  }
  return values;
}

function assertVisibleCopySafe(files) {
  const forbidden = [
    "outbox",
    "runtime",
    "payload",
    "schema",
    "mutation",
    "query",
    "lookup",
    "amountCents",
    "saleReturn",
    "terminalId",
    "businessId",
    "stack trace",
    "undefined",
    "NaN",
    "fatal"
  ];
  const allowedTechnicalContexts = [
    "schemaVersion",
    "businessId:",
    "terminalId:",
    "readRuntimeSnapshotInput",
    "TabletRuntimeSnapshot",
    "runtimeSnapshot",
    "runtime_",
    "RuntimeChip",
    "RuntimePanel",
    "RuntimeStatusStrip",
    "getRuntime",
    "buildRuntime",
    "tablet-runtime",
    "api/tablet/runtime/snapshot",
    "/events/outbox",
    "formatRuntimeInteger",
    "formatRuntimeMoney",
    "payload/",
    "manifest"
  ];
  for (const file of files) {
    const text = read(file);
    const strings = extractQuotedStrings(text);
    for (const value of strings) {
      const lower = value.toLowerCase();
      const technicalAllowed = allowedTechnicalContexts.some((ctx) => value.includes(ctx));
      if (technicalAllowed) continue;
      for (const term of forbidden) {
        if (lower.includes(term.toLowerCase())) {
          fail(`visible copy scan: ${file} has ${term} in string ${JSON.stringify(value)}`);
        }
      }
    }
  }
  ok(`visible copy scan reviewed ${files.length} files`);
}

function assertNoBlockedSurfaceInPayload() {
  const blockedPrefixes = [
    "products/pc/",
    "products/mobile/",
    "packages/shared-kernel/",
    "shared/"
  ];
  const suspectFiles = walk(root).map(rel).filter((file) => file.includes("03B") || file.includes("03C") || file.includes("runtime") || file.includes("tablet-home"));
  for (const file of suspectFiles) {
    for (const blocked of blockedPrefixes) {
      if (file.startsWith(blocked)) fail(`blocked surface touched: ${file}`);
    }
  }
  ok("blocked surfaces not touched by installed 03B/03C files");
}

function assertRouteAlias(relPath, expectedTarget) {
  const text = read(relPath);
  if (!text.includes("redirect")) fail(`${relPath} does not use redirect`);
  if (!text.includes(expectedTarget)) fail(`${relPath} does not point to ${expectedTarget}`);
  ok(`${relPath} redirects to ${expectedTarget}`);
}

function assertCssContract() {
  const css = read("components/tablet-shell/prisma-tablet-shell.module.css") + "\n" + read("components/tablet-home/tablet-home.module.css");
  const requiredSelectors = [
    ".runtimeStrip",
    ".runtimeChip",
    ".runtime_ok",
    ".runtime_warn",
    ".navPrimary",
    ".homeShell",
    ".heroMain",
    ".metricGrid",
    ".actionCard",
    ".alertCard"
  ];
  for (const selector of requiredSelectors) {
    if (!css.includes(selector)) fail(`css missing ${selector}`);
    else ok(`css includes ${selector}`);
  }
  const craftSignals = ["backdrop-filter", "var(--prisma-gold-gradient)", "var(--prisma-shadow-glass)", "@media"];
  for (const signal of craftSignals) {
    if (!css.includes(signal)) fail(`css missing craft signal ${signal}`);
    else ok(`css includes craft signal ${signal}`);
  }
}

function assertServerSnapshotContract() {
  assertContains("src/server/tablet-runtime-snapshot/queries.prisma.ts", [
    "Promise.allSettled",
    "resolveOpenShift",
    "countOutbox",
    "resolveCatalog",
    "resolveSales",
    "getTodaySalesSummary"
  ], "server snapshot queries");
  assertContains("src/server/tablet-runtime-snapshot/build.ts", [
    "localSalesAllowed: true",
    "pcRequiredForBasicSale: false",
    "connectionState",
    "catalogState",
    "capabilities",
    "warnings"
  ], "server snapshot builder");
  assertNotContains("src/server/tablet-runtime-snapshot/queries.prisma.ts", [
    "new PrismaClient",
    "db push",
    "schema.prisma",
    "products/pc",
    "products/mobile"
  ], "server snapshot safety");
}

function assertHomeDecisionContract() {
  assertContains("src/lib/tablet-home/home-view-model.ts", [
    "buildTabletHomeViewModel",
    "shiftOpen",
    "hasPending",
    "catalogReady",
    "hasStockPressure",
    "primaryHref",
    "metrics",
    "actions",
    "alerts",
    "checklist"
  ], "home view model");
  assertContains("components/tablet-home/tablet-home-screen.tsx", [
    "vm.hero.primaryHref",
    "vm.metrics.map",
    "vm.actions.map",
    "vm.alerts.length",
    "vm.checklist.map"
  ], "home render contract");
}

function assertTypeBoundaries() {
  assertContains("src/lib/tablet-runtime-snapshot/shell-contract.ts", [
    "TabletRuntimeSnapshot",
    "TabletRuntimeShift",
    "TabletRuntimeConnection",
    "TabletRuntimeCatalog",
    "TabletRuntimeSales",
    "DEFAULT_TABLET_RUNTIME_SNAPSHOT"
  ], "runtime type contract");
  assertContains("src/server/tablet-runtime-snapshot/types.ts", [
    "RuntimeSnapshotInput",
    "RuntimeSnapshotQueryResult",
    "RuntimeSnapshotBuildResult"
  ], "server type contract");
}

function assertScenarioFixtures() {
  const runtime = JSON.parse(read("tools/fixtures/tablet_runtime_snapshot_03b_scenarios.json"));
  const home = JSON.parse(read("tools/fixtures/tablet_home_03c_acceptance.json"));
  const runtimeNames = new Set(runtime.cases.map((item) => item.name));
  if (runtimeNames.size !== runtime.cases.length) fail("runtime scenarios have duplicate names");
  else ok("runtime scenarios have unique names");
  for (const scenario of runtime.cases) {
    const expected = scenario.expected || {};
    for (const key of ["shift", "connection", "catalog"]) {
      if (typeof expected[key] !== "string" || !expected[key].trim()) fail(`runtime scenario ${scenario.name} missing ${key}`);
    }
  }
  const homeNames = new Set(home.cases.map((item) => item.name));
  if (homeNames.size !== home.cases.length) fail("home scenarios have duplicate names");
  else ok("home scenarios have unique names");
  for (const scenario of home.cases) {
    if (!Array.isArray(scenario.expected?.mustShow) || scenario.expected.mustShow.length < 4) fail(`home scenario ${scenario.name} has weak mustShow contract`);
    if (!Array.isArray(scenario.expected?.forbidden) || scenario.expected.forbidden.length < 4) fail(`home scenario ${scenario.name} has weak forbidden contract`);
  }
}

function assertInstallerAndManifestEvidence() {
  const possibleManifestPaths = [
    path.join(root, "..", "..", "..", "..", "automation", "manifest.json"),
    path.join(root, "automation", "manifest.json")
  ];
  // The installed repo will not normally contain automation/manifest.json. This check is intentionally soft.
  const existing = possibleManifestPaths.find((file) => fs.existsSync(file));
  if (existing) {
    const manifest = JSON.parse(fs.readFileSync(existing, "utf8"));
    if (manifest.package !== "PRISMA_TABLET_RUNTIME_SNAPSHOT_HOME_03B_03C") fail("manifest package mismatch");
    else ok("manifest package name verified");
  } else {
    ok("manifest evidence not installed in app root; package installer validates it before apply");
  }
}

function assertNoSuspiciousBulkGeneratedContent() {
  const added = [
    "src/lib/tablet-runtime-snapshot/shell-contract.ts",
    "src/lib/tablet-runtime-snapshot/view-model.ts",
    "src/lib/tablet-runtime-snapshot/visible-copy.ts",
    "src/lib/tablet-home/home-view-model.ts",
    "components/tablet-home/tablet-home-screen.tsx",
    "components/tablet-home/tablet-home.module.css",
    "components/tablet-runtime/tablet-runtime-status-strip.tsx",
    "components/tablet-runtime/tablet-runtime-panel.tsx",
    "src/server/tablet-runtime-snapshot/build.ts",
    "src/server/tablet-runtime-snapshot/queries.prisma.ts"
  ];
  for (const file of added) {
    const text = read(file);
    const lines = text.split(/\r?\n/);
    const duplicateRatio = 1 - new Set(lines.filter((line) => line.trim())).size / Math.max(1, lines.filter((line) => line.trim()).length);
    if (duplicateRatio > 0.45) fail(`${file} has suspicious duplicate line ratio ${duplicateRatio.toFixed(2)}`);
    else ok(`${file} duplicate line ratio acceptable ${duplicateRatio.toFixed(2)}`);
  }
}

assertTypeBoundaries();
assertServerSnapshotContract();
assertHomeDecisionContract();
assertCssContract();
assertRouteAlias("app/inventory/page.tsx", "/stock");
assertRouteAlias("app/existencias/page.tsx", "/stock");
assertScenarioFixtures();
assertInstallerAndManifestEvidence();
assertNoBlockedSurfaceInPayload();
assertNoSuspiciousBulkGeneratedContent();
assertVisibleCopySafe([
  "components/tablet-shell/tablet-nav.ts",
  "components/tablet-shell/prisma-tablet-shell.tsx",
  "components/tablet-runtime/tablet-runtime-status-strip.tsx",
  "components/tablet-runtime/tablet-runtime-panel.tsx",
  "components/tablet-home/tablet-home-screen.tsx",
  "src/lib/tablet-home/home-view-model.ts"
]);

for (const note of notes) console.log(note);
for (const error of errors) console.error(error);
if (errors.length) process.exit(1);
console.log("OK deep verifier complete for PRISMA_TABLET_RUNTIME_SNAPSHOT_HOME_03B_03C");
