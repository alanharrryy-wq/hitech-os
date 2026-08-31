#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const verifier = "PRISMA_MOBILE_INTERFACE_CANON_V1";
const compatArg = process.argv.find((arg) => arg.startsWith("--compat="));
const compatibilityAlias = compatArg ? compatArg.slice("--compat=".length) : null;

function fail(message, details = {}) {
  console.error(JSON.stringify({ ok: false, verifier, compatibilityAlias, message, details }, null, 2));
  process.exit(1);
}

function read(relativePath) {
  const file = join(root, relativePath);
  if (!existsSync(file)) fail(`Missing required file: ${relativePath}`);
  return readFileSync(file, "utf8");
}

function requireFile(relativePath) {
  const file = join(root, relativePath);
  if (!existsSync(file)) fail(`Missing required file: ${relativePath}`);
}

function same(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

const canonPath = "docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.md";
const contractPath = "docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.contract.json";
const dashboardPath = "src/components/prisma-app/PrismaMobileDashboard.tsx";
const navigatorPath = "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx";
const retiredMultiContextSpec = "docs/prisma-app/PRISMA_APP_MOBILE_41_MULTI_CONTEXT_SWITCHER_RENDER_GRADE.md";
const historicalMultiContextArchive = "docs/prisma-app/archive/interface-history/PRISMA_APP_MOBILE_41_MULTI_CONTEXT_SWITCHER_RENDER_GRADE.md";

const canon = read(canonPath);
const contract = JSON.parse(read(contractPath));
const dashboard = read(dashboardPath);
const navigator = read(navigatorPath);
const pkg = JSON.parse(read("package.json"));

if (compatibilityAlias === "multi-context-switcher") {
  fail("The MultiContextSwitcher compatibility alias is retired and must not be used as current Mobile product authority");
}

if (contract.schemaVersion !== "prisma.mobile.interface-canon.v1") fail("Unexpected canon contract schemaVersion", { schemaVersion: contract.schemaVersion });
if (contract.authorityId !== "mobile.interface_specification_canon") fail("Unexpected canon authorityId", { authorityId: contract.authorityId });
if (contract.authorityState !== "SOURCE_READY") fail("Canon authorityState must reflect the Factory Ledger SOURCE_READY state", { authorityState: contract.authorityState });
if (contract.normativeDocument !== canonPath) fail("Contract normativeDocument drifted", { normativeDocument: contract.normativeDocument });
if (contract.primarySurface?.route !== "/prisma-app") fail("Primary Mobile route must stay /prisma-app");
if (contract.primarySurface?.shellOwner !== dashboardPath) fail("Dashboard owner drifted");
if (contract.primarySurface?.navigationOwner !== navigatorPath) fail("Premium Navigator owner drifted");

const expectedNavigation = [
  { id: "inicio", label: "Inicio" },
  { id: "ventas", label: "Ventas" },
  { id: "operacion", label: "Operación" },
  { id: "licencias", label: "Licencias" },
  { id: "alertas", label: "Alertas" },
  { id: "stock", label: "Stock" },
  { id: "sistema", label: "Sistema" }
];

if (!same(contract.primarySurface?.orderedNavigation, expectedNavigation)) {
  fail("Canonical orderedNavigation is not the exact seven-section contract", { actual: contract.primarySurface?.orderedNavigation, expectedNavigation });
}

if (!canon.includes("The top-level Mobile navigation is exactly seven sections")) fail("Normative canon no longer declares the seven-section primary IA");
if (!canon.includes("No component is to be re-mounted solely to satisfy an obsolete iteration document.")) fail("Normative no-remount boundary is missing");
if (!canon.includes("PRISMA Mobile defines **no global context switcher**")) fail("Normative product-simplification boundary is missing");
if (!canon.includes("separate governed product decision from zero")) fail("Future multisucursal must remain a separate product decision");

if (!dashboard.includes("PrismaMobilePremiumNavigator")) fail("Dashboard must delegate primary IA to PrismaMobilePremiumNavigator");
if (!dashboard.includes("<PrismaMobilePremiumNavigator")) fail("Dashboard must mount PrismaMobilePremiumNavigator");

const tabOrderMatch = navigator.match(/const\s+TAB_ORDER\s*:\s*PremiumTabId\[\]\s*=\s*\[([\s\S]*?)\];/);
if (!tabOrderMatch) fail("Could not parse Premium Navigator TAB_ORDER");
const actualTabIds = Array.from(tabOrderMatch[1].matchAll(/"([^"]+)"/g)).map((match) => match[1]);
const expectedTabIds = expectedNavigation.map((item) => item.id);
if (!same(actualTabIds, expectedTabIds)) fail("Premium Navigator TAB_ORDER does not match canon", { actualTabIds, expectedTabIds });

for (const item of expectedNavigation) {
  const labelPattern = new RegExp(`id:\\s*"${item.id}"\\s+as\\s+const,\\s*label:\\s*"${item.label}"`);
  if (!labelPattern.test(navigator)) fail("Premium Navigator label does not match canon", item);
}

const expectedDormant = [
  ["command-center", "PrismaMobileCommandCenter"],
  ["action-inbox", "PrismaMobileActionInbox"],
  ["daily-brief", "PrismaMobileDailyBrief"],
  ["decision-ledger", "PrismaMobileDecisionLedger"],
  ["pulse-timeline", "PrismaMobilePulseTimeline"],
  ["health-radar", "PrismaMobileHealthRadar"]
];

const dormantRows = contract.secondaryOrDormantCapabilities ?? [];
for (const [id, component] of expectedDormant) {
  const row = dormantRows.find((candidate) => candidate.id === id && candidate.component === component);
  if (!row) fail("Dormant capability missing from canon contract", { id, component });
  if (row.mountRequiredByCanon !== false) fail("Dormant capability cannot be mandatory-mounted", { id, component, mountRequiredByCanon: row.mountRequiredByCanon });
  requireFile(`src/components/prisma-app/${component}.tsx`);
  if (dashboard.includes(`<${component}`)) fail("Historical capability was re-mounted in Dashboard", { id, component });
  if (navigator.includes(`<${component}`)) fail("Historical capability was re-mounted in Premium Navigator", { id, component });
}

if (dormantRows.some((row) => row.id === "multi-context-switcher" || row.component === "PrismaMobileMultiContextSwitcher")) {
  fail("Retired MultiContextSwitcher leaked back into the normative dormant-capability contract");
}

const simplification = contract.productSimplification ?? {};
for (const key of [
  "globalContextSwitcherDefinedByCanon",
  "branchSelectorDefinedByCanon",
  "sourceSelectorDefinedByCanon",
  "readinessSelectorDefinedByCanon",
  "allBranchesOptionDefinedByCanon",
  "automaticReplacementDefinedByCanon"
]) {
  if (simplification[key] !== false) fail("Product simplification guard must remain false", { key, value: simplification[key] });
}
if (simplification.futureMultiBranchUxRequiresSeparateGovernedDecision !== true) {
  fail("Future multi-branch UX must require a separate governed product decision");
}

if (existsSync(join(root, retiredMultiContextSpec))) fail("Retired active iteration-41 MultiContext spec must not exist");
requireFile(historicalMultiContextArchive);

const capabilityEvidence = [
  ["command-center", "src/lib/prisma-app/prisma-mobile-command-center.ts", "app/api/mobile/command-center/route.ts"],
  ["action-inbox", "src/lib/prisma-app/prisma-mobile-action-inbox.ts", "app/api/mobile/action-inbox/route.ts"],
  ["daily-brief", "src/lib/prisma-app/prisma-mobile-daily-brief.ts", "app/api/mobile/daily-brief/route.ts"],
  ["decision-ledger", "src/lib/prisma-app/prisma-mobile-decision-ledger.ts", "app/api/mobile/decision-ledger/route.ts"],
  ["pulse-timeline", "src/lib/prisma-app/prisma-mobile-pulse-timeline.ts", "app/api/mobile/pulse-timeline/route.ts"],
  ["health-radar", "src/lib/prisma-app/prisma-mobile-health-radar.ts", "app/api/mobile/health-radar/route.ts"]
];
for (const [id, lib, route] of capabilityEvidence) {
  requireFile(lib);
  requireFile(route);
  if (!dormantRows.some((row) => row.id === id)) fail("Capability evidence has no dormant canon row", { id });
}

const expectedAuxiliaryRoutes = [
  ["/prisma-app/setup", "app/prisma-app/setup/page.tsx"],
  ["/prisma-app/install", "app/prisma-app/install/page.tsx"],
  ["/prisma-app/offline", "app/prisma-app/offline/page.tsx"]
];
for (const [route, file] of expectedAuxiliaryRoutes) {
  const row = (contract.auxiliaryRoutes ?? []).find((candidate) => candidate.route === route);
  if (!row || row.primaryNav !== false) fail("Auxiliary route contract drifted", { route, row });
  requireFile(file);
}

const commandRoute = (contract.separateRoutes ?? []).find((row) => row.route === "/prisma-command");
if (!commandRoute || commandRoute.primaryNav !== false) fail("/prisma-command must remain separate from primary navigation");
requireFile("app/prisma-command/page.tsx");

const retired = new Set(contract.retiredPrimaryNavigationConcepts ?? []);
for (const item of expectedNavigation) {
  if (retired.has(item.label)) fail("Current canonical label is also marked retired", item);
}

const noFakeGreen = contract.noFakeGreen ?? {};
for (const key of ["staleOrPartialIsHealthy", "componentExistsMeansMounted", "historicalVerifierMeansCurrentAuthority", "offlineRouteMeansOfflineDataCertified"]) {
  if (noFakeGreen[key] !== false) fail("No-fake-green contract must stay false", { key, value: noFakeGreen[key] });
}

if (contract.claims?.verifiersAligned !== true) fail("Canon claims.verifiersAligned must stay true after verifier reconciliation", { verifiersAligned: contract.claims?.verifiersAligned });

const canonicalCommand = "node tools/verify_prisma_mobile_interface_canon.mjs";
if (pkg.scripts?.["verify:interface-canon"] !== canonicalCommand) fail("package.json must register verify:interface-canon", { actual: pkg.scripts?.["verify:interface-canon"] });

const compatibilityScripts = {
  "verify:command-center": "command-center",
  "verify:action-inbox": "action-inbox",
  "verify:daily-brief": "daily-brief",
  "verify:decision-ledger": "decision-ledger",
  "verify:pulse-timeline": "pulse-timeline",
  "verify:mando": "mando",
  "verify:release-hardening": "release-hardening"
};
for (const [script, alias] of Object.entries(compatibilityScripts)) {
  const expected = `${canonicalCommand} --compat=${alias}`;
  if (pkg.scripts?.[script] !== expected) fail("Historical verifier script must delegate to the canon", { script, expected, actual: pkg.scripts?.[script] });
}

if (pkg.scripts?.["verify:multi-context-switcher"] !== undefined) fail("Retired MultiContext verifier alias must not exist in package.json");
for (const key of ["prismaMobileMultiContextSwitcherVersion", "prismaMobileMultiContextSwitcherPackage"]) {
  if (Object.prototype.hasOwnProperty.call(pkg, key)) fail("Retired MultiContext package metadata must not exist", { key });
}

const checkAll = String(pkg.scripts?.["check:all"] ?? "");
if (!checkAll.includes("verify:interface-canon")) fail("check:all must execute verify:interface-canon");
for (const script of Object.keys(compatibilityScripts)) {
  if (checkAll.includes(script)) fail("check:all must not repeatedly execute historical compatibility aliases", { script });
}
if (checkAll.includes("multi-context")) fail("check:all must not retain retired MultiContext terminology");

for (const technicalScript of [
  "verify:secure-projection-gateway",
  "verify:crystal-intelligence",
  "verify:premium-navigation",
  "verify:data-readiness",
  "verify:health-radar",
  "verify:health-radar-compat",
  "verify:data-plane-types",
  "verify:runtime-error-guard",
  "verify:source-states",
  "verify:pwa",
  "verify:playstore-readiness"
]) {
  if (!checkAll.includes(technicalScript)) fail("Technical gate disappeared from check:all", { technicalScript });
}

console.log(JSON.stringify({
  ok: true,
  verifier,
  compatibilityAlias,
  authorityId: contract.authorityId,
  primaryRoute: contract.primarySurface.route,
  navigation: expectedNavigation,
  dormantCapabilities: expectedDormant.map(([id]) => id),
  productSimplification: simplification,
  auxiliaryRoutes: expectedAuxiliaryRoutes.map(([route]) => route),
  separateRoutes: ["/prisma-command"],
  claimVerifiersAlignedInCanon: contract.claims?.verifiersAligned ?? null,
  message: compatibilityAlias
    ? `Historical verifier alias '${compatibilityAlias}' now defers to the Mobile interface canon.`
    : "PRISMA Mobile interface canon verifier passed."
}, null, 2));
